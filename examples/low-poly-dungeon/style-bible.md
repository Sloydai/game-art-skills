# Style Bible: Low-Poly Dungeon

Status: approved (2026-11-04, style test 2 passed)
Owner: art-director. Every Game Art Department skill reads this file before generating.

## Game
- Genre / setting: dungeon crawler, torch-lit stone halls, fantasy
- Camera: isometric / high third-person, typical distance 8 to 12 m
- Engine / platform: Godot 4, PC and web
- Assumptions made (not confirmed by user): props only, no characters; no LODs needed at this budget

## Sloyd settings (pack-wide constants)
- genStyleId: `Polygonal`
- topology: `triangles`
- textureResolution: `1k`
- Face budgets (targetFaceCount):
  - small (hand-held, < 0.5 m): 1,200
  - medium (0.5 to 2 m): 3,000
  - large (> 2 m, structures): 6,000
  - hero (focal assets): 10,000
- Characters: n/a

## Palette
| Role | Name (use these words in prompts) | Hex |
|---|---|---|
| Base 1 (~40%) | slate grey stone | #5b6270 |
| Base 2 (~20%) | warm oak brown | #8a5a3b |
| Secondary | wrought iron near-black | #2b2d33 |
| Secondary | moss green | #5f7d3a |
| Secondary | bone ivory | #e6dcc3 |
| Accent (interactables, loot) (~10%) | torch amber | #f2a33a |
| Emissive / magic | glowing teal | #2fd6c3 |

Value structure: dark stone and iron world. Wood sits at mid-value. Amber and teal are kept for
things the player can use, pick up or fear.

## Shape language and proportions
- Shape: chunky, slightly rounded masses
- Exaggeration: 1.3x thickness on handles, bands, legs and rims
- Edges: slightly bevelled facets, no sharp needles
- Silhouette rule: every prop readable as a black shape at 64 px from the isometric angle

## Texture style
- Treatment: flat color per facet with subtle gradient
- Wear and dirt: none in the generator ("edge wear" produced stray ivory chips in test 1); add wear as look-dev variants
- Baked lighting: none (the engine lights it)

## Material vocabulary
Use these phrases word for word.
- oak: warm oak brown planks or staves
- iron: wrought iron near-black bands, hinges, rims
- stone: slate grey stone blocks, moss green in the joints
- bone: bone ivory, chunky
- gold: polished gold
- flame: solid stylized torch amber flame shape
- magic: glowing teal

## Prompt template
- concept_suffix: `low-poly faceted game prop, flat-shaded triangles, chunky stylized proportions, slightly bevelled edges, only the colors named for this object, muted dungeon tones, flat colors with subtle gradient, clean unworn surfaces, single object only, no extra props or decorations, no base, no pedestal, no ground, centered, full object in frame, three-quarter view from slightly above, plain light grey background, even soft lighting, no shadow, no text`
- model_suffix: `low-poly faceted game prop, flat-shaded, chunky stylized proportions, slightly bevelled edges, only the colors named for this object, muted dungeon tones, flat colors with subtle gradient, single object, no base`
- retexture suffix: `low-poly flat colors with subtle gradient, clean surfaces`
- Subject line pattern: `<object>, <material from vocabulary>, <one distinguishing feature>`

## Banned words
realistic, photorealistic, 8k, highly detailed, intricate, cinematic, dramatic lighting,
masterpiece, depth of field, on a table, in a room, scene, pile of, lots of

## Approved references
| What | jobId | URL |
|---|---|---|
| style test: health potion | `8uvsejm3` | https://storage.googleapis.com/ai-services-quality/jobs/8uvsejm3.webp |
| style test: wooden cart | `uuupb8t4` | https://storage.googleapis.com/ai-services-quality/jobs/uuupb8t4.webp |
| style test: glowing mushroom cluster | `j555x2c5` | https://storage.googleapis.com/ai-services-quality/jobs/j555x2c5.webp |
| rejected test 1 (palette bleed, wear chips, pedestal) | `t41qy9i0`, `w8dkctup`, `9u0gtqj5` | |

## Naming
- Asset id pattern: `dng_<object>_<letter>` (e.g. `dng_barrel_a`), snake_case, unique
- Variant suffix: `__<variant>` (e.g. `dng_chest_a__gold`)

## Change log
- 2026-11-04: created for the launch demo pack
- 2026-11-04: style test 2 passed (60 credits for both tests)
- 2026-11-04: style test 1 failed: the full palette list in the suffix put every color on every prop, "light edge wear" made ivory chips, and the mushrooms grew a pedestal. Palette words now come only from each subject line; added no base / no extra props; removed wear
