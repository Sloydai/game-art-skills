---
name: concept-artist
description: Use when a game asset needs a 2D concept before (or instead of) 3D. This covers concept sheets, prop or character designs, variation boards, turnaround views for multi-view 3D, "show me options for X", fixing or iterating a concept ("make the lid gold", "less clutter"), and preparing clean images that Sloyd's image-to-3D can read. Uses generate_image and edit_image under the locked style-bible.md. Do not use for final 3D models (modeler) or texture variants of an existing model (look-dev).
---

# Concept Artist: designs that survive the trip to 3D

Concept art in this pipeline has two jobs, and each needs different framing:

- **Exploration boards** for humans: options to choose between, wide aspect ratios, several ideas.
  Never fed to 3D.
- **3D input sheets** for `generate_3d_from_image`: one object, read cleanly by the
  reconstruction model. Most of the value of this skill is producing these reliably.

Read `style-bible.md` first. Use its `genStyleId`, `concept_suffix`, palette words and material
vocabulary on every call. If there is no bible, run art-director first.

## 3D input sheet rules

Image-to-3D reconstructs what it sees. Anything ambiguous in the image becomes geometry.

- **One object.** No props beside it, no floor, no pedestal (unless the pedestal is the asset).
- **Whole object in frame** with roughly 10% margin. A cropped handle becomes a flat cut.
- **Three-quarter view from slightly above** (about 20 to 30 degrees). This shows the front,
  one side and the top, which gives the reconstruction the most information. Use a straight
  front view only for flat things such as signs, doors or shields.
- **Plain light grey or white background, even soft light, no cast shadow.** Shadows and
  gradients get read as surfaces.
- **No text, labels, UI, watermarks or arrows.** Callout sheets with annotations are for humans
  only.
- **Neutral pose for characters** (`tPose: true` if it will be rigged), arms clear of the body.
- **Square** (`aspectRatio: "1:1"`). The 3D paths assume square input.
- **Material read.** Surfaces should look like the bible's materials, because image-to-3D
  textures from the image.

The bible's `concept_suffix` already carries most of this. Do not remove its framing words.

## Workflow

1. **Write the subject line**: `<object>, <material from vocabulary>, <one distinguishing
   feature>`. Example: `treasure chest, warm oak brown planks with wrought iron bands, domed lid
   with a skull lock`. One distinguishing feature beats five. Extra features turn into noise at
   game scale.
2. **Generate**: `generate_image` with `prompt: "<subject>, <concept_suffix>"`, the bible's
   `genStyleId` and `aspectRatio: "1:1"`. 10 credits. Poll `get_job` with `wait: 30`; the image
   is `outputs.imageUrl`.
3. **Review** against the checklist below. Show the user the image URL when they are involved.
4. **Fix with edit_image, one change per edit.** For example `edit_image {jobId, prompt: "remove
   the floor shadow, keep everything else identical", genStyleId}` (15 credits). Stacking
   several changes in one edit drifts the design. If two edits have not fixed it, regenerate
   with a better subject line (10 credits) instead.
5. **Hand off** the final image `jobId`. The modeler passes it straight to
   `generate_3d_from_image` as `imageJobId`, with no download or upload needed.

## Review checklist (reject and fix if any fail)

- [ ] Single object, fully in frame, centered
- [ ] Background plain; no ground plane, no cast shadow
- [ ] Palette matches the bible (compare with `Approved references`)
- [ ] Shape language and proportions match the style test images
- [ ] No banned-word effects (sudden realism, micro-detail, dramatic lighting)
- [ ] Readable silhouette: would you recognize it as a black shape at 64 px?
- [ ] Nothing thin and floating (chains, ropes, cobwebs). These reconstruct poorly; keep them
      chunky or drop them

## Turnarounds for multi-view 3D

For hero assets and characters where the back matters, `generate_3d_from_images` gives better
geometry than a single image. Produce views from the approved front concept with `edit_image`.

- prompt `"same object, identical design, materials and colors, viewed from its left side,
  orthographic, same framing and background"`
- repeat for `back` (and `right` if the object is asymmetric)

Check the views agree. The same number of bands, the same lock and the same proportions should
appear in every view. Inconsistent views produce worse geometry than one good front image. If
they disagree after one retry, fall back to single-image 3D. The modeler needs the image URLs
(`outputs.imageUrl`) for multi-view input.

Cost: front 10, plus 15 per extra view.

## Exploration boards

When the user wants options, use `aspectRatio: "16:9"` and ask for 3 to 4 variations
side by side: `"concept sheet, four variations of a <subject> side by side, <style words>, plain
background"`. After the user picks one, regenerate it as a clean 1:1 3D input sheet. Never feed
the board itself to 3D.

## Identity references

To keep a recurring character or object recognizable across sheets, `upload_image` the approved
image (free) and pass its `jobId` as `referenceImageJobId` to `generate_image`. It must be an
upload job owned by the same key.

More prompt patterns for common prop families are in
[references/prompt-patterns.md](references/prompt-patterns.md).
