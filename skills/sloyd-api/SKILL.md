---
name: sloyd-api
description: Use first, before any other Game Art Department skill calls Sloyd, and whenever the user needs to connect Sloyd, set or fix SLOYD_CLIENT_ID / SLOYD_CLIENT_SECRET, check their credit balance, estimate what a generation will cost, poll a jobId, download a GLB or image, or recover from a 401, 402 (insufficient credits) or 429 (5 concurrent jobs) error. Also use when the agent has no MCP support and must call Sloyd over plain HTTP or curl.
---

# Sloyd API: connection, credits and the job loop

Every role in the Game Art Department (art-director, concept-artist, modeler, look-dev,
asset-pack-builder, kitbasher, engine-export) spends real credits through this API. This skill
is the shared contract: how to connect, how to price a request before running it, how to run a
job to completion, and what to do when it fails. Source of truth: the Sloyd API docs
(api-dashboard.sloyd.ai) and the live tool schemas on the MCP server. Never invent a tool or a
parameter that is not listed here or returned by `tools/list`.

## 1. Credentials: every user brings their own

Each user creates their own key. Generations are billed to that user's prepaid credits.

1. Sign in at https://api-dashboard.sloyd.ai, open **API Keys**, click **Generate Key**.
2. Copy the client secret immediately. It is shown once and cannot be retrieved later.
3. Buy credits under **Usage & Billing** (minimum $12 = 900 credits). A key with 0 credits
   authenticates but every paid call returns 402.
4. Export the pair in the shell that launches the agent:

```bash
export SLOYD_CLIENT_ID="sok_live_..."
export SLOYD_CLIENT_SECRET="..."
```

Rules for the agent:

- Read credentials only from `SLOYD_CLIENT_ID` and `SLOYD_CLIENT_SECRET` (or a git-ignored
  `.env` in the project). Never ask the user to paste a secret into chat, never write it into
  a tracked file, a manifest, a log or a commit, and never echo it back.
- If either variable is missing, stop and give the user the four steps above. Do not try to
  generate anything without them.
- To check without printing anything secret: `[ -n "$SLOYD_CLIENT_ID" ] && echo set`.

## 2. Connect

**Claude Code (MCP, preferred).** This plugin ships a `.mcp.json` that registers the hosted
server with `${SLOYD_CLIENT_ID}` / `${SLOYD_CLIENT_SECRET}` from the environment, so installing
the plugin is enough once the variables are exported before `claude` starts. To add it by hand:

```bash
claude mcp add --transport http sloyd https://api.sloyd.ai/api/mcp \
  --header "x-client-id: $SLOYD_CLIENT_ID" \
  --header "x-client-secret: $SLOYD_CLIENT_SECRET"
```

Other clients (Cursor, VS Code, Claude Desktop via `mcp-remote`, Messages API, Responses API):
see [references/clients.md](references/clients.md).

