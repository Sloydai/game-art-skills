# Launch tweet: Game Art Department

Every number and image below comes from the real run in
[`examples/low-poly-dungeon/`](examples/low-poly-dungeon/), made on 2026-11-04 against the live
Sloyd API. Source of each claim: `run-record.json` (spend, rerolls) and `images/` (renders of the
actual GLBs).

## Main post

```
I gave Claude a full 3D art department.

40 game-ready props. One locked style. 29 minutes. $20 of API credits.

[[video: 35s demo, shot list below]]
```

Attach `examples/low-poly-dungeon/images/contact-sheet.png` if the video is not ready.

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

So the art director tests the style on 3 props before spending on 40.

The first test failed: every prop got every palette color, plus a pedestal. It fixed the bible, retested, then ran the pack.
```

Image: the two style-test rounds side by side (`style-test/` plus the rejected job URLs in
`style-bible.md`).

**4/ The receipt**

```
40 props + 5 variants + a destructible barrel.
1,495 credits (~$20), 29 minutes, 5 jobs at a time, 0 failed jobs.
It caught 4 weak models in review and rerolled them.
Every asset ships with its jobId, triangle count and engine-ready file.
```

Image: `images/variants-sheet.png` (gold and rusty chest, mossy door, mana potion, frozen barrel).

**5/ Install**

```
/plugin marketplace add Sloydai/game-art-skills
/plugin install game-art@sloyd-game-art

Bring your own Sloyd API key.
github.com/Sloydai/game-art-skills
```

## Alternate hooks

1. `Most AI asset packs look like 40 different games. So I gave Claude an art director first.`
2. `Claude just made every prop in my dungeon. 40 GLBs, one style, $20 in API credits.`

## About "one prompt"

The launch pack was produced by these skills' pipeline. In this session the agent drove it in
stages: style tests, a 2-asset pilot, then the batch. Before posting "from one prompt", record a
clean run in Claude Code where a single message ("Make 40 props for my low-poly dungeon in
Godot") triggers `game-art-director`, and use that recording for shots 2 to 5. Until then, use
the main post as written above, which makes no one-prompt claim.

## Demo video shot list (about 35 seconds, record 16:9 and 9:16)

All footage is real screen capture of this plugin and its output. Use Poppins and the Sloyd
palette for overlays and the end card: navy `#0b1833` background, white text, CTA gradient
`#45bcff → #03f584` with `#021225` text.

| # | Time | Shot | Source |
|---|---|---|---|
| 1 | 0 to 3 s | Cold open on the result: slow fly-through of a torch-lit Godot dungeon dressed with the 40 props | Godot scene built from `export/godot/` |
| 2 | 3 to 6 s | The prompt typed into Claude Code: "Make 40 props for my low-poly dungeon in Godot" | Terminal capture |
| 3 | 6 to 10 s | `style-bible.md` scrolls; test 1 (rejected) flips to test 2 (approved) | `style-test/` + rejected URLs |
| 4 | 10 to 13 s | Plan grouped by category, cost estimate, the user types "yes" | `run_pack.py --estimate` output |
| 5 | 13 to 20 s | Timelapse: models appearing while the log shows 5 jobs in flight; counter 0 → 40 | Screen recording, sped up |
| 6 | 20 to 24 s | Hero frame: the 40-prop contact sheet | `images/contact-sheet.png` |
| 7 | 24 to 27 s | Look-dev: the chest swaps base → gold → rusty | `gallery.html` variant buttons (local, from your own run) |
| 8 | 27 to 30 s | Kitbasher: the barrel shatters into its 5 split pieces in Godot | `export/kit/` parts + rigid bodies |
| 9 | 30 to 33 s | Engine export: `export/godot/` dropped into `res://`; props land at the right size on the floor | Godot FileSystem dock |
| 10 | 33 to 36 s | End card: folder tree, install line, `github.com/Sloydai/game-art-skills`, Sloyd logo | Static card |

Capture notes:

- Record at 60 fps, with the same Godot lighting for shots 1, 8 and 9.
- Keep the terminal font large (18 pt or more) so text reads on mobile.
- The fly-through in shot 1 is what stops the scroll. Spend the most time on it.
- The barrel's partition split made 5 horizontal slices along its bands. That reads well as
  "staves fall apart", less well as a shatter. If the shot needs more drama, run kitbasher on the
  barrel with `numberOfParts: 10` (40 credits) before recording.

## Proof checklist before posting

- [x] `run-record.json` shows `done: 40` and `spend.credits: 1495`, matching tweet 4
- [x] The contact sheet is a render of that run's actual GLBs (`render_sheet.mjs`)
- [x] Every exported GLB passes the Khronos glTF validator with 0 errors
- [ ] Godot scene for the video built only from that run's `export/godot/`
- [ ] Clean single-prompt recording in Claude Code (needed before any "one prompt" claim)
- [ ] Repo public and both install lines tested from a clean Claude Code
