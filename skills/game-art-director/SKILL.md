---
name: game-art-director
description: Use when the user asks for game art end to end in one request. Examples are "make 40 props for my low-poly dungeon", "build an asset pack for my game", "I need all the art for a cozy farm level", "give my Godot game a prop library" or "be my art department". Orchestrates the whole Game Art Department with Sloyd (style bible, concepts, models, variants, modular pieces, engine export) and ends with a finished, engine-ready pack folder. For a single asset or one step, use the specific role skill instead.
---

# Game Art Director: one prompt to a finished pack

You run a small art department: art-director, concept-artist, modeler, look-dev,
asset-pack-builder, kitbasher, engine-export, with sloyd-api as shared plumbing. Your job is
sequencing, gates and budget. Each role's skill holds the craft. Load it when its stage starts
and follow it.

The deliverable is a folder the developer can drop into their engine:

```
art/<pack>/
  style-bible.md       locked look (art-director)
  plan.json            asset list and routes (asset-pack-builder)
  manifest.json        every asset, jobId, URL, file, export record
  concepts/            2D sheets (concept-artist)
  models/              base GLBs (modeler / asset-pack-builder)
  variants/            retextures (look-dev)
  parts/               split results (kitbasher)
  export/<engine>/     normalized, named GLBs + IMPORT.md (engine-export)
  gallery.html         3D preview of the whole pack
  README.md            what is in the pack, how to import, credits used
```

## Stage 0: Preflight (sloyd-api)

- Check that `SLOYD_CLIENT_ID` and `SLOYD_CLIENT_SECRET` are set, without printing them. If
  either is missing, give the user the key setup steps from sloyd-api and stop.
- Call `get_credit_balance`. If it is 0, say so now, before any planning effort is wasted.
- Pick transport: Sloyd MCP tools if connected, otherwise `${CLAUDE_PLUGIN_ROOT}/skills/sloyd-api/scripts/sloyd.py`.

## Stage 1: Brief

Extract from the prompt:

- genre and setting
- asset count and type
- engine
- camera
- platform
- references
- budget

Ask at most three questions, and only about what changes the outcome, usually engine, camera
and budget. If the user said "just go", infer, write the assumptions into the bible, and
continue. Default engine: none (export for all four on request). Default count for "a pack":
24.

## Stage 2: Style bible (art-director). Gate 1.

Write `style-bible.md` and run the 3-image style test (about 30 credits). Show the three test
images and the locked settings in a few lines.

**Gate 1:** the user approves the look, or has pre-approved ("use your judgment"). Never start
the batch on an untested bible. A bad bible multiplies across every asset.

## Stage 3: Pack plan and price (asset-pack-builder). Gate 2.

Plan the asset list by level-design coverage (structure, furniture, containers and loot, light,
hazards, clutter and organic), with the size mix, routes, heights, and variants planned as
retextures. Write `plan.json`. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/asset-pack-builder/scripts/run_pack.py art/<pack>/plan.json --estimate`. Show:

- the list grouped by category, one line each
- total credits, dollars, reroll reserve, current balance, and balance after the run

**Gate 2:** an explicit yes to the spend, unless the user pre-approved a budget that covers it.
If the balance is short, offer a smaller first batch, the critical assets first.

## Stage 4: Production

Run the same command with `--yes` instead of `--estimate`. It handles concepts, models, variants and splits with at most 5
concurrent jobs, resumable state and 402/429 handling.

While it runs, give brief progress updates (every ~10 assets), not a running commentary. If it
stops on 402, report the shortfall and how to resume (the same command after topping up).

Hero assets needing multi-view (`views` route) or bespoke concepts go through concept-artist
and modeler directly, then into `manifest.json` in the same schema.

## Stage 5: Review as a set

Build `gallery.html` and review the whole pack side by side with the asset-pack-builder QA
checklist (palette, detail level, silhouettes, budgets). Fix outliers within the reroll reserve:

- **Texture issues:** look-dev retexture.
- **Shape issues:** new subject line plus a reset stage.
- **Two failed rerolls on one asset:** drop it or change its route. Do not burn credits.

## Stage 6: Variants and pieces

Only what the brief asked for, or what the plan already priced:

- **look-dev:** material, team or rarity variants.
- **kitbasher:** destructible splits or modular parts.

## Stage 7: Engine export

Run engine-export for the user's engine (`glb_tool.py export --engine <engine>`). Read the
engine reference for the import notes. Copy any warnings into the pack README.

## Stage 8: Deliver

Write `art/<pack>/README.md` covering:

- the pack title and style summary (genStyleId, palette, budgets)
- an asset table: id, name, category, triangles, variants
- how to preview (`python3 -m http.server`, then `gallery.html`) and how to import (link
  `export/<engine>/IMPORT.md`)
- credits used, balance remaining, and failed or dropped assets with the reason

Then tell the user in a short summary:

- assets done / planned
- credits used and remaining
- the folder path and the one thing they should do next (usually "copy `export/godot/` into
  `res://art/` and open `gallery.html`")

## Budget discipline

- Every paid step is priced before it runs, and the user hears the number.
- Keep spend at or below plan + reserve. Ask before exceeding it.
- Never resubmit a job that has a saved `jobId` in flight. Resume it.
- Credentials stay in the environment. Never write them to any file in the pack.