**No MCP? Use the bundled client or curl.** `${CLAUDE_PLUGIN_ROOT}/skills/sloyd-api/scripts/sloyd.py` calls the same MCP tools over
plain HTTPS with the standard library only. It works in any agent that can run a shell.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sloyd-api/scripts/sloyd.py check                                   # credentials + balance
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sloyd-api/scripts/sloyd.py styles                                  # genStyleId list
python3 ${CLAUDE_PLUGIN_ROOT}/skills/sloyd-api/scripts/sloyd.py run generate_3d_from_text '{"prompt":"wooden barrel"}'
```

The REST equivalents with curl are in [references/rest-fallback.md](references/rest-fallback.md).

**Script paths.** Commands in these skills use `${CLAUDE_PLUGIN_ROOT}/skills/...`. Claude Code
replaces that with the plugin's install folder. In other agents, replace it with the folder this
repository was cloned or installed into. All scripts are Python 3.9+ with the standard library
only. Run them from the user's project folder, because outputs go to paths you pass in.

## 3. Tools (the complete list)

| Tool | Use it for | Credits |
|---|---|---|
| `generate_3d_from_text` | GLB from a prompt. Args: `prompt`, `genStyleId`, `topology` (auto/quads/triangles), `targetFaceCount` (0 to 500000), `textureResolution` (128 to 4k, auto, none), `tPose` | 25 textured, 15 with `textureResolution:"none"`, +5 quads |
| `generate_3d_from_image` | GLB from one image. Args: `file` {url or base64+mimeType} or `imageJobId` (an `upload_image` or `generate_image` job), plus `topology`, `targetFaceCount`, `textureResolution` | 20 textured, 10 untextured, +5 quads |
| `generate_3d_from_images` | GLB from views. Args: `frontImage` plus at least one of `leftImage`/`backImage`/`rightImage`, `FaceCount` (numeric string), `EnablePBR` ("true"/"false" string) | 40 textured (estimate), 30 untextured |
| `upload_image` | Upload once, reuse the `jobId` as `imageJobId` / `referenceImageJobId` | free |
| `generate_image` | 2D image. Args: `prompt`, `genStyleId`, `aspectRatio` (1:1, 4:3, 3:4, 3:2, 2:3, 16:9, 9:16), `referenceImageJobId`, `tPose` | 10 |
| `edit_image` | Edit an image job. Args: `jobId`, `prompt`, `genStyleId` | 15 |
| `generate_skybox` | 360 skybox. Args: `prompt`, `genStyleId` | 25 |
| `generate_skybox_from_image` | Skybox from an uploaded image. Args: `imageJobId`, `prompt`, `genStyleId` | 25 |
| `edit_skybox` | Edit a skybox job. Args: `jobId`, `prompt`, `genStyleId` | 25 (estimate) |
| `retexture_model` | New texture on a model job you own. Args: `jobId`, `prompt`, `textureResolution` (default 2k) | 15 |
| `split_model_into_parts` | Split a model job. Args: `jobId`, `method` (partition/decomposition), `numberOfParts` (4 to 16, partition only), `attachmentPoints` (partition only) | 40 |
| `get_job` | Status and outputs. Args: `jobId`, `wait` (0 to 30) | free |
| `get_credit_balance` | Remaining prepaid credits | free |
| `get_generation_styles` | Built-in `genStyleId` values | free |

Prices come from https://www.sloyd.ai/api/pricing (1 USD = 75 credits) and were confirmed against
live 402 responses for text-to-3D, image generation and image edit. Values marked "estimate"
follow the published formula. Texture-free and quads options change 3D prices; a target face
count of 500K or more adds 10. When an estimate and a 402 disagree, the 402 `required` value wins.

`multi-image` gotcha: `EnablePBR` is a string and defaults to geometry only. Send `"true"` when
you want textures.

## 4. Spend safely

Before any paid call or batch:

1. Call `get_credit_balance`.
2. Price the whole plan with the table above (or `python3 ${CLAUDE_PLUGIN_ROOT}/skills/sloyd-api/scripts/sloyd.py call ...` which prints
   the estimate). Include rerolls: budget about 15% extra for a pack.
3. Tell the user the total, the balance, and what is left after the run, in one line, for example
   `This pack costs about 1,090 credits (~$14.50). Balance: 1,500. Remaining after: ~410.`
4. Wait for a yes unless the user already approved a budget that covers it.

Credits are charged when a job starts and refunded automatically if the job fails.

## 5. The job loop

1. A generation tool returns `{ "jobId": "..." }` immediately.
2. Call `get_job` with `{ "jobId": "...", "wait": 30 }`. Each call blocks up to 30 seconds.
   Repeat until `done` is `true`. Jobs take one to several minutes; split takes about 2.5 to 4.
3. On `status: "success"`, read `outputs`:
   - `outputs.glbUrl` for 3D models (also `https://storage.googleapis.com/ai-services-quality/jobs/{jobId}.glb`)
   - `outputs.imageUrl` for images
   - `outputs.panoramaUrl` and `outputs.cubemapFaceUrls` for skyboxes
4. On `status: "error"`, read `errorMessage`. Credits were refunded. Retry once with the same
   arguments; if it fails again, change the input (simpler prompt, cleaner image) instead of
   retrying blindly.
5. Write every `jobId` down (manifest, notes) the moment you get it. There is no list-jobs
   endpoint, and a lost id means a paid result you cannot find. On resume, poll the saved id
   instead of starting a new job.

Output URLs are public. Download files you want to keep into the project.

## 6. Errors

| Status | Meaning | What to do |
|---|---|---|
| 401 | Missing or wrong credentials | Re-check the two env vars; a revoked key fails immediately |
| 402 | Not enough credits. Body has `required` and `available` | Stop launching new jobs. Tell the user the shortfall and the dashboard link. Nothing was charged; the same call can be retried after a top-up |
| 403 | Not your job (e.g. retexturing someone else's model) | Use a jobId this key created, or upload the GLB |
| 422 | Bad field (enum, range, missing image) | Fix the argument; nothing was charged |
| 429 | 5 jobs already pending or running on this key (includes jobs from other tools or teammates on the same key) | Wait for a running job to finish, then retry. Never fire a 6th job in parallel |
| 500 | Server error | Retry with backoff; report the jobId if it persists |

Over MCP, these arrive as tool errors whose text contains the status code (for example
`Sloyd API error 402: Insufficient API credits ...`). The bundled client maps them to
`CreditsError`, `BusyError` and `AuthError`.

## 7. Concurrency

At most 5 jobs per key can be pending or running. Keep a hard cap of 5 in-flight jobs in any
batch, and treat 429 as "slot not free yet", not as a failure. If the user runs other Sloyd work
on the same key at the same time, lower your cap. `asset-pack-builder` implements this for
batches; for one-off calls, start up to 5 and poll them in turn.
