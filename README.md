# Game Art Department

[Agent Skills](https://agentskills.io) that give your coding agent a full 3D art department. Describe your game and get a pack of matching, engine-ready 3D models, made with the [Sloyd API](https://www.sloyd.ai/api).

![40 low-poly dungeon props made by the Game Art Department skills](examples/low-poly-dungeon/images/contact-sheet.png)

```sh
npx skills add Sloydai/game-art-skills
```

Works with Claude Code, Codex, Cursor, opencode, Kiro, and GitHub Copilot. You need your own [Sloyd API key](#2-add-your-sloyd-api-key). See [Install](#install) for manual setup.

Made by [Sloyd](https://sloyd.ai). If it saves you a week of modelling, give it a star.

AI is great at making one cool 3D model, and bad at making 40 that look like they belong in the same game: a realistic barrel next to a cartoon chest, five different wood colors, a pedestal nobody asked for under the mushrooms.

These skills work like a small art team. An art director locks the style and tests it on 3 props before anything else is made. Then the team plans the pack, builds it, reviews every model, remakes the weak ones, and exports the result for your engine.

## What it does

1. **Locks the style.** The art director writes `style-bible.md` (palette, poly budget, proportions, one Sloyd style) and tests it on 3 props.
2. **Plans the pack.** It picks a mix of sizes and asset types that a real level needs, then shows you the cost before spending anything.
3. **Builds it.** Concept image first, then 3D, 5 models at a time. It resumes after interruptions and never pays twice.
4. **Reviews the set.** It renders every model, compares them side by side, and remakes the outliers.
5. **Adds variants and parts.** Gold, rusty, frozen or team-color versions from one mesh, and destructible or modular pieces.
6. **Exports for your engine.** Unity, Godot, Unreal or Roblox, at real-world scale, sitting on the floor, with per-engine names and import notes.

| Skill | Role |
|---|---|
| `game-art-director` | Runs the whole pipeline from one request. Start here. |
| `art-director` | Writes and tests the style bible |
| `concept-artist` | Concept images that turn into clean 3D |
| `modeler` | Text, image or multi-view to 3D |
| `look-dev` | Material, team-color and rarity variants |
| `asset-pack-builder` | Batched, resumable pack runs |
| `kitbasher` | Destructible and modular parts |
| `engine-export` | Scale, pivots, naming and import guides per engine |
| `sloyd-api` | Shared setup: API key, credits, job polling, errors |

## Real example

We asked for 40 props for a low-poly dungeon crawler. [See the pack.](examples/low-poly-dungeon/)

- **Result:** 40 props, 5 variants and a destructible barrel in 29 minutes, for 1,495 credits (about $20).
- **The first style test failed.** Every prop got every palette color, and the mushrooms grew a stone pedestal. The art director fixed the rules and retested before making the other 37.
- **Review caught 4 weak models**, which it remade: a blob-shaped boulder, an anvil with no stump, a plain chair and a soft coin stack.

![Variants](examples/low-poly-dungeon/images/variants-sheet.png)

## Install

### 1. Add the skills

With the [`skills` CLI](https://github.com/vercel-labs/skills), in your game project:

```sh
npx skills add Sloydai/game-art-skills
```

Or as a Claude Code plugin, which also connects the Sloyd MCP server for you:

```sh
claude plugin marketplace add Sloydai/game-art-skills
claude plugin install game-art@sloyd-game-art
```

Or copy the folders in [`skills/`](skills/) into your agent's skills directory. Keep all 9 together, because they call each other's scripts.

| Agent | Project-level | User-level |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| opencode | `.opencode/skills/` | `~/.config/opencode/skills/` |
| Kiro | `.kiro/skills/` | `~/.kiro/skills/` |
| GitHub Copilot | `.github/skills/` | |

For example, for Claude Code in the current project:

```sh
git clone --depth 1 https://github.com/Sloydai/game-art-skills.git /tmp/game-art-skills
mkdir -p .claude/skills
cp -r /tmp/game-art-skills/skills/* .claude/skills/
```

### 2. Add your Sloyd API key

Each person uses their own key, and generations are billed to their own credits.

1. Sign in at [api-dashboard.sloyd.ai](https://api-dashboard.sloyd.ai), open **API Keys** and click **Generate Key**. Copy the secret; it is shown once.
2. Buy credits under **Usage & Billing**. The minimum is $12 for 900 credits.
3. Set the key in the terminal you start your agent from:

   ```sh
   export SLOYD_CLIENT_ID="sok_live_..."
   export SLOYD_CLIENT_SECRET="..."
   ```

   On Windows PowerShell: `$env:SLOYD_CLIENT_ID="sok_live_..."` and `$env:SLOYD_CLIENT_SECRET="..."`.

   Or put both lines in a `.env` file in your project (copy [`.env.example`](.env.example)) and make sure `.env` is in your `.gitignore`.

Never paste the secret into chat or commit it.

### 3. Optional: connect the Sloyd MCP server

The skills work without it: they call Sloyd through a bundled Python script (Python 3.9+, no packages needed). If your agent supports MCP, connecting the server lets it call Sloyd tools directly. In Claude Code:

```sh
claude mcp add --transport http sloyd https://api.sloyd.ai/api/mcp \
  --header "x-client-id: $SLOYD_CLIENT_ID" \
  --header "x-client-secret: $SLOYD_CLIENT_SECRET"
```

Configs for Cursor, VS Code and other clients are in [`skills/sloyd-api/references/clients.md`](skills/sloyd-api/references/clients.md).

## Usage

Describe your game to your agent:

> Use game-art-director to make 40 props for my low-poly dungeon crawler in Godot. Isometric camera, budget 1,500 credits.

The agent checks your key and balance, shows you the style test and the cost, and waits for your yes before building the pack. You get a folder like this:

```
art/low-poly-dungeon/
├── style-bible.md        the locked look
├── plan.json             the asset list
├── manifest.json         every asset, job and file
├── concepts/  models/  variants/  parts/
├── export/godot/         engine-ready files + IMPORT.md
└── gallery.html          orbit every model in the browser
```

Other things to ask:

- `Lock a style bible for a cozy farming sim on mobile, then show me three test props.`
- `Turn this sketch into a game-ready model for Unity.` (attach an image)
- `Give the treasure chest gold, rusty and frozen variants.`
- `Make the barrel destructible: split it into 6 pieces.`
- `Export the whole pack for Roblox and warn me about anything over the triangle limit.`

## Cost

Sloyd API credits, at 75 credits per $1. The agent always shows the estimate and your balance before spending.

| Step | Credits |
|---|---|
| Concept image | 10 |
| Image to 3D | 20 |
| Text to 3D | 25 |
| Variant (retexture) | 15 |
| Split into parts | 40 |

A 40-prop pack is about 1,300 to 1,500 credits ($17 to $20), including style tests and rerolls. Current prices: [sloyd.ai/api/pricing](https://www.sloyd.ai/api/pricing).

## Privacy

Prompts and images you send are processed by Sloyd. See the [Sloyd privacy policy](https://www.sloyd.ai/privacy-policy).

## License

[MIT](LICENSE)
