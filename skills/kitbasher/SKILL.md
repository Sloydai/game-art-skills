---
name: kitbasher
description: Use when a 3D model should become separate pieces for a game. Examples are destructible or breakable props (a barrel that shatters, a wall that crumbles), modular kits to mix and match (swap sword hilts and blades, armor pieces, vehicle parts), parts that animate separately (chest lid, door, wheels), or "split this model into parts". Uses Sloyd split_model_into_parts (partition or decomposition) on a model jobId, then cuts the result into per-part GLB files with pivots for engine use.
---

# Kitbasher: one model, many usable pieces

`split_model_into_parts` (40 credits, about 2.5 to 4 minutes) returns a new model whose parts
are separate meshes. The method decides what those parts are good for. Choose by the game need,
not by the model.

## Choose the method

| Game need | Method | Why |
|---|---|---|
| Destructible / breakable prop (barrel smash, crumbling pillar, pot shatter) | `partition`, `numberOfParts` 4 to 8 | Slices through the surface. Pieces fit back together exactly, keep the original texture, and each cut gets a flat cap, so fragments look solid from inside |
| Pre-fractured large structure | `partition`, 10 to 16 | More, smaller chunks. The result can be 2 more or fewer than asked |
| Animated sub-parts (chest lid, door leaf, cart wheels, turret head) | `decomposition` | Separates natural components as complete parts, rebuilding hidden surfaces (the chest body under the lid) |
| Modular kit to recombine (blades and hilts, helmets and armor pieces) | `decomposition` | Each part is whole on its own, so it can be reused on other assets |
| Physical 3D-print pieces | `partition` + `attachmentPoints: true` | Pins and holes. Do not use for games, because the pins are extra geometry |

Known trade-offs:

- **`decomposition` parts have no textures** and usually more polygons than the source. Plan to
  texture them, either:
  - in the engine with the pack's palette materials (simplest for flat low-poly packs)
  - by uploading a part GLB through REST `POST /jobs/upload-3d` (free) and running look-dev
    `retexture_model` on the returned jobId (15 credits)
- **`partition` caps are flat and untextured-looking** (they keep the source texturing around
  the cut). For destructibles, that is usually what you want: the inside reads as solid
  material. Hide the seam with a dust or particle burst on break.
- `partition` needs a source GLB of 16 MB or less.

## Run

1. Take a finished model `jobId` owned by this key (from modeler or `manifest.json`). External
   GLB: upload it first with REST `POST /jobs/upload-3d`.
2. Price: 40 credits. Check the balance and tell the user.
3. Call `split_model_into_parts`:
   - `{jobId, method: "partition", numberOfParts: 6}`
   - or `{jobId, method: "decomposition"}`

   The returned `jobId` is the new split model, not the source.
4. Poll `get_job` with `wait: 30` and download `outputs.glbUrl`. In a pack, add
   `"split": {...}` to the asset in `plan.json` and asset-pack-builder runs it as a stage.

## Turn the result into engine pieces

The split GLB holds every part as its own mesh in its assembled position. Normalize first, so
parts share the asset's real size, then cut it into files:

```bash
S="${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts"
python3 $S/glb_tool.py normalize parts/dng_barrel_a__parts.glb tmp/barrel_parts.glb --height 1.0 --name Barrel_A
python3 $S/glb_tool.py split tmp/barrel_parts.glb export/kit/barrel_a --prefix Barrel_A             # assembled
python3 $S/glb_tool.py split tmp/barrel_parts.glb export/kit/barrel_a_lib --prefix Barrel_A --recenter  # library
```

- **Assembled** (default): every part keeps its position. Import all parts under one parent at
  the same origin and the prop is whole. Use this for destructibles: swap the intact model for
  the parts on hit, then enable physics per part.
- **Library** (`--recenter`): each part's pivot moves to its own bottom-center. Use this for kits
  that snap or recombine. `<prefix>_parts.json` stores each part's `assembledOffset`, so code can
  rebuild the original.

Materials and textures are copied byte for byte. Each file contains only its own part's data.

## Destructible recipe (any engine)

1. Keep the intact model (the asset's `model` GLB) for normal play.
2. On break, hide it, spawn the assembled parts at its transform, give each a rigid body with a
   convex collider, and apply a small outward impulse from the hit point.
3. Despawn or freeze fragments after 3 to 5 seconds to protect performance.
4. Six to eight parts read as "smashed" at game distance. More is rarely worth the physics cost.

## Modular kit rules

- Name parts by role after inspecting them (`Sword_A_Blade`, `Sword_A_Hilt`). The split returns
  them numbered (`Part01`), so rename files and update `_parts.json`.
- Recombine across assets only within one style bible. A blade from a `Polygonal` sword will not
  sit right on a `HandpaintedStylized` hilt.
- AI parts are not grid-exact. For architecture that must tile (walls, floors on a 2 m or 4 m
  grid), build the grid pieces in the engine or a DCC, and use Sloyd for the dressing on top
  (arches, pillars, doors, trims).

## Hand-off

Report:

- the split `jobId`
- the part count
- folders for the assembled and library versions
- triangle counts per part (the `_parts.json` file)

Then hand to engine-export, or straight to the engine with the destructible recipe.
