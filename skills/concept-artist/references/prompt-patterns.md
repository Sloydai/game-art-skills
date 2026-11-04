# Subject-line patterns by prop family

Pattern: `<object>, <material phrase from the bible>, <one distinguishing feature>`. The bible's
`concept_suffix` is appended after this. Examples assume a low-poly dungeon bible.

| Family | Good subject line | Avoid |
|---|---|---|
| Container | `wooden barrel, warm oak brown staves with wrought iron bands, one band slightly loose` | "barrel full of apples on a stone floor" (scene, multiple objects) |
| Furniture | `heavy wooden table, warm oak brown, thick square legs, one corner chipped` | "medieval tavern table with food and candles" |
| Light source | `iron wall sconce with torch, wrought iron, flame as a solid stylized amber shape` | "flickering torch casting dramatic light" (lighting is the engine's job) |
| Loot | `small treasure chest, oak with gold trim, slightly open lid showing coins` | "pile of treasure" (shapeless) |
| Weapon | `short sword, worn steel blade, leather-wrapped grip, round pommel`, front or side view | three-quarter view on thin objects hides the blade profile |
| Hazard | `floor spike trap, slate grey stone tile with iron spikes raised` | "deadly trap" (no shape information) |
| Architecture dressing | `stone archway segment, slate grey blocks, moss in the joints` | full rooms or corridors (use kits, see kitbasher) |
| Organic | `cluster of three glowing mushrooms, bone ivory stems, teal caps` | "forest floor with mushrooms" |
| Rocks | `medium boulder, slate grey, flat top, mossy north side` | "rocks" (plural means multiple objects) |
| Character | `goblin warrior, standing, neutral T-pose, leather armor, oversized hands`, `tPose: true` | action poses (they get baked into the mesh) |

## Words that help reconstruction

`single object`, `centered`, `full object in frame`, `three-quarter view`, `plain background`,
`even soft lighting`, `no shadow`, `solid`, `chunky`.

## Words that hurt packs

`highly detailed`, `intricate`, `8k`, `photorealistic` (in stylized packs), `cinematic`,
`dramatic lighting`, `depth of field`, `bokeh`, `on a table`, `in a room`, `scene`, `pile of`,
`lots of`, `various`.

## Thin and transparent things

Chains, ropes, cloth fringes, glass and liquids reconstruct poorly from one image. Make them
chunky and opaque: "thick rope", "stylized solid flame", "opaque frosted glass bottle with a
cork". Or plan them as separate engine effects (particles, shaders).

## Variation without drift

When a pack needs "the same chair, three ways", keep the subject line identical except for one
slot: `wooden chair, warm oak brown, <intact | one leg broken | tipped over>`. For pure material
or color variants, skip concept work and use look-dev (`retexture_model`, 15 credits) on the
finished model. That keeps the silhouette identical and costs less than a new model.
