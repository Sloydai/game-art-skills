# Godot 4

## Import

Godot imports `.glb` natively. Copy `export/godot/` to `res://art/<pack>/`. Each file becomes an
imported scene (`PackedScene`) that you can instance or open as a New Inherited Scene to attach
scripts.

- Units are meters and Y is up, the same as glTF. Files are already at real size with the pivot
  placed.
- File names are snake_case (`dng_barrel_a.glb`), following the Godot style guide.

## Collision from name suffixes (import hints)

Godot reads suffixes on node names in the source file and builds physics on import:

| Suffix | Result |
|---|---|
| `-col` | Mesh + StaticBody3D with a trimesh (concave) collision shape |
| `-convcol` | Mesh + StaticBody3D with a convex collision shape |
| `-colonly` | Trimesh collision only, no visible mesh |
| `-convcolonly` | Convex collision only |
| `-rigid` | RigidBody3D |
| `-noimp` | Node is not imported |

`glb_tool.py export --engine godot --godot-collision convcol` appends the suffix to every mesh
node. Choose:

- `convcol` for props: cheap, stable physics
- `col` for static set dressing the player walks on or around (arches, stairs)

To change collision per asset later, use the Advanced Import Settings dialog (double-click the
.glb). It overrides the suffix.

## LODs and shadows

Godot 4 generates LOD meshes and shadow meshes on import by default (Import dock > Meshes >
Generate LODs / Create Shadow Meshes). Leave them on. For low-poly packs the LODs are small but
harmless.

## Materials

Imported StandardMaterial3D from glTF PBR. For a stylized pack, extract materials (Advanced
Import Settings > Materials > Extract) and switch shading. For `Polygonal` packs, flat-shaded
normals in the file give faceted shading; do not enable "Ensure Tangents" unless you use normal
maps.

## Sloyd Godot Bridge (live drop-in)

Repository: https://github.com/Sloydai/sloyd-godot-bridge (Godot 4.x editor plugin, v1.0.3).

- Install: copy `addons/sloyd-godot-bridge/` into the project's `addons/`. Then go to Project >
  Project Settings > Plugins and enable "Sloyd Godot Bridge".
- The plugin listens on `127.0.0.1:6969` (the port in the v1.0.3 script; the README mentions
  4571, so check the Output panel line "Listening on ..."). It accepts
  `POST {"url": "...glb", "name": "..."}`, downloads the GLB, converts importer meshes to
  MeshInstance3D, names the mesh after `name`, and adds it to the edited scene root. Nodes are
  owned by the scene, so Ctrl+S keeps them.
- From the agent: `python3 scripts/send_to_godot.py --manifest manifest.json`. In the Sloyd web
  app: "Send to Godot".

Use the bridge for judging assets in the level's lighting. Use the export folder for the final
project files.

## Pitfalls

- If a model is enormous, it is the raw file. Use `export/godot/`.
- Duplicate node names get auto-suffixed (`Barrel2`). That is fine, but keep scene names unique
  per asset id.
- `-col` on a high-poly mesh makes a heavy trimesh shape. Prefer `convcol` or a simple box for
  moving props.
