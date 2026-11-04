# Roblox Studio

## Import

Studio > Home (or Avatar) > **Import 3D**, then select the `.glb` files from `export/roblox/`.
The 3D Importer supports glTF/GLB with meshes, PBR textures, rigs, skinning and animation, and
shows a preview with warnings before inserting. For many files, use the import queue to bring them
in one batch.

## Units

- Roblox measures in studs, at 1 stud = 0.28 m. A default R15 character is about 5 to 6 studs tall.
- `glb_tool.py export --engine roblox` pre-scales files to studs (a 1.0 m barrel is about 3.57
  studs).
- After import, compare one asset against a 4-stud Part or an R15 dummy. If the importer
  rescaled it, adjust the importer's scale or unit setting rather than resizing 40 MeshParts by
  hand.

## Hard limits (check before importing)

| Limit | Value | What to do |
|---|---|---|
| Triangles per mesh | 20,000 | `glb_tool.py inspect` reports `maxTrianglesPerMesh`. Regenerate with a lower `targetFaceCount`, or split with kitbasher (`partition`) |
| Texture size | 1024 x 1024 | Larger textures are downscaled. Use `textureResolution: "1k"` or lower in the bible. Even then, check: on the launch pack, 4 of 40 models requested at `1k` came back with one 2048 px texture. `glb_tool.py export --engine roblox` warns about each one |

The `Roblox` genStyleId plus budgets of 500 to 15,000 faces keeps packs comfortably inside both.

## Collision and performance

- `CollisionFidelity`:
  - Box for small props and clutter
  - Hull for medium props
  - Default or PreciseConvexDecomposition only for surfaces players stand on
- Anchor static props (`Anchored = true`). Set `CanCollide = false` on pure decoration.
- Leave `RenderFidelity` on Automatic so the engine handles distance LOD.
- Group variants in a Folder named after the asset (`DngChestA` with `DngChestAGold`). Copy
  placed props (Ctrl+D) instead of re-importing, so copies reuse the same uploaded mesh.

## Naming

PascalCase with no separators (`DngBarrelA`), which matches Roblox instance naming. Keep names
unique so scripts can find them with `FindFirstChild`.

## Pitfalls

- If a model imports as several MeshParts, the source has several meshes. That is expected for
  split results; group them in a Model.
- If an avatar item or character fails the Avatar Setup checks, it needs a rig and body-part split
  that prop packs do not have. Use Roblox's Avatar Setup tool, or Sloyd's avatar tools in the web
  app.
