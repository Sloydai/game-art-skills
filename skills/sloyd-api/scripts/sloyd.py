#!/usr/bin/env python3
"""Minimal Sloyd API client for the Game Art Department skills.

Talks to the hosted Sloyd MCP server (https://api.sloyd.ai/api/mcp) over plain
HTTP JSON-RPC, so it works from any shell even when the agent's client has no
MCP support. Standard library only.

Credentials come from the environment (or a .env file in the current folder):
    SLOYD_CLIENT_ID      sok_live_...
    SLOYD_CLIENT_SECRET  shown once when you create the key

CLI:
    python3 sloyd.py setup                      ask for the key, test it, save to .env
    python3 sloyd.py check                      credentials + balance
    python3 sloyd.py balance
    python3 sloyd.py styles
    python3 sloyd.py call TOOL '{"json":"args"}'  start a job (prints jobId)
    python3 sloyd.py wait JOB_ID                poll until done, print outputs
    python3 sloyd.py run TOOL '{"json":"args"}'   call + wait
    python3 sloyd.py download URL PATH
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

MCP_URL = os.environ.get("SLOYD_MCP_URL", "https://api.sloyd.ai/api/mcp")
PROTOCOL = "2025-11-25"
DASHBOARD = "https://api-dashboard.sloyd.ai"

# Credit prices from https://www.sloyd.ai/api/pricing (checked 2026-11-04).
# The server's 402 body ("required") is the authority; these are for estimates.
PRICES = {
    "generate_image": 10,
    "edit_image": 15,
    "retexture_model": 15,
    "split_model_into_parts": 40,
    "generate_skybox": 25,
    "generate_skybox_from_image": 25,
    "edit_skybox": 25,
    "upload_image": 0,
    "get_job": 0,
    "get_credit_balance": 0,
    "get_generation_styles": 0,
}


def estimate(tool: str, args: dict | None = None) -> int:
    """Credit estimate for one call. 3D prices depend on options."""
    args = args or {}
    if tool in PRICES:
        return PRICES[tool]
    textured_flag = args.get("textureResolution", "auto") != "none"
    quads = args.get("topology") == "quads"
    huge = int(args.get("targetFaceCount") or 0) >= 500000
    if tool == "generate_3d_from_text":
        return 10 + 5 + (10 if textured_flag else 0) + (5 if quads else 0) + (10 if huge else 0)
    if tool == "generate_3d_from_image":
        return 10 + (10 if textured_flag else 0) + (5 if quads else 0) + (10 if huge else 0)
    if tool == "generate_3d_from_images":
        textured = str(args.get("EnablePBR", "false")).lower() == "true"
        # Pricing page example: multi-image textured with quads = 40.
        return 10 + 10 + (10 if textured else 0) + 5
    return 0


class SloydError(Exception):
    def __init__(self, status: int | None, message: str, body: dict | None = None):
        super().__init__(message)
        self.status = status
        self.body = body or {}


class CreditsError(SloydError):
    """402: not enough prepaid credits. Nothing was charged."""


class BusyError(SloydError):
    """429: 5 jobs already pending/running on this key."""


class AuthError(SloydError):
    """401: missing or invalid credentials."""


def load_dotenv(path: str = ".env") -> None:
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key.startswith("SLOYD_") and val and not os.environ.get(key):
                os.environ[key] = val


def credentials() -> tuple[str, str]:
    load_dotenv()
    cid = os.environ.get("SLOYD_CLIENT_ID", "").strip()
    sec = os.environ.get("SLOYD_CLIENT_SECRET", "").strip()
    if not cid or not sec:
        raise AuthError(
            401,
            "Sloyd credentials not found. Create a key at "
            f"{DASHBOARD} (API Keys > Generate Key), then:\n"
            "  export SLOYD_CLIENT_ID=sok_live_...\n"
            "  export SLOYD_CLIENT_SECRET=...\n"
            "or put them in a .env file in this folder (never commit it).",
        )
    return cid, sec


class Sloyd:
    def __init__(self) -> None:
        self.cid, self.secret = credentials()
        self.session: str | None = None
        self._id = 0

    def _post(self, payload: dict) -> dict:
        headers = {
            "x-client-id": self.cid,
            "x-client-secret": self.secret,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": PROTOCOL,
        }
        if self.session:
            headers["mcp-session-id"] = self.session
        req = urllib.request.Request(
            MCP_URL, data=json.dumps(payload).encode(), headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=75) as resp:
                sid = resp.headers.get("mcp-session-id")
                if sid:
                    self.session = sid
                raw = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as err:
            text = err.read().decode("utf-8", "replace")
            if err.code == 401:
                raise AuthError(401, "Invalid Sloyd API credentials (401). Check SLOYD_CLIENT_ID / SLOYD_CLIENT_SECRET.")
            raise SloydError(err.code, f"HTTP {err.code}: {text[:300]}")
        for line in raw.splitlines():
            if line.startswith("data: "):
                return json.loads(line[6:])
        return json.loads(raw) if raw.strip() else {}

    def tool(self, name: str, args: dict | None = None, retries: int = 3) -> dict:
        """Call one MCP tool and return its structured result.

        Raises CreditsError (402), BusyError (429), AuthError (401), SloydError.
        Transient network/5xx errors are retried with backoff.
        """
        delay = 5.0
        for attempt in range(retries + 1):
            self._id += 1
            try:
                msg = self._post({
                    "jsonrpc": "2.0", "id": self._id, "method": "tools/call",
                    "params": {"name": name, "arguments": args or {}},
                })
            except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
                if attempt == retries:
                    raise SloydError(None, f"network error: {err}")
                time.sleep(delay)
                delay *= 2
                continue
            except SloydError as err:
                if err.status and err.status >= 500 and attempt < retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise
            if "error" in msg:
                raise SloydError(None, f"MCP error: {msg['error']}")
            res = msg.get("result", {})
            data = res.get("structuredContent")
            text = " ".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
            if res.get("isError"):
                if "402" in text or (data or {}).get("error") == "Payment Required":
                    raise CreditsError(402, text, data)
                if "429" in text:
                    raise BusyError(429, text, data)
                if "401" in text:
                    raise AuthError(401, text, data)
                if any(code in text for code in ("500", "502", "503", "504")) and attempt < retries:
                    time.sleep(delay)
                    delay *= 2
                    continue
                raise SloydError(None, text, data)
            if data is None:
                try:
                    data = json.loads(text)
                except ValueError:
                    data = {"text": text}
            return data
        raise SloydError(None, "unreachable")

    # -- helpers -----------------------------------------------------------

    def balance(self) -> int:
        return int(self.tool("get_credit_balance").get("balance", 0))

    def styles(self) -> list[dict]:
        return self.tool("get_generation_styles").get("styles", [])

    def start(self, name: str, args: dict, busy_wait: float = 20.0, max_busy: int = 90) -> str:
        """Start a job; on 429 wait and retry (another job must finish first)."""
        for _ in range(max_busy):
            try:
                out = self.tool(name, args)
                job = out.get("jobId")
                if not job:
                    raise SloydError(None, f"{name} returned no jobId: {out}")
                return job
            except BusyError:
                time.sleep(busy_wait)
        raise BusyError(429, "Still at the 5-concurrent-job limit after a long wait.")

    def wait(self, job_id: str, timeout: float = 1800.0) -> dict:
        """Poll get_job with wait=30 until done. Returns the final job dict."""
        end = time.time() + timeout
        while time.time() < end:
            job = self.tool("get_job", {"jobId": job_id, "wait": 30})
            if job.get("done") or job.get("status") in ("success", "error", "completed", "failed"):
                return job
        raise SloydError(None, f"job {job_id} did not finish within {int(timeout)}s")


def download(url: str, path: str) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".part"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as resp, open(tmp, "wb") as fh:
                while True:
                    chunk = resp.read(1 << 16)
                    if not chunk:
                        break
                    fh.write(chunk)
            os.replace(tmp, path)
            return path
        except (urllib.error.URLError, TimeoutError):
            time.sleep(3 * (attempt + 1))
    raise SloydError(None, f"download failed: {url}")


def job_ok(job: dict) -> bool:
    return job.get("status") in ("success", "completed")


def setup() -> int:
    """Ask for the key, test it, save it to .env here, and keep .env out of git."""
    import getpass
    print("Sloyd API key setup")
    print(f"Get your key at {DASHBOARD} > API Keys > Generate Key.\n")
    cid = input("Paste your Client ID (starts with sok_) and press Enter: ").strip().strip('"\'')
    print("Paste your Client Secret and press Enter.")
    print("(Nothing will appear while you paste. That is normal.)")
    sec = getpass.getpass("Client Secret: ").strip().strip('"\'')
    if not cid.startswith("sok_"):
        print("\nThat Client ID does not start with sok_. Copy it again from the API Keys page and rerun setup.")
        return 1
    if not sec:
        print("\nNo secret was entered. Rerun setup and paste the secret.")
        return 1
    os.environ["SLOYD_CLIENT_ID"], os.environ["SLOYD_CLIENT_SECRET"] = cid, sec
    try:
        bal = Sloyd().balance()
    except AuthError:
        print("\nSloyd rejected this key. Check you copied the whole ID and secret, then rerun setup.")
        return 1
    except SloydError as err:
        print(f"\nCould not reach Sloyd: {err}. Check your internet connection and rerun setup.")
        return 1
    lines = []
    if os.path.isfile(".env"):
        with open(".env", encoding="utf-8") as fh:
            lines = [l.rstrip("\n") for l in fh if not l.startswith(("SLOYD_CLIENT_ID=", "SLOYD_CLIENT_SECRET="))]
    lines += [f"SLOYD_CLIENT_ID={cid}", f"SLOYD_CLIENT_SECRET={sec}"]
    with open(".env", "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    ignored = False
    if os.path.isfile(".gitignore"):
        with open(".gitignore", encoding="utf-8") as fh:
            ignored = any(l.strip() in (".env", "/.env", ".env*") for l in fh)
    if not ignored:
        with open(".gitignore", "a", encoding="utf-8") as fh:
            fh.write("\n# Sloyd API key (never commit)\n.env\n")
    print(f"\nDone. Your key works and is saved in {os.path.abspath('.env')}")
    print(".env is in .gitignore, so it will not be committed.")
    print(f"Credit balance: {bal}")
    if bal == 0:
        print(f"You have 0 credits. Buy some at {DASHBOARD} > Usage & Billing before making models.")
    return 0


def _main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[1]
    if cmd == "setup":
        try:
            return setup()
        except (KeyboardInterrupt, EOFError):
            print("\nSetup cancelled.")
            return 1
    try:
        if cmd == "download":
            print(download(argv[2], argv[3]))
            return 0
        api = Sloyd()
        if cmd in ("check", "balance"):
            bal = api.balance()
            print(json.dumps({"credentials": "ok", "balance": bal}))
            if bal == 0:
                print(f"Balance is 0. Buy credits at {DASHBOARD} (Usage & Billing).", file=sys.stderr)
            return 0
        if cmd == "styles":
            print(json.dumps(api.styles(), indent=1))
            return 0
        if cmd in ("call", "run"):
            name = argv[2]
            args = json.loads(argv[3]) if len(argv) > 3 else {}
            print(f"# estimated cost: {estimate(name, args)} credits", file=sys.stderr)
            if name in ("get_job", "get_credit_balance", "get_generation_styles", "upload_image"):
                print(json.dumps(api.tool(name, args), indent=1))
                return 0
            job = api.start(name, args)
            print(json.dumps({"jobId": job}))
            if cmd == "run":
                print(json.dumps(api.wait(job), indent=1))
            return 0
        if cmd == "wait":
            print(json.dumps(api.wait(argv[2]), indent=1))
            return 0
        print(__doc__)
        return 1
    except CreditsError as err:
        b = err.body
        print(f"402 insufficient credits: need {b.get('required')}, have {b.get('available')}. "
              f"Top up at {DASHBOARD}; nothing was charged.", file=sys.stderr)
        return 2
    except SloydError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
