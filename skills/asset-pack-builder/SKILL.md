---
name: asset-pack-builder
description: Use when the user wants many game assets at once, as a set that must match. Examples are "40 props for my low-poly dungeon", "a kit of 20 sci-fi crates and barrels", "fill my farm level with props", "an asset pack for my game" or "batch generate these items". Turns the request into a planned asset list (plan.json), prices it, runs it through Sloyd in batches that respect the 5-concurrent-job limit, resumes after interruptions, and writes manifest.json plus a gallery.html preview. Requires an approved style-bible.md (run art-director first).
---

# Asset Pack Builder: 40 props that belong to the same game

A pack is a design problem before it is a batch job. The difference between a usable pack and 40
random models is the plan: coverage of what a level needs, size and shape variety, and one locked
template. This skill owns that plan, runs it reliably, and produces `manifest.json`, the hand-off
to every later stage.

Prerequisite: `style-bible.md` approved. If it is missing, run art-director first. Never batch
without a style test.

## 1. Plan the list like a level artist

Start from what the player will see, not from a list of nouns. For a room-based game, walk an
imaginary room:

- **Structure dressing** (pillars, arches, doors): large silhouettes that frame a space.
- **Furniture and function** (tables, shelves, beds, workbenches): they tell the player what the
  room was for.
- **Containers and loot** (barrels, crates, chests, urns, coins): interactables. Give them the
  accent color.
- **Light sources** (torches, braziers, lanterns): gameplay-critical, they pull the eye.
- **Hazards and mechanisms** (traps, levers, plates): must read instantly.
- **Clutter and organic** (bones, mushrooms, rocks, scrolls): breaks up repetition and fills edges.

Coverage rules for a pack of N:

- Size mix: about 40% small, 40% medium, 20% large, plus 1 to 3 hero assets. All-medium packs look
  flat in a level.
- No near-duplicates in the base list. "Wooden chair" and "wooden stool" are fine; "barrel" and
  "wooden barrel" are not.
- Plan variants as retextures (look-dev, 15 credits each) instead of extra models wherever only
  the material changes (gold chest, frozen sword, mana potion). The silhouette stays identical and
  it costs about half.
- Avoid assets that reconstruct poorly from images: thin chains, cobwebs, rope bridges, glass
  with liquid you can see through, piles of many small items. Make them chunky ("neat stack of
  coins") or leave them to engine effects.
- Large architecture (walls, floors) that must tile on a grid is a kitbasher or engine-blockout
  job, not a prop. Keep it out of prop packs.

Route per asset (see modeler):

- `concept` (image, then 3D; 30 credits) is the default. It is the most consistent.
- `text` (25 credits) works for simple, iconic filler.
- `image` uses a user-supplied picture.
- `views` uses multi-view hero assets.

Assign `size` so the bible's face budget applies, and `heightM` (vertical bounding-box height in
meters), which engine-export uses to scale.

Asset ids: `<prefix>_<object>_<letter>` in snake_case, e.g. `dng_barrel_a`. Ids are permanent.
Files, manifest entries and engine names all derive from them.

## 2. Write plan.json

Format: [references/plan-and-manifest.md](references/plan-and-manifest.md). Working example (40
dungeon props): `examples/low-poly-dungeon/plan.json` in this repo. Copy the bible's
`genStyleId`, `topology`, `textureResolution`, `concept_suffix`, `model_suffix` and budgets into
`defaults` and `budgets`. Asset entries then hold only the subject line and per-asset choices. If
you are tempted to put style words in a subject line, the bible is incomplete. Fix the bible.

Show the user the list grouped by category (one line per asset) before pricing.

## 3. Price, then get a yes

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/asset-pack-builder/scripts/run_pack.py art/<pack>/plan.json --estimate
```

This prints the cost per tool, the total, a 15% reroll reserve, the live balance and what remains
after the run, and spends nothing. Tell the user, for example: `40 props + 5 variants + 1
destructible split: 1,270 credits (~$16.90) plus ~190 reserve. Balance 1,500.` If the balance is
short, say by how much and link https://api-dashboard.sloyd.ai. Offer a smaller first batch
(`--only id1,id2,...`) or `--allow-partial`.

## 4. Run

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/asset-pack-builder/scripts/run_pack.py art/<pack>/plan.json --yes
```

