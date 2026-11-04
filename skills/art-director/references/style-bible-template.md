# Style Bible: <Pack or game name>

Status: draft | approved (<date>, by <user>)
Owner: art-director. Every Game Art Department skill reads this file before generating.

## Game
- Genre / setting:
- Camera: <top-down | isometric | third-person | first-person | side-on>, typical distance <m>
- Engine / platform:
- Assumptions made (not confirmed by user):

## Sloyd settings (pack-wide constants)
- genStyleId: `<one id from get_generation_styles>`
- topology: `<auto | triangles | quads>`
- textureResolution: `<512 | 1k | 2k>`
- Face budgets (targetFaceCount):
  - small (hand-held, < 0.5 m): <n>
  - medium (furniture, 0.5 to 2 m): <n>
  - large (> 2 m, vehicles, structures): <n>
  - hero (focal assets): <n>
- Characters: tPose `<true | false>`

## Palette
| Role | Name (use these words in prompts) | Hex |
|---|---|---|
| Base 1 (~40%) | | |
| Base 2 (~20%) | | |
| Secondary | | |
| Secondary | | |
| Secondary | | |
| Accent (interactables, loot) (~10%) | | |
| Emissive / magic (optional) | | |

Value structure: <e.g. dark world, mid-value props, bright accent on anything the player can use>

## Shape language and proportions
- Shape: <chunky / rounded / blocky / angular / spindly>
- Exaggeration: <1:1 | 1.2-1.5x stylized | 2x toy>
- Edges: <sharp faceted | bevelled | soft rounded>
- Silhouette rule: <e.g. every prop readable as a flat black silhouette at 64 px>

## Texture style
- Treatment: <flat color | gradient | hand-painted | PBR stylized | PBR realistic>
- Wear and dirt: <none | light on edges | heavy grime>
- Baked lighting: <none (engine lights it) | soft top-light (hand-painted only)>

## Material vocabulary
Use these phrases word for word.
- <material>: <fixed description>
- ...

## Prompt template
- concept_suffix:
  `<style words>, <shape words>, only the colors named for this object, <world> tones, <texture words>, clean surfaces, single object only, no extra props or decorations, no base, no pedestal, no ground, centered, full object in frame, three-quarter view from slightly above, plain light grey background, even soft lighting, no shadow, no text`
- model_suffix:
  `<style words>, <shape words>, only the colors named for this object, <world> tones, <texture words>, single object, no base`
- Colors live in the subject line (from the material vocabulary), never as a full palette list in a suffix.
- Subject line pattern: `<object>, <key material from vocabulary>, <one distinguishing feature>`

## Banned words
<list>

## Approved references
| What | jobId | URL |
|---|---|---|
| style test 1 | | |
| style test 2 | | |
| style test 3 | | |
| user reference upload | | |

## Naming
- Asset id pattern: `<prefix>_<object>_<variant letter>` (e.g. `dng_barrel_a`), snake_case, unique
- Variant suffix: `__<variant>` (e.g. `dng_barrel_a__rusty`)

## Change log
- <date>: created
