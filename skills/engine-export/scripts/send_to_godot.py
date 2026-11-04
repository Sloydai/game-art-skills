#!/usr/bin/env python3
"""Drop Sloyd models straight into the scene open in the Godot editor.

Needs the Sloyd Godot Bridge plugin (https://github.com/Sloydai/sloyd-godot-bridge) enabled in
a Godot 4.x project. The bridge listens on 127.0.0.1 and accepts
POST {"url": "<...>.glb", "name": "<node name>"}. It downloads the GLB and adds it to the
edited scene root.

    python3 send_to_godot.py --ping
    python3 send_to_godot.py https://storage.googleapis.com/ai-services-quality/jobs/JOB.glb --name Barrel
    python3 send_to_godot.py --manifest art/dungeon/manifest.json [--only dng_barrel_a,dng_chest_a] [--delay 2]

This is for fast look-dev in context. It sends the raw Sloyd GLB URL, not the normalized
export. For production, copy export/godot/ into res:// (see references/godot.md).
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time

DEFAULT_PORT = 6969  # value in sloyd-godot-bridge.gd v1.0.3 (the README mentions 4571)


def request(port: int, method: str, path: str, body: dict | None = None) -> tuple[int, str]:
    payload = json.dumps(body).encode() if body is not None else b""
    head = (f"{method} {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
            f"Content-Type: application/json\r\nContent-Length: {len(payload)}\r\nConnection: close\r\n\r\n").encode()
    # One write: the bridge reads whatever bytes are available once per request.
    with socket.create_connection(("127.0.0.1", port), timeout=10) as s:
        s.sendall(head + payload)
        chunks = []
        while True:
            try:
                c = s.recv(4096)
            except socket.timeout:
                break
            if not c:
                break
            chunks.append(c)
    raw = b"".join(chunks).decode("utf-8", "replace")
    status = int(raw.split(" ", 2)[1]) if raw.startswith("HTTP/") else 0
    return status, raw.split("\r\n\r\n", 1)[-1]


def send(port: int, url: str, name: str) -> bool:
    if not url.endswith(".glb"):
        print(f"skip {name}: bridge only accepts .glb URLs ({url})", file=sys.stderr)
        return False
    status, body = request(port, "POST", "/", {"url": url, "name": name})
    ok = status == 200
    print(f"{'sent' if ok else 'FAILED'} {name} ({status}) {body.strip()[:120]}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", nargs="?")
    ap.add_argument("--name", default="SloydModel")
    ap.add_argument("--manifest")
    ap.add_argument("--only")
    ap.add_argument("--delay", type=float, default=2.0, help="seconds between models (the bridge imports one at a time)")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--ping", action="store_true")
    args = ap.parse_args()
    try:
        status, body = request(args.port, "GET", "/ping")
    except OSError:
        print(f"No Sloyd Godot Bridge on 127.0.0.1:{args.port}. Open the project in Godot, enable "
              "Project > Project Settings > Plugins > Sloyd Godot Bridge, open a scene, then retry.", file=sys.stderr)
        return 1
    if args.ping:
        print(body)
        return 0 if status == 200 else 1
    if args.url:
        return 0 if send(args.port, args.url, args.name) else 1
    if not args.manifest:
        ap.print_help()
        return 1
    with open(args.manifest, encoding="utf-8") as fh:
        man = json.load(fh)
    only = set(args.only.split(",")) if args.only else None
    n = 0
    for a in man["assets"]:
        if only and a["id"] not in only:
            continue
        job = a.get("jobs", {}).get("model", {})
        if job.get("status") == "success" and job.get("url"):
            n += send(args.port, job["url"], a.get("name", a["id"]))
            time.sleep(args.delay)
    print(f"{n} models sent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