The runner:

- Keeps at most 5 jobs in flight. Lower this with `--max-concurrent 3` if the same key is busy
  elsewhere. A 429 means wait for a free slot.
- Chains stages per asset: concept, model, variants, split.
- Writes each `jobId` to `manifest.json` the moment it exists. If the run stops (Ctrl-C, crash,
  402), running the same command again resumes polling and never pays twice.
- On 402, it stops starting new jobs, lets running ones finish, and exits with code 2. Top up and
  re-run.
- Retries a failed job once (Sloyd refunds failed jobs), then marks it failed.
- Downloads into `concepts/`, `models/`, `variants/` and `parts/` next to the plan.

The launch pack (40 props, 31 concept route and 9 text route, 5 variants, 1 split) took 29
minutes at 5 in flight, with 0 failed jobs. A concept takes about 30 s, a model about 2 min, a
retexture about 2 min. Check progress with
`python3 -c "import json;print(json.load(open('art/<pack>/manifest.json'))['totals'])"`.

**Without a shell (MCP-only chat client):** follow the same plan by hand. Keep 5 jobs in flight
by starting 5, polling each with `get_job` `wait: 30`, and starting the next stage or asset as
each finishes. Record every jobId in `manifest.json` as you go, in the same schema.

## 5. QA the pack as a set

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/asset-pack-builder/scripts/build_gallery.py art/<pack>/manifest.json
cd art/<pack> && python3 -m http.server 8000      # open http://localhost:8000/gallery.html
```

You (the agent) need to see the models too. Render real thumbnails and contact sheets with
headless Chromium, then open the images:

```bash
npm i playwright && npx playwright install chromium        # once
node ${CLAUDE_PLUGIN_ROOT}/skills/asset-pack-builder/scripts/render_sheet.mjs art/<pack>/manifest.json
```

This writes:
- `thumbs/` with one PNG per model, variant and split
- `contact-sheet.png` with every base model
- `variants-sheet.png` with each base next to its variants

Review those images, not the concept art. The 3D result is what ships.

Review all assets together. Consistency problems only show side by side.

- [ ] One palette across the pack. Flag any asset whose dominant color is off-bible.
- [ ] One level of detail. Flag any asset noticeably busier or smoother than its neighbours.
- [ ] Silhouettes are distinct at thumbnail size (`gallery.html?sheet=1` shows the whole pack).
- [ ] Triangle counts are in budget. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/engine-export/scripts/glb_tool.py inspect
      art/<pack>/models/*.glb`.
- [ ] Failed assets are listed with their error.

Fix the outliers. Use about 15% of the budget for rerolls. The launch pack used 12%:
- 4 rerolls, 3 of them text-route assets
- 1 texture fix
- 1 rejected variant, a thin blade that would not take frost

- **Texture-only problem:** look-dev retexture (15 credits).
- **Shape problem:** edit the asset's subject line (switch a text-route asset to `concept`).
  In `manifest.json`, add the old jobIds to the asset's `rerolls` list with a reason, then set
  its `jobs` to `{}`. Re-run with `--only <id>`. Notes such as `rerolls` and `export` are kept
  across runs.

Recording rerolls is how the pack stays auditable: every credit spent maps to a jobId.

## 6. Hand-off

`manifest.json` (schema in the reference) is the contract. It lists every asset with its id,
category, size, height and jobIds, plus URLs and local files for concept, model, variants and
parts. Pass it to:

- **look-dev**, for more variants (add `variants` to plan entries and re-run; only new stages
  run)
- **kitbasher**, for modular pieces and destructibles
- **engine-export**, which normalizes scale and pivots, names files per engine and writes import
  steps

Report to the user:

- assets done / failed
- credits used and remaining balance
- paths to `manifest.json` and `gallery.html`
