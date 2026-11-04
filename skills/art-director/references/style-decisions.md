# Style decisions: tables and presets

## Built-in genStyleId values

Always confirm with `get_generation_styles` at run time; the list below was current on
2026-11-04.

| genStyleId | Look | Good for | Watch out |
|---|---|---|---|
| `Auto` | Pipeline picks | One-offs | Not consistent across a pack. Never use for packs |
| `Polygonal` | Flat-shaded facets, limited palette | Low-poly indie, mobile, stylized survival | Pair with `topology: "triangles"` and low face budgets |
| `RetroCRT90s` | PS1/N64, low-res, simple polygons | Retro horror, boomer shooters | Use `textureResolution` 128 to 512 for authenticity |
| `HandpaintedStylized` | Painted textures, warm light, WoW-like | Fantasy RPG, MMO-style | Texture carries the detail, so geometry can stay low |
| `Cartoon` | Exaggerated, vibrant, Pixar-like | Family, party, platformers | Keep proportions consistently exaggerated |
| `CozyMobile` | Soft rounded pastels | Farming, cozy, casual mobile | Low contrast. Give interactables a stronger accent |
| `ClayMorphic` | Matte clay or plasticine | Puzzle, toy-box, claymation | Matte only; metals read as painted clay |
| `StylizedAnime` | Bold simplified anime | Creature collectors, action | |
| `DetailedAnime` | Ornate JRPG | JRPG hero assets | Heavy detail. Raise budgets or keep to heroes |
| `CelShadedComic` | Outlines, flat colors, hard shadows | Comic or graphic games | Outlines are baked in texture. Pair with a toon shader or not at all |
| `PainterlyComic` | Borderlands-like painted comic | Looter shooters | Same as above |
| `Roblox` | Blocky, bright, saturated | Roblox experiences | Respect Roblox's 20k triangle limit |
| `Realistic` | Photoreal | Sims, realistic indie | Biggest file and texture cost |
| `IsometricDiorama` | Miniature tabletop scene on a base | Hero dioramas, level previews | Adds a base or scene. Not for individual props |
| `Color3DPrint` | Four flat colors, hard edges | Printed figurines | Not a game style |
| `Sketch` | Pencil linework | Concept exploration only | Not for final textures |

## Face budgets by style (targetFaceCount)

Starting points for props. Halve for mobile or web, double for PC hero assets. `0` lets Sloyd
pick, which is fine for one-offs but drifts across a pack. Always set a number for packs.

| Style | Small | Medium | Large | Hero |
|---|---|---|---|---|
| Faceted low-poly (`Polygonal`) | 500 to 1,500 | 1,500 to 4,000 | 4,000 to 8,000 | 10,000 |
| Retro PS1 | 300 to 800 | 800 to 2,000 | 2,000 to 4,000 | 6,000 |
| Stylized / hand-painted / toon | 1,500 to 4,000 | 4,000 to 10,000 | 10,000 to 20,000 | 30,000 |
| Realistic | 5,000 to 15,000 | 15,000 to 40,000 | 40,000 to 80,000 | 150,000 |
| Roblox (per MeshPart) | 500 to 2,000 | 2,000 to 6,000 | 6,000 to 15,000 | 20,000 max |

These are faces as passed to `targetFaceCount`. Engines count triangles; a quad mesh is about 2
triangles per face.

## Texture resolution by camera

| Camera / platform | Small prop | Medium | Large / hero |
|---|---|---|---|
| Top-down or isometric, mobile | 256 to 512 | 512 | 1k |
| Third-person, PC | 512 to 1k | 1k | 2k |
| First-person, PC | 1k | 2k | 2k to 4k |

Pick one value for the whole pack unless the hero tier is clearly separate.

## Genre presets

Use as a starting draft, then adjust to the user's references.

**Low-poly dungeon crawler.** `Polygonal`, triangles, 1k.
- Palette: slate grey stone, warm oak brown, wrought iron near-black, torch amber accent, moss
  green, bone ivory.
- Shape: chunky, 1.3x thickness, slightly bevelled.
- Texture: flat color with subtle gradient, light edge wear.
- Camera: isometric or third-person.

**Cozy farming sim.** `CozyMobile`, auto, 1k.
- Palette: butter yellow, sage green, terracotta, cream, sky blue accent.
- Shape: rounded, soft, toy-like 1.5x.
- Texture: smooth gradients, no grime.

**PS1 horror.** `RetroCRT90s`, triangles, 256.
- Palette: desaturated olive, rust brown, sickly yellow, deep red accent.
- Shape: blocky, 1:1 proportions, sharp.
- Texture: low-res noisy, dirty.

**Fantasy RPG (WoW-like).** `HandpaintedStylized`, auto, 2k.
- Palette: royal blue, gold accent, warm stone, deep red, forest green.
- Shape: chunky, oversized hands and weapons (2x).
- Texture: painted highlights on top edges.

**Sci-fi arena (stylized).** `Cartoon` or `PainterlyComic`, quads, 1k.
- Palette: gunmetal, white panels, team color accent, cyan emissive.
- Shape: blocky hard-surface, bevelled panels.

**Roblox obby or simulator.** `Roblox`, auto, 512.
- Palette: saturated primaries.
- Shape: blocky, 1.5x.
- Budget: 20,000 triangles per mesh, at most.

## Palette rules that make packs read well

- Value matters more than hue. Interactable things (doors, chests, levers, loot) should be at
  least one value step away from the surfaces around them.
- Keep saturation in one band across the pack. A single over-saturated prop is the first thing a
  player notices.
- Shift hue in shadows (cooler) and highlights (warmer) only in hand-painted styles. Flat
  styles keep one color per material.
- Reserve the accent color. If every prop has gold trim, nothing reads as loot.
