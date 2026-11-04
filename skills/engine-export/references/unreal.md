# Unreal Engine 5

## Import

UE 5.x imports glTF/GLB natively (Content Browser > Import). For a whole pack, run the bundled
script inside the editor (needs the Python Editor Script Plugin):

```
py "C:/path/to/skills/engine-export/scripts/unreal_import.py" "C:/path/to/art/<pack>/export/unreal" "/Game/Art/<Pack>"
```

It imports every `.glb` as a Static Mesh with the file name as the asset name, with no dialogs,
replacing existing assets, and saves.

## Units and naming

- glTF is in meters; Unreal works in centimeters. The glTF importer converts, so a 1.0 m barrel
  arrives about 100 uu tall. Check one asset next to the 180 cm mannequin before importing 40.
- Naming follows the common Unreal convention:
  - `SM_` static meshes
  - `M_` / `MI_` materials and material instances
  - `T_` textures

  The export already prefixes meshes `SM_`. Rename generated materials to `MI_<Asset>` if the
  project enforces the convention.
- Pivots are already at bottom-center (floor), back-center (wall) or top-center (hanging), so
  props snap to the floor or wall with the End key.

## Collision

Imported meshes have no simple collision. Per mesh, in the Static Mesh editor:

- small props: Collision > Add Box or Capsule Simplified Collision
- irregular props: Auto Convex Collision (hull count 4 to 8)
- walk-on set dressing: Collision Complexity "Use Complex Collision As Simple" (static only)

## LODs vs Nanite

- Low-poly packs (under ~5k triangles): no LODs, no Nanite.
- Mid-poly props: Static Mesh editor > LOD Settings > Number of LODs = 3 (auto reduction).
- High-poly hero or realistic meshes: enable Nanite (Details > Nanite Settings > Enable).
  Nanite does not help low-poly flat-shaded assets.

## Materials

The importer builds materials from glTF PBR. For a pack, make one master material in the
bible's style (flat, toon or PBR) and convert the imported ones to instances of it. This keeps
the pack's lighting response identical.

## Pitfalls

- If a mesh is 100x too small or large, the importer setting was changed, or the file was
  exported in another unit. Re-export from `glb_tool.py`, which always writes meters.
- Black or very dark assets usually mean a missing sky light in a new level, not a broken texture.
