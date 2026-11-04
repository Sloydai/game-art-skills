---
name: modeler
description: Use when the user needs an actual 3D model (GLB) for a game, whether from a text description, an approved concept image, a photo or sketch, or several views of the same object. Also use for "make this into 3D", "turn the concept into a model", re-rolling a bad mesh, or choosing between text-to-3D, image-to-3D and multi-image-to-3D. Picks the right Sloyd tool and parameters per asset under style-bible.md and hands GLBs to look-dev, kitbasher or engine-export. For 10+ assets at once, use asset-pack-builder instead.
---

# Modeler: the right route for each asset

Sloyd has three ways to make a model. Choosing well saves credits and rerolls. Read
`style-bible.md` first for `genStyleId`, `topology`, `textureResolution` and face budgets.

## Pick the route

| Situation | Route | Tool | Credits |
|---|---|---|---|
| Simple, iconic prop whose look the style already implies (barrel, crate, rock, bucket) | **text** | `generate_3d_from_text` | 25 |
| Design matters, the pack must match, or the user approved a concept | **concept** | `generate_image`, then `generate_3d_from_image` with `imageJobId` | 10 + 20 = 30 |
| User has an image (sketch, photo, screenshot, existing 2D art) | **image** | `upload_image` (free), then `generate_3d_from_image` | 20 |
| Hero asset or character where back and sides matter, and consistent views exist | **views** | `generate_3d_from_images` with `EnablePBR: "true"` | ~40 |
| Character for rigging | text or concept with `tPose: true` | either | same |
| Geometry only (you will texture elsewhere, or look-dev will retexture anyway) | any, `textureResolution: "none"` | either | 15 text, 10 image |

Rules of thumb:

- **Consistency beats speed in packs.** The concept route lets you check a 10-credit image before
  committing 20 credits to 3D, and the style lock happens in 2D, where it is cheap to fix.
- **Text route** is best when `genStyleId` and `model_suffix` carry the style on their own. Use it
  for filler and clutter.
- **Multi-view** only pays off when the views agree (see concept-artist turnarounds). One clean
  front image beats four inconsistent ones.
- Do not use `textureResolution: "none"` to save credits when the model needs its own colors.
  Retexturing later costs 15, so 15 + 15 = 30, more than 25 for a textured text model.

## Parameters

Always set these explicitly in a pack. Defaults drift.

- `topology`: from the bible (`triangles` for faceted low-poly, `quads` for DCC editing, +5
  credits).
- `targetFaceCount`: from the bible's size class. `0` lets Sloyd choose, which varies per asset.
- `textureResolution`: the bible's single value.
- `genStyleId` (text route only. Image routes inherit the style from the image).
- `tPose: true` for characters that will be rigged.
- Multi-view uses different field names: `FaceCount` as a numeric string, `EnablePBR` as
  `"true"`/`"false"`. There is no `topology` or `textureResolution`.

Text route prompt: `"<subject line>, <model_suffix>"`. Keep it under about 60 words. The subject
comes first, because generators weight early words more.

## Run it

1. Price it, check `get_credit_balance`, and tell the user the cost (sloyd-api section 4).
2. Start the job and record the `jobId` immediately (in `manifest.json` if there is a pack, or
   in your notes).
3. Poll `get_job` with `wait: 30` until `done`. 3D usually takes 1 to 4 minutes.
4. Download `outputs.glbUrl` to `art/<pack>/models/<asset_id>.glb`.
5. Up to 5 jobs can run at once. Start several, then poll them in turn.

## Review the model

Open the GLB (any glTF viewer, the pack gallery from asset-pack-builder, or
`python3 ${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/glb_tool.py inspect file.glb` for numbers). Check:

- [ ] Silhouette matches the concept or prompt; no missing parts or fused handles
- [ ] Triangle count within about 25% of the budget (`glb_tool.py inspect` reports it)
- [ ] Texture matches the bible's palette and style; no baked shadows from the concept image
- [ ] No floating debris, no internal faces poking through, no ground plane baked in
- [ ] Proportions match the other assets in the pack. Scale is fixed later in engine-export,
      but proportions are not

Reroll policy:

- If the problem is the input, fix the concept (concept-artist) and rerun image-to-3D (20).
- If the problem is texture only, retexture (look-dev, 15). This keeps the geometry.
- If geometry fails twice on text, switch to the concept route.
- Never reroll the same failing input more than twice. Change something.

## Hand-off

Report each model as `asset_id`, `jobId`, `glbUrl`, triangle count and cost. The `jobId` is what
look-dev (`retexture_model`) and kitbasher (`split_model_into_parts`) need. They only work on
jobs owned by this API key. For an external GLB, upload it first with REST
`POST /jobs/upload-3d` (free, see sloyd-api `references/rest-fallback.md`) to get a jobId.
