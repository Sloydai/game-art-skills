# Import into Godot: Low-Poly Dungeon Props (40)

46 files, units: meters, Y-up.

## Steps

1. Copy this folder to `res://art/low-poly-dungeon/`. Godot imports each .glb as a scene.
2. Files are in meters with the pivot already placed, so no root scale is needed.
3. Collision is generated on import from the mesh-name suffix `-convcol`.
4. LODs and shadow meshes are generated on import by default (Import dock > Meshes).
5. Instance the .glb scenes, or use 'New Inherited Scene' to add scripts.
6. To drop single models into the open scene while iterating, use `send_to_godot.py` with the Sloyd Godot Bridge.

## Files

| File | Triangles | Size (x, y, z) | Pivot |
|---|---|---|---|
| `dng_barrel_a.glb` | 2999 | 0.82, 1.00, 0.82 | bottom-center |
| `dng_barrel_a_frozen.glb` | 2999 | 0.82, 1.00, 0.82 | bottom-center |
| `dng_barrel_a_parts.glb` | 4443 | 0.82, 1.00, 0.82 | bottom-center |
| `dng_crate_a.glb` | 3000 | 1.25, 0.80, 1.24 | bottom-center |
| `dng_chest_a.glb` | 10000 | 0.75, 0.70, 0.57 | bottom-center |
| `dng_chest_a_gold.glb` | 10000 | 0.75, 0.70, 0.57 | bottom-center |
| `dng_chest_a_rusty.glb` | 10000 | 0.75, 0.70, 0.57 | bottom-center |
| `dng_urn_a.glb` | 1200 | 0.24, 0.60, 0.19 | bottom-center |
| `dng_coffin_a.glb` | 6000 | 0.68, 0.60, 1.43 | bottom-center |
| `dng_table_a.glb` | 3000 | 1.26, 0.80, 1.05 | bottom-center |
| `dng_chair_a.glb` | 3000 | 0.51, 1.00, 0.53 | bottom-center |
| `dng_bench_a.glb` | 3000 | 1.41, 0.50, 0.57 | bottom-center |
| `dng_bookshelf_a.glb` | 6000 | 1.14, 2.00, 0.46 | bottom-center |
| `dng_stool_a.glb` | 1200 | 0.64, 0.50, 0.63 | bottom-center |
| `dng_throne_a.glb` | 10000 | 1.28, 2.00, 0.83 | bottom-center |
| `dng_wall_torch_a.glb` | 1200 | 0.27, 0.60, 0.15 | back-center |
| `dng_brazier_a.glb` | 3000 | 0.91, 1.00, 0.92 | bottom-center |
| `dng_candelabra_a.glb` | 1200 | 0.35, 0.70, 0.22 | bottom-center |
| `dng_lantern_a.glb` | 1200 | 0.25, 0.50, 0.23 | top-center |
| `dng_potion_a.glb` | 1200 | 0.20, 0.30, 0.21 | bottom-center |
| `dng_potion_a_mana.glb` | 1200 | 0.20, 0.30, 0.21 | bottom-center |
| `dng_coins_a.glb` | 1200 | 0.17, 0.20, 0.17 | bottom-center |
| `dng_key_a.glb` | 1200 | 0.56, 0.25, 1.74 | bottom-center |
| `dng_scroll_a.glb` | 1200 | 1.37, 0.30, 0.31 | bottom-center |
| `dng_skull_a.glb` | 1200 | 0.17, 0.25, 0.22 | bottom-center |
| `dng_sword_a.glb` | 1200 | 0.26, 0.90, 0.09 | bottom-center |
| `dng_shield_a.glb` | 3000 | 0.89, 0.90, 0.18 | bottom-center |
| `dng_axe_a.glb` | 3000 | 0.34, 1.00, 0.11 | bottom-center |
| `dng_spellbook_a.glb` | 1200 | 0.29, 0.30, 0.29 | bottom-center |
| `dng_spike_trap_a.glb` | 3000 | 0.81, 0.40, 0.82 | bottom-center |
| `dng_bear_trap_a.glb` | 1200 | 1.04, 0.25, 0.92 | bottom-center |
| `dng_lever_a.glb` | 1200 | 0.33, 0.60, 0.34 | back-center |
| `dng_pillar_a.glb` | 6000 | 1.33, 3.00, 1.33 | bottom-center |
| `dng_pillar_broken_a.glb` | 6000 | 0.42, 1.60, 0.41 | bottom-center |
| `dng_archway_a.glb` | 6000 | 2.66, 3.50, 0.71 | bottom-center |
| `dng_door_a.glb` | 6000 | 1.65, 2.40, 0.40 | bottom-center |
| `dng_door_a_mossy.glb` | 6000 | 1.65, 2.40, 0.40 | bottom-center |
| `dng_gargoyle_a.glb` | 10000 | 1.11, 1.50, 0.93 | bottom-center |
| `dng_altar_a.glb` | 5999 | 1.57, 1.00, 1.15 | bottom-center |
| `dng_mushrooms_a.glb` | 1200 | 0.39, 0.50, 0.27 | bottom-center |
| `dng_boulder_a.glb` | 3000 | 1.56, 1.00, 1.63 | bottom-center |
| `dng_crystal_a.glb` | 3000 | 0.57, 0.80, 0.61 | bottom-center |
| `dng_ribcage_a.glb` | 1196 | 0.36, 0.40, 0.61 | top-center |
| `dng_cauldron_a.glb` | 3000 | 0.71, 0.80, 0.73 | bottom-center |
| `dng_anvil_a.glb` | 2999 | 0.92, 0.80, 0.63 | bottom-center |
| `dng_weapon_rack_a.glb` | 6000 | 1.00, 1.60, 0.60 | bottom-center |
