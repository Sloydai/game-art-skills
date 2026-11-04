---
name: engine-export
description: Use when Sloyd GLBs (single models or a pack manifest.json) need to go into a game engine, either Unity, Godot, Unreal Engine or Roblox Studio. Also use for "import these into Godot", "make them game-ready", or questions about scale, units, pivots, naming conventions, collision, LODs, triangle limits or why a model is huge, tiny, sideways or floating after import. Normalizes scale and pivots without touching materials, names files per engine, writes IMPORT.md, and can push models live into Godot via the Sloyd Godot Bridge.
---

# Engine Export: from GLB to placed, collidable, correctly sized asset

Generated models arrive with arbitrary scale and an origin wherever the generator put it. A barrel
that imports at 40 meters tall, or with its pivot at the center so it sinks half into the floor,
costs the developer more time than generating it did. This skill makes every asset land in the
engine at the right size, on the floor, with a predictable name.

Input: `manifest.json` from asset-pack-builder (preferred), or individual GLBs plus the intended
heights. Everything here is local file work and costs no credits.

## 1. Check before converting

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/glb_tool.py inspect art/<pack>/models/*.glb
```

This reports triangles, per-mesh maximum, bounds in meters, texture sizes and required extensions.
Flag anything over its budget, any Roblox mesh over 20,000 triangles, and any asset whose
proportions look wrong next to its `heightM`. A 0.3 m potion that is wider than it is tall needs
a look before you scale it.

## 2. Export for the engine

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/glb_tool.py export art/<pack>/manifest.json --engine godot --godot-collision convcol
python3 ${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/glb_tool.py export art/<pack>/manifest.json --engine unity
python3 ${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/glb_tool.py export art/<pack>/manifest.json --engine unreal
python3 ${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/glb_tool.py export art/<pack>/manifest.json --engine roblox
```

For every model, variant and split result, the export:

- **Scales** uniformly so the vertical extent equals the asset's `heightM` (meters; Roblox is
  converted to studs at 1 stud = 0.28 m).
- **Places the pivot** by usage:
  - `bottom-center` for floor props (default)
  - `back-center` for wall-mounted props (torch, sconce, lever, sign, banner); glTF back is -Z
  - `top-center` for hanging props (lantern, chandelier, cage)

  These are guessed from the asset id. Set `"pivot"` on a plan asset to override.
- **Names** files and mesh nodes per engine convention. Asset id `dng_barrel_a` becomes:

  | Engine | Name |
  |---|---|
  | Godot | `dng_barrel_a` |
  | Unity | `Dng_Barrel_A` |
  | Unreal | `SM_Dng_Barrel_A` |
  | Roblox | `DngBarrelA` |

  Variants append their name: `SM_Dng_Chest_A_Gold`.
- **Writes** `export/<engine>/` plus `IMPORT.md` (steps, a file table with triangles, size and
  pivot, and warnings), and records an `export` block per asset in `manifest.json`.

The tool wraps the scene in one transform node. Vertex data, materials and textures are copied
byte for byte, so nothing is re-compressed or lost.

Sizes are axis-aligned bounds. For rotated sub-meshes they are slightly conservative, which is
fine for placement.

Single file:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/glb_tool.py normalize in.glb out.glb --height 1.0 --pivot bottom-center --name Barrel_A
```

Use `--node-suffix=-convcol` (with `=`) for Godot hints.

## 3. Engine notes

Read the matching reference before giving import advice. Each covers importer setup, units,
materials, collision, LODs and the pitfalls specific to that engine.

- Unity: [references/unity.md](references/unity.md). glTFast package; meters; colliders; static
  batching.
- Godot: [references/godot.md](references/godot.md). Native GLB; import-hint suffixes for
  collision; auto LOD; the Sloyd Godot Bridge.
- Unreal: [references/unreal.md](references/unreal.md). glTF importer (meters to cm); SM_
  naming; collision; LODs vs Nanite; `${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/unreal_import.py` batch import.
- Roblox: [references/roblox.md](references/roblox.md). 3D Importer; studs; 20k triangles per
  mesh; 1024 px textures; CollisionFidelity.

## 4. LODs

Low-poly packs (under ~3k triangles per prop) usually need no LODs. Above that:

- **Godot** generates LODs on import automatically.
- **Unreal**: Static Mesh editor, LOD Settings, Number of LODs (auto reduction).
- **Unity**: author LOD files and use a LODGroup. Generate the meshes with meshoptimizer's
  gltfpack:
  `npx gltfpack -i Dng_Chest_A.glb -o Dng_Chest_A_LOD1.glb -si 0.5 -noq` (and `-si 0.25` for
  LOD2). `-noq` keeps the output readable by importers without `KHR_mesh_quantization` support.
- **Roblox** handles mesh LOD itself (RenderFidelity Automatic).

## 5. Live preview in Godot (optional)

With the [Sloyd Godot Bridge](https://github.com/Sloydai/sloyd-godot-bridge) enabled in the open
project:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/send_to_godot.py --ping
python3 ${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/send_to_godot.py --manifest art/<pack>/manifest.json --only dng_chest_a,dng_barrel_a
```

The bridge downloads each GLB and adds it to the edited scene. This is good for judging scale and
palette in the real level lighting. It sends raw Sloyd models; final assets come from
`export/godot/`.

## Hand-off

Tell the user:

- the export folder per engine
- the `IMPORT.md` path
- any warnings (over budget, Roblox limits, odd proportions)
- the one manual step their engine still needs, usually colliders in Unity or Unreal
