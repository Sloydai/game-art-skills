---
name: art-director
description: Use before ANY Sloyd generation for a game (props, characters, environments, packs), and whenever the user describes a game's look ("low-poly dungeon", "cozy farming sim", "PS1 horror", "like Zelda Wind Waker"), asks for a consistent asset set, or when no style-bible.md exists yet in the project. Locks the visual rules (genre, camera, palette, poly style, proportions, texture style, genStyleId, prompt template, budgets) into style-bible.md, runs a cheap style test, and gets sign-off. Also use to update or audit an existing style bible when assets come out inconsistent.
---

# Art Director: lock the style bible first

An asset pack looks like slop when every asset was prompted on its own: five different wood
colors, three levels of detail, one realistic barrel next to a cartoon chest. Real studios avoid
this with a style guide that every artist follows. This skill writes that guide as
`style-bible.md`, tests it for about 30 credits, and makes it binding for every later role.

**Hard rule:** no other Game Art Department skill generates anything until `style-bible.md`
exists and the user has approved it (or explicitly said "skip approval, use your judgment").

## Inputs to gather

Ask at most three questions, and only for what you cannot infer. Infer the rest and state the
assumption in the bible.

1. **Game and camera.** Genre, perspective (top-down, isometric, third-person, first-person,
   side-on) and typical camera distance. Camera distance sets how much detail is visible, which
   sets poly and texture budgets.
2. **Target engine and platform.** Unity, Godot, Unreal, Roblox; mobile, PC, web, console.
3. **References.** Games the user names, screenshots or existing assets. If the user uploads an
   image, run `upload_image` (free) and record the `jobId` in the bible.

## Decide the look

Work through these in order. Each decision constrains the next. Full option tables and genre
presets are in [references/style-decisions.md](references/style-decisions.md).

1. **genStyleId.** Call `get_generation_styles` (free) and choose exactly one built-in style.
   Pass that style on every `generate_image`, `generate_3d_from_text` and `edit_image` call in the
   pack. Custom web-app styles are not available through the API. Never mix styles inside a
   pack. Common mappings:
   - low-poly or faceted: `Polygonal`
   - PS1/N64 retro: `RetroCRT90s`
   - WoW-like painted fantasy: `HandpaintedStylized`
   - cozy or casual mobile: `CozyMobile`
   - toon/Pixar: `Cartoon`
   - comic or Borderlands: `PainterlyComic` or `CelShadedComic`
   - anime: `StylizedAnime` or `DetailedAnime`
   - Roblox games: `Roblox`
   - soft toy look: `ClayMorphic`
   - realistic: `Realistic`

   `IsometricDiorama` builds a whole scene on a base, which suits hero dioramas but not single
   props.
2. **Palette.** 5 to 8 named colors with hex values. Assign roles:
   - 1 to 2 dominant base materials, about 60% of surface area
   - 2 to 3 secondaries, about 30%
   - 1 accent reserved for interactables and loot, about 10%

   Name colors in words as well as hex. Generators follow "warm oak brown" better than "#8a5a3b",
   and the hex is for engine-side tinting and QA. Note the value structure (dark world with light
   interactables, or the reverse). That is what makes props readable in-game.
3. **Shape language and proportions.** Pick one. Chunky with thick edges, ~1.3x real-world
   thickness, reads at distance. Spindly or elegant. Blocky or rounded. Write how exaggerated the
   proportions are (realistic 1:1, stylized 1.2 to 1.5x, toy-like 2x heads/handles). This line goes
   into every prompt.
4. **Poly style and budgets.** Flat-shaded faceted, smooth low-poly, mid-poly stylized or
   realistic. Set `topology` (`triangles` for faceted low-poly, `quads` if artists will edit in a
   DCC, `auto` otherwise). Set `targetFaceCount` per size class (small, medium, large, hero). See
   the budget table in the reference. Budgets must also respect the engine (Roblox: 20,000
   triangles per mesh max).
5. **Texture style.** Flat color, gradient, hand-painted, PBR-stylized or PBR-realistic. Set one
   `textureResolution` for the pack (`512` or `1k` for low-poly mobile props, `1k` to `2k` PC
   props, `2k` hero). Mixed resolutions are the fastest way to make a pack look assembled from
   different sources.
6. **Material vocabulary.** The 6 to 12 materials the world is made of, each with a fixed
   description: "oak: warm brown, wide visible grain, rounded worn edges". Every prompt that
   mentions oak uses those words exactly.
7. **Lighting assumption.** No baked lighting, no baked AO in albedo, unless the style is
   hand-painted (which bakes soft top-light by convention). This prevents double shading in
   engine.
8. **Prompt template.** Assemble decisions 1 to 7 into two fixed suffixes:
   - `concept_suffix` for `generate_image` (adds framing for 3D input, see concept-artist)
   - `model_suffix` for `generate_3d_from_text`

   Each asset varies only its `{subject}` line. Template wording is frozen once the bible is approved.
9. **Banned words.** List words that push the generator off-style. For stylized packs:
   "realistic", "photorealistic", "8k", "highly detailed", "intricate", "cinematic", "dramatic
   lighting", "masterpiece". Also list scene words that create clutter: "on a table", "in a
   room", "with background".

## Write style-bible.md

Copy [references/style-bible-template.md](references/style-bible-template.md) to the project
root of the art folder (default `art/<pack-slug>/style-bible.md`) and fill every field. Keep it
under two screens. Downstream skills read it literally, so write rules, not prose.

## Style test (the gate)

Before the full pack, prove the bible works on three deliberately different subjects:

- one small hand-held prop (for example a potion)
- one large hard-surface prop (for example a wooden cart)
- one organic or irregular prop (for example a mushroom cluster or a rock)

For each: `generate_image` with `{subject}, {concept_suffix}` and the bible's `genStyleId`,
`aspectRatio: "1:1"`. Cost: 3 x 10 = 30 credits. Optionally turn the best one into 3D with
`generate_3d_from_image` (20 credits) to check that the poly style survives.

Show the three images side by side and check:

- Same palette, same edge treatment, same texture style?
- Is each subject alone, centered, uncropped, on a plain background? (Needed for image-to-3D.)
- Would these three sit in the same game screenshot without one looking pasted in?

If they fail, change the bible, not individual prompts, and test again. Record the passing test
jobIds in the bible under `Approved references`. Later concept work uses them as the visual
yardstick.

## Hand-off

Tell the user what was locked, in about five lines: style, palette, budgets, cost of the test,
and the next step. The concept-artist and modeler read `style-bible.md`. The asset-pack-builder
copies `genStyleId`, suffixes and budgets into `plan.json`. If the user later asks for an asset
that breaks the bible (a realistic sword in a toon pack), say so and offer to either adapt the
subject to the bible or start a separate bible.
