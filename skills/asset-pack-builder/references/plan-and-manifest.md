# plan.json and manifest.json

## plan.json (input, written by the agent)

```json
{
  "pack": "low-poly-dungeon",
  "title": "Low-Poly Dungeon Props (40)",
  "styleBible": "style-bible.md",
  "maxConcurrent": 5,
  "defaults": {
    "route": "concept",
    "genStyleId": "Polygonal",
    "topology": "triangles",
    "textureResolution": "1k",
    "aspectRatio": "1:1",
    "conceptSuffix": "<bible concept_suffix>",
    "modelSuffix": "<bible model_suffix>",
    "retextureSuffix": "<bible texture style words>"
  },
  "budgets": { "small": 1200, "medium": 3000, "large": 6000, "hero": 10000 },
  "assets": [
    {
      "id": "dng_chest_a",
      "name": "Treasure Chest",
      "category": "containers",
      "size": "hero",
      "heightM": 0.7,
      "subject": "treasure chest, warm oak brown planks with wrought iron bands, domed lid with a skull-shaped lock",
      "variants": [{ "name": "gold", "prompt": "polished gold metal replacing all iron bands ..." }]
    },
    {
      "id": "dng_barrel_a",
      "route": "text",
      "size": "medium",
      "heightM": 1.0,
      "subject": "wooden barrel, warm oak brown staves with wrought iron bands",
      "split": { "method": "partition", "numberOfParts": 6 }
    }
  ]
}
```

| Field | Notes |
|---|---|
| `pack` | Slug. Used for folders and engine names |
| `defaults.*` | Applied to every asset unless the asset overrides the same key |
| `budgets` | `targetFaceCount` per `size`, used when an asset has no explicit `targetFaceCount` |
| `assets[].id` | Unique, permanent, snake_case |
| `assets[].route` | `concept` (generate_image, then generate_3d_from_image), `text` (generate_3d_from_text), `image` (upload_image from `image` URL, then generate_3d_from_image), `views` (generate_3d_from_images from `views.front` plus `left`/`back`/`right` URLs) |
| `assets[].subject` | Subject line only. Suffixes are appended: `subject, conceptSuffix` or `subject, modelSuffix` |
| `assets[].heightM` | Vertical bounding-box height in meters for engine-export scaling |
| `assets[].tPose` | Characters that will be rigged |
| `assets[].variants[]` | `{name, prompt}`. Each one is a `retexture_model` on the finished model. `retextureSuffix` is appended |
| `assets[].split` | `{method: "partition" \| "decomposition", numberOfParts: 4-16, attachmentPoints: bool}` |

Only parameters that exist on the Sloyd tools are passed through: `genStyleId`, `topology`,
`targetFaceCount`, `textureResolution`, `aspectRatio`, `tPose`, and for multi-view `FaceCount`
and `EnablePBR` (set automatically from `textureResolution`).

## manifest.json (output and state, written by run_pack.py)

```json
{
  "schema": "sloyd-game-art/manifest@1",
  "pack": "low-poly-dungeon",
  "title": "Low-Poly Dungeon Props (40)",
  "styleBible": "style-bible.md",
  "genStyleId": "Polygonal",
  "textureResolution": "1k",
  "topology": "triangles",
  "createdAt": "2026-11-04T10:00:00Z",
  "updatedAt": "2026-11-04T10:42:00Z",
  "totals": { "assets": 40, "done": 40, "failed": 0, "creditsSpentEstimate": 1270, "creditsRemainingEstimate": 0 },
  "assets": [
    {
      "id": "dng_chest_a",
      "name": "Treasure Chest",
      "category": "containers",
      "size": "hero",
      "heightM": 0.7,
      "route": "concept",
      "subject": "treasure chest, ...",
      "targetFaceCount": 10000,
      "status": "done",
      "jobs": {
        "concept":      { "tool": "generate_image", "args": {...}, "jobId": "...", "status": "success", "url": "https://.../x.webp", "file": "concepts/dng_chest_a.webp", "estimate": 10, "attempts": 1 },
        "model":        { "tool": "generate_3d_from_image", "args": {"imageJobId": {"$from": "concept"}, ...}, "jobId": "...", "status": "success", "url": "https://.../y.glb", "file": "models/dng_chest_a.glb", "estimate": 20 },
        "variant:gold": { "tool": "retexture_model", "jobId": "...", "file": "variants/dng_chest_a__gold.glb", ... }
      }
    }
  ]
}
```

- `status` per asset: `planned`, `partial`, `done` or `failed`.
- `status` per job: `planned`, `running`, `success` or `error`.
- `{"$from": "<stage>"}` in `args` is resolved at run time to that stage's `jobId`.
- Any `jobId` with `status: "success"` can be passed to `retexture_model` or
  `split_model_into_parts` later (model stages only).
- To redo a stage, set its `status` to `planned` and `attempts` to `0`, then re-run with
  `--only <id>`. Later stages that depend on it should be reset too.
- `assets[].rerolls[]`: `{reason, previous: {stage: jobId}}` for every replaced attempt.
  `assets[].rejected[]`: `{stage, jobIds, reason}` for attempts that were dropped. The runner
  keeps both across runs.
- `spend` (optional, written by the agent at delivery): the real balance before and after, and
  a breakdown. `totals.creditsSpentEstimate` only counts the current jobs, not rerolls or style
  tests.
- Never put credentials in either file.

engine-export adds an `export` block per asset (file names per engine, triangle counts, scale).
See engine-export.
