# Style Bible: Low-Poly Dungeon

Status: draft. Becomes approved after the style test below passes.
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
- Wear and dirt: light wear on edges only
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
- concept_suffix: `low-poly faceted game prop, flat-shaded triangles, chunky stylized proportions, slightly bevelled edges, limited palette of slate grey stone, warm oak brown, wrought iron near-black, torch amber, moss green and bone ivory, flat colors with subtle gradient, light edge wear, single object, centered, full object in frame, three-quarter view from slightly above, plain light grey background, even soft lighting, no shadow, no text`
- model_suffix: `low-poly faceted game prop, flat-shaded, chunky stylized proportions, slightly bevelled edges, slate grey stone, warm oak brown, wrought iron near-black, torch amber accents, flat colors with subtle gradient, single object`
- retexture suffix: `low-poly flat colors with subtle gradient, light edge wear`
- Subject line pattern: `<object>, <material from vocabulary>, <one distinguishing feature>`

## Banned words
realistic, photorealistic, 8k, highly detailed, intricate, cinematic, dramatic lighting,
masterpiece, depth of field, on a table, in a room, scene, pile of, lots of

## Approved references
| What | jobId | URL |
|---|---|---|
| style test 1: health potion | (filled by the style test) | |
| style test 2: wooden cart | | |
| style test 3: glowing mushroom cluster | | |

## Naming
- Asset id pattern: `dng_<object>_<letter>` (e.g. `dng_barrel_a`), snake_case, unique
- Variant suffix: `__<variant>` (e.g. `dng_chest_a__gold`)

## Change log
- 2026-11-04: created for the launch demo pack
