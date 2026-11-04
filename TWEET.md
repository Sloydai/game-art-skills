# Launch tweet: Game Art Department

> **Do not post until the real pack exists.** Every number, image and clip in this thread must
> come from an actual run of this plugin: `examples/low-poly-dungeon/plan.json` run end to end
> through `game-art-director`. Fill the `[[...]]` slots from that run's `manifest.json`,
> `gallery.html` and `export/godot/`. No mockups, no renders of models the team did not make.

## Main post

```
I gave Claude a full 3D art department.

40 game-ready props from one prompt. One locked style, real GLBs, dropped straight into Godot.

[[video: 35s demo, shot list below]]
```

## Thread

**2/ The team**

```
game-art/
├── art-director        locks the style bible first
├── concept-artist      concept sheets
├── modeler             text / image → GLB
├── look-dev            rusty, gold, frozen variants
├── asset-pack-builder  40 props, batched
├── kitbasher           destructible parts
└── engine-export       Unity · Godot · Unreal · Roblox
```

**3/ The anti-slop step**

```
Most AI asset packs look like 40 different games.

Before anything is generated, the art director locks a style bible: palette, poly budget, proportions, one Sloyd style. Then it tests it on 3 props before spending on 40.

[[image: style-bible.md next to the 3 style-test images]]
```

**4/ The receipt**

```
[[40]] props + [[5]] variants + a destructible barrel.
[[1,270]] credits (~$[[17]]) of Sloyd API, [[N]] minutes, 5 jobs at a time.
Every asset ships with its jobId, triangle count and engine-ready file.

[[image: gallery.html?sheet=1 contact sheet of all 40]]
```

**5/ Install**

```
/plugin marketplace add Sloydai/game-art-skills
/plugin install game-art@sloyd-game-art

Bring your own Sloyd API key. Free to install.
github.com/Sloydai/game-art-skills
```

## Alternate hooks

1. `Most AI asset packs look like 40 different games. So I gave Claude an art director first.`
2. `Claude just made every prop in my dungeon. 40 GLBs, one style, $[[17]] in API credits.`

## Demo video shot list (about 35 seconds, record 16:9 and 9:16)

All footage is real screen capture of this plugin and its output. Use Poppins and the Sloyd
palette for overlays and the end card: navy `#0b1833` background, white text, CTA gradient
`#45bcff → #03f584` with `#021225` text.

| # | Time | Shot | Source |
|---|---|---|---|
| 1 | 0 to 3 s | Cold open on the result: slow fly-through of a torch-lit Godot dungeon dressed with the 40 props | Godot scene built from `export/godot/` |
| 2 | 3 to 6 s | The one prompt typed into Claude Code: "Make 40 props for my low-poly dungeon in Godot" | Terminal capture |
| 3 | 6 to 10 s | `style-bible.md` scrolls; the 3 style-test images pop in beside it | Real bible + test images |
| 4 | 10 to 13 s | Plan grouped by category, cost estimate, the user types "yes" | `run_pack.py --estimate` output |
| 5 | 13 to 20 s | Timelapse: `gallery.html` filling with models while the log shows 5 jobs in flight; counter 0 → 40 | Screen recording, sped up |
| 6 | 20 to 24 s | Hero frame: `gallery.html?sheet=1`, all 40 models auto-rotating in one grid | Also export as the tweet 4 image |
| 7 | 24 to 27 s | Look-dev: the chest swaps base → gold → rusty in the gallery | Variant buttons |
| 8 | 27 to 30 s | Kitbasher: the barrel shatters into its 6 split pieces in Godot | Assembled parts + rigid bodies |
| 9 | 30 to 33 s | Engine export: `export/godot/` copied into `res://`; models land at the right size on the floor | Godot FileSystem dock |
| 10 | 33 to 36 s | End card: folder tree, install line, `github.com/Sloydai/game-art-skills`, Sloyd logo | Static card |

Capture notes:

- Record at 60 fps, with the same Godot lighting for shots 1, 8 and 9.
- Keep the terminal font large (18 pt or more) so text reads on mobile.
- The fly-through in shot 1 is what stops the scroll. Spend the most time on it.
- Pull every number shown on screen from that run's `manifest.json`.

## Proof checklist before posting

- [ ] `manifest.json` from the real run shows `done: 40`, and its credits match tweet 4
- [ ] The contact-sheet image is a screenshot of that run's `gallery.html?sheet=1`
- [ ] The Godot scene uses only files from that run's `export/godot/`
- [ ] PR or release notes link the run's GLB URLs
- [ ] The repo is public and both install lines work from a clean Claude Code
