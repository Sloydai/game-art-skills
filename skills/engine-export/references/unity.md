# Unity

## Importer

Unity has no built-in glTF importer. Install one:

- **glTFast** (Unity's official package): Package Manager > `+` > Add package by name >
  `com.unity.cloud.gltfast`. It supports the Built-in render pipeline, URP and HDRP and imports
  `.glb` files dropped into `Assets/` as assets you can drag into scenes.
- UnityGLTF (Khronos) is an alternative if the project already uses it.

## Units and orientation

- 1 Unity unit = 1 meter, the same as glTF. Files from `glb_tool.py export --engine unity` are
  already at real size, so keep Scale Factor 1.
- glTF is right-handed Y-up and Unity is left-handed Y-up. glTFast converts, so models face +Z
  in Unity. If a prop faces the wrong way, rotate the prefab root, not the mesh.

## Materials

glTFast creates materials from glTF PBR (base color, metallic-roughness, normal, emission).
Flat low-poly packs look right with the default lit shader. For a toon look, swap shaders on the
generated materials, or extract them and assign your own. Keep the texture.

Texture import: set Max Size to the bible's resolution, compression Normal Quality, and leave
mipmaps on. For pixel-crisp retro styles (`RetroCRT90s`), use Filter Mode Point.

## Prefabs and collision

1. Drag the imported model into a scene.
2. Add colliders:
   - BoxCollider or CapsuleCollider for props the player bumps into
   - MeshCollider (non-convex) only for static, walkable set dressing
   - convex MeshCollider for small dynamic props with a Rigidbody
3. Mark non-moving set dressing **Static** for batching and baked lighting.
4. Save as a prefab in `Assets/Art/<Pack>/Prefabs/` named after the file (`Dng_Barrel_A`).
5. Variants: make the base a prefab and the variants Prefab Variants. Swap only the mesh or
   material.

## LODs

Add a LODGroup and assign `_LOD1` / `_LOD2` meshes made with
`npx gltfpack -i X.glb -o X_LOD1.glb -si 0.5 -noq`. Skip this for props under ~3k triangles.

## Pitfalls

- A prop sinking into the floor means the pivot was not normalized. Use the export folder, not
  raw `models/`.
- Pink materials in URP or HDRP mean the importer's shader is not in the build. Check glTFast's
  shader variant settings, or reference its shaders in Project Settings > Graphics.
- If a model looks oddly smooth or faceted, check the mesh's Normals import settings. Faceted
  low-poly packs need the file's normals, not recalculated ones.
