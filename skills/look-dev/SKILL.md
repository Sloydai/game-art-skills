---
name: look-dev
description: Use when an existing 3D model needs new surface looks without changing its shape. Examples include material or wear variants (rusty, frozen, burnt, mossy, gold, cursed), team or faction colors, seasonal or biome versions, rarity tiers (common/rare/epic/legendary), damaged states, or fixing a model whose geometry is good but whose texture is off-style. Uses Sloyd retexture_model on a model jobId and keeps variants consistent with style-bible.md.
---

# Look-dev: variants from one mesh

`retexture_model` paints a new texture onto an existing model job. It costs 15 credits, against
25 to 30 for a new model, and the silhouette stays identical. That is exactly what games need for
variants: the player learns the shape once, and the material tells them what changed.

Inputs: a model `jobId` owned by this key (from modeler or asset-pack-builder, or an uploaded GLB),
and `style-bible.md`.

## Write texture prompts like a material artist

A retexture prompt describes surfaces, not objects. The model already exists. Structure:

`<base material in bible vocabulary>, <condition or effect>, <where it appears>, <bible texture style words>`

| Variant | Prompt (low-poly dungeon bible) |
|---|---|
| Rusty | `wrought iron bands heavily oxidized, orange-brown rust bloom collecting in crevices and edges, oak planks darker and water-stained, flat color with subtle gradient` |
| Frozen | `surfaces coated in pale blue frost, thick white ice crust on top edges, small icicle shapes along the bottom rim, cold desaturated colors, flat color with subtle gradient` |
| Gold / legendary | `polished gold metal replacing iron, warm yellow highlights on edges, oak stained deep red-brown, small ruby inlays, flat color with subtle gradient` |
| Burnt | `charred black wood with glowing ember orange cracks, soot on upper surfaces, iron darkened, flat color` |
| Mossy / overgrown | `green moss patches on top surfaces and joints, damp darker wood, iron with green patina, flat color with subtle gradient` |
| Cursed | `wood bleached bone white, iron turned black-purple, faint violet glow in the cracks, flat color` |
| Team red / blue | `<same base prompt>, painted panels and trims in crimson red #c0392b` and the same with `royal blue #2e5aac`. Change only the color words between teams |

Rules:

- **Keep the bible's texture style words at the end of every variant.** That is what stops a
  "gold" variant from coming back photoreal.
- **Name where the effect goes** (edges, crevices, top surfaces, bottom rim). Effects that follow
  form read as believable; uniform overlays look like a filter.
- **One idea per variant.** "Rusty and frozen and gold" produces mud.
- **Team colors:** generate the first team, review, then copy that prompt word for word and swap
  only the color name and hex. Any other wording change drifts more than the color.
- **Rarity tiers** should step along one axis, usually trim material: iron, then steel with blue
  trim, then gold, then gold with emissive gems. That way the tiers read as a sequence.
- Keep `textureResolution` equal to the bible's value (the API defaults to `2k`, so pass it
  explicitly when the bible says `1k` or `512`).

## Run

1. Plan the variant list with names: `<asset_id>__<variant>` (e.g. `dng_chest_a__gold`).
2. Price: 15 credits each. Check the balance and tell the user.
3. `retexture_model {jobId, prompt, textureResolution}`, then poll `get_job` with `wait: 30`.
   Up to 5 in parallel.
4. Download `outputs.glbUrl` to `art/<pack>/variants/<asset_id>__<variant>.glb`.
5. Add each variant to `manifest.json` under its parent asset's `variants` (see
   asset-pack-builder `references/manifest-schema.md`).

## Review

- [ ] Geometry unchanged (same silhouette; retexture does not move vertices)
- [ ] Effect follows form (edges, crevices) rather than a flat overlay
- [ ] Variant still in the bible's texture style and saturation band
- [ ] Team variants differ only in team color
- [ ] Readable at game distance: squint test. Could the player tell rusty from normal?

What worked and what did not on the launch pack:

- **Worked first time:** gold and rusty chest, mossy door, mana potion, frozen barrel. These are
  large surfaces where the effect has room.
- **Failed twice:** a frozen short sword came back dark green both times, even with explicit
  colors and hex. Thin objects (blades, keys, wands, staffs) do not take surface effects well,
  because there is too little surface. For thin objects, make the variant as a new concept
  instead (concept-artist plus modeler, 30 credits), or apply the effect in the engine with an
  emissive or frost shader.
- **Texture fix on a base model:** a stray blue stripe on the anvil stump was fixed with one
  retexture that named every part's color and added "no blue". Retexture is the cheapest fix
  when the geometry is right.

If a variant fails, change one phrase and rerun once. If the base texture is the problem (a bad
source model), fix the base first. Variants inherit its UVs.

## Engine-side alternative

For pure color swaps (team colors on a flat-shaded pack), an engine material tint or palette-swap
shader can be cheaper than baked variants and costs no credits. Recommend it when the user needs
more than 4 or 5 colors per asset, or runtime customization. Keep `retexture_model` for changes of
material (rust, ice, gold) that a tint cannot fake.
