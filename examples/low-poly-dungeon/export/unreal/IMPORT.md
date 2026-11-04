# Import into Unreal: Low-Poly Dungeon Props (40)

46 files, units: meters in file; the glTF importer converts to centimeters.

## Steps

1. Import: Content Browser > Import, select the .glb files (UE 5.x glTF importer), or run `unreal_import.py`.
2. The glTF importer converts meters to centimeters. Check one asset against the 180 cm mannequin.
3. Pivots are already placed at bottom-center (floor props), back-center (wall props) or top-center (hanging props).
4. Open each Static Mesh: add simple collision (Collision > Add Box/Capsule) and set LODs (LOD Settings > Number of LODs, e.g. 3).
5. Enable Nanite only for high-poly hero meshes. Low-poly packs gain nothing from it.

## Files

| File | Triangles | Size (x, y, z) | Pivot |
|---|---|---|---|
| `SM_Dng_Barrel_A.glb` | 2999 | 0.82, 1.00, 0.82 | bottom-center |
| `SM_Dng_Barrel_A_Frozen.glb` | 2999 | 0.82, 1.00, 0.82 | bottom-center |
| `SM_Dng_Barrel_A_Parts.glb` | 4443 | 0.82, 1.00, 0.82 | bottom-center |
| `SM_Dng_Crate_A.glb` | 3000 | 1.25, 0.80, 1.24 | bottom-center |
| `SM_Dng_Chest_A.glb` | 10000 | 0.75, 0.70, 0.57 | bottom-center |
| `SM_Dng_Chest_A_Gold.glb` | 10000 | 0.75, 0.70, 0.57 | bottom-center |
| `SM_Dng_Chest_A_Rusty.glb` | 10000 | 0.75, 0.70, 0.57 | bottom-center |
| `SM_Dng_Urn_A.glb` | 1200 | 0.24, 0.60, 0.19 | bottom-center |
| `SM_Dng_Coffin_A.glb` | 6000 | 0.68, 0.60, 1.43 | bottom-center |
| `SM_Dng_Table_A.glb` | 3000 | 1.26, 0.80, 1.05 | bottom-center |
| `SM_Dng_Chair_A.glb` | 3000 | 0.51, 1.00, 0.53 | bottom-center |
| `SM_Dng_Bench_A.glb` | 3000 | 1.41, 0.50, 0.57 | bottom-center |
| `SM_Dng_Bookshelf_A.glb` | 6000 | 1.14, 2.00, 0.46 | bottom-center |
| `SM_Dng_Stool_A.glb` | 1200 | 0.64, 0.50, 0.63 | bottom-center |
| `SM_Dng_Throne_A.glb` | 10000 | 1.28, 2.00, 0.83 | bottom-center |
| `SM_Dng_Wall_Torch_A.glb` | 1200 | 0.27, 0.60, 0.15 | back-center |
| `SM_Dng_Brazier_A.glb` | 3000 | 0.91, 1.00, 0.92 | bottom-center |
| `SM_Dng_Candelabra_A.glb` | 1200 | 0.35, 0.70, 0.22 | bottom-center |
| `SM_Dng_Lantern_A.glb` | 1200 | 0.25, 0.50, 0.23 | top-center |
| `SM_Dng_Potion_A.glb` | 1200 | 0.20, 0.30, 0.21 | bottom-center |
| `SM_Dng_Potion_A_Mana.glb` | 1200 | 0.20, 0.30, 0.21 | bottom-center |
| `SM_Dng_Coins_A.glb` | 1200 | 0.17, 0.20, 0.17 | bottom-center |
| `SM_Dng_Key_A.glb` | 1200 | 0.56, 0.25, 1.74 | bottom-center |
| `SM_Dng_Scroll_A.glb` | 1200 | 1.37, 0.30, 0.31 | bottom-center |
| `SM_Dng_Skull_A.glb` | 1200 | 0.17, 0.25, 0.22 | bottom-center |
| `SM_Dng_Sword_A.glb` | 1200 | 0.26, 0.90, 0.09 | bottom-center |
| `SM_Dng_Shield_A.glb` | 3000 | 0.89, 0.90, 0.18 | bottom-center |
| `SM_Dng_Axe_A.glb` | 3000 | 0.34, 1.00, 0.11 | bottom-center |
| `SM_Dng_Spellbook_A.glb` | 1200 | 0.29, 0.30, 0.29 | bottom-center |
| `SM_Dng_Spike_Trap_A.glb` | 3000 | 0.81, 0.40, 0.82 | bottom-center |
| `SM_Dng_Bear_Trap_A.glb` | 1200 | 1.04, 0.25, 0.92 | bottom-center |
| `SM_Dng_Lever_A.glb` | 1200 | 0.33, 0.60, 0.34 | back-center |
| `SM_Dng_Pillar_A.glb` | 6000 | 1.33, 3.00, 1.33 | bottom-center |
| `SM_Dng_Pillar_Broken_A.glb` | 6000 | 0.42, 1.60, 0.41 | bottom-center |
| `SM_Dng_Archway_A.glb` | 6000 | 2.66, 3.50, 0.71 | bottom-center |
| `SM_Dng_Door_A.glb` | 6000 | 1.65, 2.40, 0.40 | bottom-center |
| `SM_Dng_Door_A_Mossy.glb` | 6000 | 1.65, 2.40, 0.40 | bottom-center |
| `SM_Dng_Gargoyle_A.glb` | 10000 | 1.11, 1.50, 0.93 | bottom-center |
| `SM_Dng_Altar_A.glb` | 5999 | 1.57, 1.00, 1.15 | bottom-center |
| `SM_Dng_Mushrooms_A.glb` | 1200 | 0.39, 0.50, 0.27 | bottom-center |
| `SM_Dng_Boulder_A.glb` | 3000 | 1.56, 1.00, 1.63 | bottom-center |
| `SM_Dng_Crystal_A.glb` | 3000 | 0.57, 0.80, 0.61 | bottom-center |
| `SM_Dng_Ribcage_A.glb` | 1196 | 0.36, 0.40, 0.61 | top-center |
| `SM_Dng_Cauldron_A.glb` | 3000 | 0.71, 0.80, 0.73 | bottom-center |
| `SM_Dng_Anvil_A.glb` | 2999 | 0.92, 0.80, 0.63 | bottom-center |
| `SM_Dng_Weapon_Rack_A.glb` | 6000 | 1.00, 1.60, 0.60 | bottom-center |
