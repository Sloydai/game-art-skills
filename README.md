# Game Art Department

A full 3D art department for your coding agent. Describe your game once and get a consistent,
engine-ready asset pack: a locked style bible, concept sheets, GLB models, material variants,
destructible and modular pieces, and import-ready files for Unity, Godot, Unreal or Roblox.

Built for indie game devs. Powered by the [Sloyd API](https://www.sloyd.ai/api).

![40 low-poly dungeon props made by the Game Art Department skills](examples/low-poly-dungeon/images/contact-sheet.png)

*A real run: 40 props, 5 variants and a destructible barrel in 29 minutes for 1,495 credits (~$20).
[See the pack](examples/low-poly-dungeon/).*

```
/plugin marketplace add Sloydai/game-art-skills
/plugin install game-art@sloyd-game-art
```

## The team

```
game-art/
├── game-art-director     runs the whole pipeline from one prompt, with budget gates
├── art-director          locks style-bible.md before anything is generated (the anti-slop step)
├── concept-artist        concept sheets that survive the trip to 3D
├── modeler               text, image or multi-view to GLB; picks the right route per asset
├── look-dev              rusty, frozen, gold, team-color and rarity variants from one mesh
├── asset-pack-builder    "40 props for my dungeon": batched, resumable runs, manifest.json and gallery.html
├── kitbasher             destructible fragments and modular parts
├── engine-export         scale, pivots, naming, collision and LOD notes for Unity, Godot, Unreal and Roblox
└── sloyd-api             shared plumbing: credentials, credits, job polling, errors, REST fallback
```

Each role hands its output to the next:

1. art-director writes `style-bible.md`
2. concept-artist and modeler read the bible
3. asset-pack-builder turns the bible into `plan.json` and `manifest.json`
4. look-dev and kitbasher add to the manifest
5. engine-export turns the manifest into `export/<engine>/` with an `IMPORT.md`

## What you get

```
art/low-poly-dungeon/
├── style-bible.md        genre, camera, palette, poly style, proportions, genStyleId, prompt template
├── plan.json             40 assets by category, size, height and route
├── manifest.json         every asset: jobIds, URLs, files, triangle counts, export records
├── concepts/  models/  variants/  parts/
├── export/godot/         dng_barrel_a.glb ... + IMPORT.md   (or unity/, unreal/, roblox/)
├── gallery.html          orbit every model in the browser; ?sheet=1 for a contact sheet
└── README.md             pack summary, credits used, how to import
```

## Setup

1. **Get your own Sloyd API key.** Each user brings their own credentials, and generations are
   billed to your prepaid credits.
   1. Go to [api-dashboard.sloyd.ai](https://api-dashboard.sloyd.ai), open **API Keys**, and
      click **Generate Key**. Copy the secret; it is shown once.
   2. Buy credits under **Usage & Billing**. The minimum is $12 for 900 credits.
2. **Export the key** in the shell you start your agent from. Or copy `.env.example` to a
   git-ignored `.env`.

   ```bash
   export SLOYD_CLIENT_ID="sok_live_..."
   export SLOYD_CLIENT_SECRET="..."
   ```

3. **Install the plugin** (above). It registers Sloyd's hosted MCP server
   (`https://api.sloyd.ai/api/mcp`) using those two environment variables. To add the server by
   hand instead:

   ```bash
   claude mcp add --transport http sloyd https://api.sloyd.ai/api/mcp \
     --header "x-client-id: $SLOYD_CLIENT_ID" \
     --header "x-client-secret: $SLOYD_CLIENT_SECRET"
   ```

Other agents (Cursor, VS Code, Codex and others) can load the `skills/` folders directly. Clients
without MCP use the bundled standard-library Python client, or curl
(`skills/sloyd-api/references/rest-fallback.md`). Credentials are only read from the environment
and never written to any file.

## Example prompts

- `Make 40 props for my low-poly dungeon crawler in Godot. Isometric camera, budget 1,500 credits.`
- `Lock a style bible for a cozy farming sim on mobile, then show me three test props.`
- `Turn this sketch into a game-ready GLB for Unity.` (attach an image)
- `Give the treasure chest gold, rusty and frozen variants, plus red and blue team versions.`
- `Make the barrel destructible: split it into 6 pieces and give me the Unreal import steps.`
- `Export the whole pack for Roblox and warn me about anything over the triangle limit.`
- `Drop the chest and the torches into my open Godot scene so I can check the scale.`

## Cost

Sloyd API credits ($1 = 75 credits). The agent always shows the estimate and your balance before
spending.

| Step | Credits |
|---|---|
| Concept image | 10 |
| Image edit | 15 |
| Text to 3D (textured) | 25 |
| Image to 3D (textured) | 20 |
| Retexture variant | 15 |
| Split into parts | 40 |

The launch pack was planned at 1,270 credits (40 props, 5 variants, 1 split). It came in at
1,495 credits (~$20) once style tests, 4 rerolls, a texture fix and a rejected variant were
included. That is 12% over plan, inside the 15% reserve the planner adds. Full breakdown:
[examples/low-poly-dungeon](examples/low-poly-dungeon/README.md).
Current prices: [sloyd.ai/api/pricing](https://www.sloyd.ai/api/pricing).

## Example: low-poly dungeon (40 props)

[`examples/low-poly-dungeon/`](examples/low-poly-dungeon/) is the real output of one run:

- the style bible, including the failed first style test and what changed
- the plan, a run record (settings, triangles, spend, rerolls) and the concept images
- rendered contact sheets and per-engine `IMPORT.md` files
- the 3D models are not included: run the plan with your own Sloyd key to make them

## Requirements

- Python 3.9+ for the helper scripts (standard library only)
- A Sloyd API key with credits
- Optional:
  - Node.js 18+ with Playwright, for rendered thumbnails and contact sheets (`render_sheet.mjs`)
  - Unity's glTFast importer (`com.unity.cloud.gltfast`)
  - the [Sloyd Godot Bridge](https://github.com/Sloydai/sloyd-godot-bridge)
  - `npx gltfpack` for LODs

## Privacy

Prompts and images you send are processed by Sloyd. See the
[Sloyd privacy policy](https://www.sloyd.ai/privacy-policy).

## License

MIT
