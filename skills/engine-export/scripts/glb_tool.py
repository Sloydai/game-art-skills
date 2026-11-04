#!/usr/bin/env python3
"""Inspect and engine-prep GLB files without touching meshes, materials or textures.

    python3 glb_tool.py inspect models/*.glb
    python3 glb_tool.py normalize in.glb out.glb --height 1.0 --pivot bottom-center --name Barrel_A
    python3 glb_tool.py split parts.glb out_dir --prefix Barrel_A [--recenter]
    python3 glb_tool.py export art/dungeon/manifest.json --engine godot   [--out DIR] [--godot-collision convcol]

normalize wraps the scene in one new root node that scales and offsets it. Vertex data,
materials and textures stay byte-for-byte identical, so nothing is lost or re-compressed.

  --height M     uniform scale so the vertical (Y) extent is M meters
  --pivot        bottom-center (props on the floor, default) | back-center (wall-mounted,
                 glTF back = -Z) | top-center (hanging) | center | none
  --name         root node and mesh name
  --node-suffix  appended to mesh node names, e.g. Godot import hints -col, -convcol, -colonly

export reads manifest.json (asset-pack-builder), normalizes every model and variant to its
heightM, names files per engine convention, writes them to export/<engine>/, records
the result in the manifest's "export" block, and writes export/<engine>/IMPORT.md.

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import struct
import sys

GLB_MAGIC = 0x46546C67
CHUNK_JSON = 0x4E4F534A
CHUNK_BIN = 0x004E4942

# ------------------------------------------------------------------ GLB io


def read_glb(path: str) -> tuple[dict, bytes]:
    with open(path, "rb") as fh:
        data = fh.read()
    magic, version, _length = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC or version != 2:
        raise ValueError(f"{path}: not a glTF 2.0 binary (.glb)")
    off = 12
    gltf, binchunk = None, b""
    while off < len(data):
        clen, ctype = struct.unpack_from("<II", data, off)
        chunk = data[off + 8: off + 8 + clen]
        if ctype == CHUNK_JSON:
            gltf = json.loads(chunk.decode("utf-8"))
        elif ctype == CHUNK_BIN:
            binchunk = chunk
        off += 8 + clen
    if gltf is None:
        raise ValueError(f"{path}: no JSON chunk")
    return gltf, binchunk


def write_glb(path: str, gltf: dict, binchunk: bytes) -> None:
    js = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    js += b" " * ((4 - len(js) % 4) % 4)
    parts = [struct.pack("<II", len(js), CHUNK_JSON), js]
    if binchunk:
        b = binchunk + b"\0" * ((4 - len(binchunk) % 4) % 4)
        parts += [struct.pack("<II", len(b), CHUNK_BIN), b]
    body = b"".join(parts)
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(struct.pack("<III", GLB_MAGIC, 2, 12 + len(body)))
        fh.write(body)


# ------------------------------------------------------------------ math (column-major 4x4)


def mat_mul(a: list[float], b: list[float]) -> list[float]:
    out = [0.0] * 16
    for c in range(4):
        for r in range(4):
            out[c * 4 + r] = sum(a[k * 4 + r] * b[c * 4 + k] for k in range(4))
    return out


def node_matrix(node: dict) -> list[float]:
    if "matrix" in node:
        return [float(x) for x in node["matrix"]]
    tx, ty, tz = node.get("translation", [0, 0, 0])
    x, y, z, w = node.get("rotation", [0, 0, 0, 1])
    sx, sy, sz = node.get("scale", [1, 1, 1])
    r = [
        1 - 2 * (y * y + z * z), 2 * (x * y + z * w), 2 * (x * z - y * w), 0,
        2 * (x * y - z * w), 1 - 2 * (x * x + z * z), 2 * (y * z + x * w), 0,
        2 * (x * z + y * w), 2 * (y * z - x * w), 1 - 2 * (x * x + y * y), 0,
        0, 0, 0, 1,
    ]
    s = [sx, 0, 0, 0, 0, sy, 0, 0, 0, 0, sz, 0, 0, 0, 0, 1]
    t = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, tx, ty, tz, 1]
    return mat_mul(t, mat_mul(r, s))


def apply(m: list[float], p: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = p
    return (m[0] * x + m[4] * y + m[8] * z + m[12],
            m[1] * x + m[5] * y + m[9] * z + m[13],
            m[2] * x + m[6] * y + m[10] * z + m[14])


IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def scene_roots(gltf: dict) -> list[int]:
    scenes = gltf.get("scenes") or [{"nodes": list(range(len(gltf.get("nodes", []))))}]
    return list(scenes[gltf.get("scene", 0)].get("nodes", []))


def walk(gltf: dict):
    """Yield (node_index, world_matrix) for every node in the default scene."""
    nodes = gltf.get("nodes", [])
    stack = [(i, IDENTITY) for i in scene_roots(gltf)]
    while stack:
        i, parent = stack.pop()
        m = mat_mul(parent, node_matrix(nodes[i]))
        yield i, m
        for c in nodes[i].get("children", []):
            stack.append((c, m))


# ------------------------------------------------------------------ analysis


def bounds(gltf: dict) -> tuple[list[float], list[float]] | None:
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    meshes = gltf.get("meshes", [])
    acc = gltf.get("accessors", [])
    for i, m in walk(gltf):
        node = gltf["nodes"][i]
        if "mesh" not in node:
            continue
        for prim in meshes[node["mesh"]].get("primitives", []):
            a = acc[prim["attributes"]["POSITION"]]
            if "min" not in a or "max" not in a:
                continue
            mn, mx = a["min"], a["max"]
            for cx in (mn[0], mx[0]):
                for cy in (mn[1], mx[1]):
                    for cz in (mn[2], mx[2]):
                        p = apply(m, (cx, cy, cz))
                        for k in range(3):
                            lo[k] = min(lo[k], p[k])
                            hi[k] = max(hi[k], p[k])
    if lo[0] == math.inf:
        return None
    return lo, hi


def triangles(gltf: dict) -> tuple[int, list[int]]:
    meshes = gltf.get("meshes", [])
    acc = gltf.get("accessors", [])
    per_mesh = []
    for mesh in meshes:
        t = 0
        for prim in mesh.get("primitives", []):
            mode = prim.get("mode", 4)
            n = acc[prim["indices"]]["count"] if "indices" in prim else acc[prim["attributes"]["POSITION"]]["count"]
            if mode == 4:
                t += n // 3
            elif mode in (5, 6):
                t += max(0, n - 2)
        per_mesh.append(t)
    total = 0
    for i, _ in walk(gltf):
        node = gltf["nodes"][i]
        if "mesh" in node:
            total += per_mesh[node["mesh"]]
    return total, per_mesh


def image_size(b: bytes) -> tuple[int, int] | None:
    if b[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", b[16:24])
    if b[:2] == b"\xff\xd8":
        i = 2
        while i < len(b) - 9:
            if b[i] != 0xFF:
                i += 1
                continue
            marker = b[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", b[i + 5: i + 9])
                return w, h
            seg = struct.unpack(">H", b[i + 2: i + 4])[0]
            i += 2 + seg
        return None
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP":
        kind = b[12:16]
        if kind == b"VP8 ":
            w, h = struct.unpack("<HH", b[26:30])
            return w & 0x3FFF, h & 0x3FFF
        if kind == b"VP8L":
            v = int.from_bytes(b[21:25], "little")
            return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
        if kind == b"VP8X":
            return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    return None


def textures(gltf: dict, binchunk: bytes) -> list[dict]:
    out = []
    views = gltf.get("bufferViews", [])
    for idx, img in enumerate(gltf.get("images", [])):
        size = None
        if "bufferView" in img:
            v = views[img["bufferView"]]
            start = v.get("byteOffset", 0)
            size = image_size(binchunk[start: start + min(v["byteLength"], 65536)])
        out.append({"index": idx, "name": img.get("name", ""), "mimeType": img.get("mimeType", ""),
                    "size": list(size) if size else None})
    return out


def inspect(path: str) -> dict:
    gltf, binchunk = read_glb(path)
    b = bounds(gltf)
    tris, per_mesh = triangles(gltf)
    info = {
        "file": path,
        "bytes": os.path.getsize(path),
        "meshes": len(gltf.get("meshes", [])),
        "nodes": len(gltf.get("nodes", [])),
        "materials": len(gltf.get("materials", [])),
        "triangles": tris,
        "maxTrianglesPerMesh": max(per_mesh) if per_mesh else 0,
        "textures": textures(gltf, binchunk),
        "extensionsRequired": gltf.get("extensionsRequired", []),
    }
    if b:
        lo, hi = b
        info["boundsMin"] = [round(x, 4) for x in lo]
        info["boundsMax"] = [round(x, 4) for x in hi]
        info["size"] = [round(hi[k] - lo[k], 4) for k in range(3)]
    return info


# ------------------------------------------------------------------ normalize


def normalize(src: str, dst: str, height: float | None = None, pivot: str = "bottom-center",
              name: str | None = None, node_suffix: str = "", unit_scale: float = 1.0) -> dict:
    gltf, binchunk = read_glb(src)
    b = bounds(gltf)
    if not b:
        raise ValueError(f"{src}: no mesh bounds found")
    lo, hi = b
    h = hi[1] - lo[1]
    s = (height / h if height and h > 0 else 1.0) * unit_scale
    cx, cy, cz = [(lo[k] + hi[k]) / 2 for k in range(3)]
    anchor = {
        "bottom-center": (cx, lo[1], cz),
        "back-center": (cx, cy, lo[2]),
        "top-center": (cx, hi[1], cz),
        "center": (cx, cy, cz),
        "none": (0.0, 0.0, 0.0),
    }[pivot]
    roots = scene_roots(gltf)
    nodes = gltf.setdefault("nodes", [])
    root = {
        "name": name or os.path.splitext(os.path.basename(dst))[0],
        "children": roots,
        "translation": [-anchor[0] * s, -anchor[1] * s, -anchor[2] * s],
        "scale": [s, s, s],
    }
    nodes.append(root)
    scenes = gltf.setdefault("scenes", [{"nodes": roots}])
    si = gltf.get("scene", 0)
    gltf["scene"] = si
    scenes[si]["nodes"] = [len(nodes) - 1]
    if name:
        meshes = gltf.get("meshes", [])
        multi = len(meshes) > 1
        for i, m in enumerate(meshes):
            m["name"] = f"{name}_{i}" if multi else name
        k = 0
        for i, _ in walk(gltf):
            n = nodes[i]
            if "mesh" in n:
                n["name"] = (f"{name}_{k}" if multi else f"{name}_Mesh") + node_suffix
                k += 1
    gltf.setdefault("asset", {"version": "2.0"})
    gltf["asset"]["generator"] = (gltf["asset"].get("generator", "") + " + sloyd-game-art glb_tool").strip(" +")
    write_glb(dst, gltf, binchunk)
    return inspect(dst)


# ------------------------------------------------------------------ split into part files


def _texture_refs(obj, out: list) -> None:
    """Collect every {'index': n} textureInfo dict inside a material (incl. extensions)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.endswith("Texture") and isinstance(v, dict) and "index" in v:
                out.append(v)
            _texture_refs(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _texture_refs(v, out)


def extract_node(gltf: dict, binchunk: bytes, node_index: int, world: list[float], name: str) -> tuple[dict, bytes]:
    """A standalone GLB holding one mesh node, with only the data it references."""
    src_mesh = gltf["meshes"][gltf["nodes"][node_index]["mesh"]]
    mesh = json.loads(json.dumps(src_mesh))
    acc_map: dict[int, int] = {}
    view_map: dict[int, int] = {}
    mat_map: dict[int, int] = {}
    tex_map: dict[int, int] = {}
    img_map: dict[int, int] = {}
    out = {"asset": {"version": "2.0", "generator": "sloyd-game-art glb_tool split"},
           "accessors": [], "bufferViews": [], "materials": [], "textures": [], "images": [],
           "samplers": json.loads(json.dumps(gltf.get("samplers", [])))}
    blob = bytearray()

    def view(i: int) -> int:
        if i not in view_map:
            v = dict(gltf["bufferViews"][i])
            start = v.get("byteOffset", 0)
            data = binchunk[start: start + v["byteLength"]]
            blob.extend(b"\0" * ((4 - len(blob) % 4) % 4))
            v["buffer"] = 0
            v["byteOffset"] = len(blob)
            blob.extend(data)
            view_map[i] = len(out["bufferViews"])
            out["bufferViews"].append(v)
        return view_map[i]

    def accessor(i: int) -> int:
        if i not in acc_map:
            a = json.loads(json.dumps(gltf["accessors"][i]))
            if "bufferView" in a:
                a["bufferView"] = view(a["bufferView"])
            sp = a.get("sparse")
            if sp:
                sp["indices"]["bufferView"] = view(sp["indices"]["bufferView"])
                sp["values"]["bufferView"] = view(sp["values"]["bufferView"])
            acc_map[i] = len(out["accessors"])
            out["accessors"].append(a)
        return acc_map[i]

    def image(i: int) -> int:
        if i not in img_map:
            im = dict(gltf["images"][i])
            if "bufferView" in im:
                im["bufferView"] = view(im["bufferView"])
            img_map[i] = len(out["images"])
            out["images"].append(im)
        return img_map[i]

    def texture(i: int) -> int:
        if i not in tex_map:
            t = json.loads(json.dumps(gltf["textures"][i]))
            if "source" in t:
                t["source"] = image(t["source"])
            for ext in (t.get("extensions") or {}).values():
                if isinstance(ext, dict) and "source" in ext:
                    ext["source"] = image(ext["source"])
            tex_map[i] = len(out["textures"])
            out["textures"].append(t)
        return tex_map[i]

    def material(i: int) -> int:
        if i not in mat_map:
            m = json.loads(json.dumps(gltf["materials"][i]))
            refs: list = []
            _texture_refs(m, refs)
            for r in refs:
                r["index"] = texture(r["index"])
            mat_map[i] = len(out["materials"])
            out["materials"].append(m)
        return mat_map[i]

    for prim in mesh.get("primitives", []):
        prim["attributes"] = {k: accessor(v) for k, v in prim["attributes"].items()}
        if "indices" in prim:
            prim["indices"] = accessor(prim["indices"])
        if "targets" in prim:
            prim["targets"] = [{k: accessor(v) for k, v in t.items()} for t in prim["targets"]]
        if "material" in prim:
            prim["material"] = material(prim["material"])
    mesh["name"] = name
    out["meshes"] = [mesh]
    out["nodes"] = [{"name": name, "mesh": 0, "matrix": [float(x) for x in world]}]
    out["scenes"] = [{"nodes": [0]}]
    out["scene"] = 0
    out["buffers"] = [{"byteLength": len(blob)}]
    for key in ("extensionsUsed", "extensionsRequired"):
        if key in gltf:
            out[key] = list(gltf[key])
    for key in ("materials", "textures", "images", "samplers"):
        if not out[key]:
            del out[key]
    return out, bytes(blob)


def split_file(src: str, out_dir: str, prefix: str, recenter: bool) -> list[dict]:
    gltf, binchunk = read_glb(src)
    mesh_nodes = [(i, m) for i, m in walk(gltf) if "mesh" in gltf["nodes"][i]]
    os.makedirs(out_dir, exist_ok=True)
    parts = []
    for k, (i, world) in enumerate(sorted(mesh_nodes)):
        nm = f"{prefix}_Part{k + 1:02d}"
        part, blob = extract_node(gltf, binchunk, i, world, nm)
        dst = os.path.join(out_dir, nm + ".glb")
        write_glb(dst, part, blob)
        info = inspect(dst)
        rec = {"file": os.path.basename(dst), "triangles": info["triangles"], "size": info.get("size")}
        if recenter:
            lo, hi = info["boundsMin"], info["boundsMax"]
            rec["assembledOffset"] = [round((lo[0] + hi[0]) / 2, 4), round(lo[1], 4), round((lo[2] + hi[2]) / 2, 4)]
            normalize(dst, dst, pivot="bottom-center", name=nm)
        parts.append(rec)
    with open(os.path.join(out_dir, f"{prefix}_parts.json"), "w", encoding="utf-8") as fh:
        json.dump({"source": os.path.basename(src), "recentered": recenter, "parts": parts}, fh, indent=2)
    return parts


# ------------------------------------------------------------------ engine export

ENGINES = {
    "unity": {"unit": 1.0, "pivot_note": "meters, Y-up (glTFast converts handedness)"},
    "godot": {"unit": 1.0, "pivot_note": "meters, Y-up"},
    "unreal": {"unit": 1.0, "pivot_note": "meters in file; the glTF importer converts to centimeters"},
    "roblox": {"unit": 1.0 / 0.28, "pivot_note": "pre-scaled to studs (1 stud = 0.28 m)"},
}


def words(asset_id: str) -> list[str]:
    return [w for w in asset_id.replace("-", "_").split("_") if w]


def engine_name(asset_id: str, engine: str, variant: str | None = None) -> str:
    w = words(asset_id) + (words(variant) if variant else [])
    if engine == "godot":
        return "_".join(x.lower() for x in w)
    cap = [x[:1].upper() + x[1:] for x in w]
    if engine == "unity":
        return "_".join(cap)
    if engine == "unreal":
        return "SM_" + "_".join(cap)
    if engine == "roblox":
        return "".join(cap)
    raise ValueError(engine)


DEFAULT_PIVOTS = {
    "back-center": ("torch", "sconce", "lever", "banner", "sign", "plaque", "shelf_wall", "mirror"),
    "top-center": ("lantern", "chandelier", "hanging", "cage"),
}


def guess_pivot(asset: dict) -> str:
    if asset.get("pivot"):
        return asset["pivot"]
    aid = asset["id"]
    for pivot, keys in DEFAULT_PIVOTS.items():
        if any(k in aid for k in keys):
            return pivot
    return "bottom-center"


def export_pack(manifest_path: str, engine: str, out: str | None, godot_collision: str | None) -> int:
    base = os.path.dirname(os.path.abspath(manifest_path))
    with open(manifest_path, encoding="utf-8") as fh:
        man = json.load(fh)
    out = out or os.path.join(base, "export", engine)
    os.makedirs(out, exist_ok=True)
    cfg = ENGINES[engine]
    suffix = f"-{godot_collision}" if engine == "godot" and godot_collision else ""
    rows, warnings = [], []
    for a in man["assets"]:
        jobs = a.get("jobs", {})
        items = [(None, jobs.get("model"))] + [
            (k.split(":", 1)[1], j) for k, j in jobs.items() if k.startswith("variant:")]
        if jobs.get("split"):
            items.append(("parts", jobs["split"]))
        pivot = guess_pivot(a)
        a.setdefault("export", {})[engine] = []
        for variant, job in items:
            if not job or job.get("status") not in ("success", "completed") or not job.get("file"):
                continue
            src = os.path.join(base, job["file"])
            if not os.path.isfile(src):
                warnings.append(f"{a['id']}: missing file {job['file']}")
                continue
            nm = engine_name(a["id"], engine, variant)
            dst = os.path.join(out, nm + ".glb")
            info = normalize(src, dst, height=a.get("heightM"), pivot=pivot, name=nm,
                             node_suffix=suffix, unit_scale=cfg["unit"])
            rec = {"file": os.path.relpath(dst, base), "name": nm, "triangles": info["triangles"],
                   "size": info.get("size"), "pivot": pivot}
            a["export"][engine].append(rec)
            rows.append(rec)
            budget = a.get("targetFaceCount") or 0
            if budget and info["triangles"] > budget * 2.5:
                warnings.append(f"{nm}: {info['triangles']} triangles vs budget {budget} faces")
            if engine == "roblox":
                if info["maxTrianglesPerMesh"] > 20000:
                    warnings.append(f"{nm}: a mesh has {info['maxTrianglesPerMesh']} triangles; Roblox allows 20,000 per mesh")
                big = [t for t in info["textures"] if t["size"] and max(t["size"]) > 1024]
                if big:
                    warnings.append(f"{nm}: textures larger than 1024 px are downscaled by Roblox")
            if info["extensionsRequired"]:
                warnings.append(f"{nm}: requires extensions {info['extensionsRequired']}")
    with open(manifest_path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=2)
    os.replace(manifest_path + ".tmp", manifest_path)
    write_import_notes(out, engine, man, rows, warnings, suffix)
    print(f"{len(rows)} files -> {out}")
    for w in warnings:
        print("warning:", w)
    return 0


def write_import_notes(out: str, engine: str, man: dict, rows: list[dict], warnings: list[str], suffix: str) -> None:
    steps = {
        "unity": [
            "Install glTFast: Window > Package Manager > + > Add package by name > `com.unity.cloud.gltfast`.",
            f"Copy this folder to `Assets/Art/{man['pack']}/`. Each .glb imports as a prefab-like asset.",
            "Files are in meters with the pivot already placed, so leave Scale Factor at 1.",
            "Drag into the scene, add colliders (Box/Capsule for props, Mesh Collider only for static set dressing) and save as prefabs.",
            "Mark non-moving set dressing Static (batching and baked GI).",
        ],
        "godot": [
            f"Copy this folder to `res://art/{man['pack']}/`. Godot imports each .glb as a scene.",
            "Files are in meters with the pivot already placed, so no root scale is needed.",
            ("Collision is generated on import from the mesh-name suffix `" + suffix + "`." if suffix else
             "For automatic collision, re-export with `--godot-collision convcol` (convex) or `col` (trimesh)."),
            "LODs and shadow meshes are generated on import by default (Import dock > Meshes).",
            "Instance the .glb scenes, or use 'New Inherited Scene' to add scripts.",
            "To drop single models into the open scene while iterating, use `send_to_godot.py` with the Sloyd Godot Bridge.",
        ],
        "unreal": [
            "Import: Content Browser > Import, select the .glb files (UE 5.x glTF importer), or run `unreal_import.py`.",
            "The glTF importer converts meters to centimeters. Check one asset against the 180 cm mannequin.",
            "Pivots are already placed at bottom-center (floor props), back-center (wall props) or top-center (hanging props).",
            "Open each Static Mesh: add simple collision (Collision > Add Box/Capsule) and set LODs (LOD Settings > Number of LODs, e.g. 3).",
            "Enable Nanite only for high-poly hero meshes. Low-poly packs gain nothing from it.",
        ],
        "roblox": [
            "Studio > Home > Import 3D, select the .glb files.",
            "Files are pre-scaled to studs (1 stud = 0.28 m). Compare against a 4-stud part or an R15 dummy after import.",
            "Each mesh must stay under 20,000 triangles; textures above 1024 px are downscaled.",
            "Set CollisionFidelity to Box or Hull for small props, and keep PreciseConvexDecomposition for walk-on surfaces only.",
            "Anchor static props. Group variants under a Folder named after the asset.",
        ],
    }[engine]
    lines = [f"# Import into {engine.title()}: {man.get('title', man['pack'])}", "",
             f"{len(rows)} files, units: {ENGINES[engine]['pivot_note']}.", "", "## Steps", ""]
    lines += [f"{i}. {s}" for i, s in enumerate(steps, 1)]
    lines += ["", "## Files", "", "| File | Triangles | Size (x, y, z) | Pivot |", "|---|---|---|---|"]
    for r in rows:
        size = ", ".join(f"{v:.2f}" for v in (r.get("size") or []))
        lines.append(f"| `{os.path.basename(r['file'])}` | {r['triangles']} | {size} | {r['pivot']} |")
    if warnings:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in warnings]
    with open(os.path.join(out, "IMPORT.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# ------------------------------------------------------------------ cli


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inspect")
    p.add_argument("files", nargs="+")
    p = sub.add_parser("normalize")
    p.add_argument("src")
    p.add_argument("dst")
    p.add_argument("--height", type=float)
    p.add_argument("--pivot", default="bottom-center",
                   choices=["bottom-center", "back-center", "top-center", "center", "none"])
    p.add_argument("--name")
    p.add_argument("--node-suffix", default="")
    p.add_argument("--unit-scale", type=float, default=1.0)
    p = sub.add_parser("split")
    p.add_argument("src")
    p.add_argument("out_dir")
    p.add_argument("--prefix", required=True)
    p.add_argument("--recenter", action="store_true",
                   help="pivot each part at its own bottom-center (kit library); offsets go to <prefix>_parts.json")
    p = sub.add_parser("export")
    p.add_argument("manifest")
    p.add_argument("--engine", required=True, choices=sorted(ENGINES))
    p.add_argument("--out")
    p.add_argument("--godot-collision", choices=["col", "convcol", "colonly", "convcolonly"])
    args = ap.parse_args()

    if args.cmd == "inspect":
        for f in args.files:
            try:
                print(json.dumps(inspect(f)))
            except (ValueError, OSError) as err:
                print(json.dumps({"file": f, "error": str(err)}))
        return 0
    if args.cmd == "normalize":
        print(json.dumps(normalize(args.src, args.dst, args.height, args.pivot, args.name,
                                   args.node_suffix, args.unit_scale)))
        return 0
    if args.cmd == "split":
        print(json.dumps(split_file(args.src, args.out_dir, args.prefix, args.recenter), indent=1))
        return 0
    return export_pack(args.manifest, args.engine, args.out, args.godot_collision)


if __name__ == "__main__":
    sys.exit(main())
