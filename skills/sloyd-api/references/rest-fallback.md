# REST fallback (curl)

For agents or scripts with no MCP client. Base URL `https://api.sloyd.ai/api`. Every request
sends both headers. Each MCP tool maps to one endpoint and takes the same fields and price.

```bash
H=(-H "x-client-id: $SLOYD_CLIENT_ID" -H "x-client-secret: $SLOYD_CLIENT_SECRET")
```

| MCP tool | REST endpoint | Body |
|---|---|---|
| `generate_3d_from_text` | `POST /jobs/text-to-3d` | JSON |
| `generate_3d_from_image` | `POST /jobs/image-to-3d` | multipart (`file` or `imageJobId`) |
| `generate_3d_from_images` | `POST /jobs/multi-image-to-3d` | multipart (`frontImage`, `leftImage`, `backImage`, `rightImage`) |
| `upload_image` | `POST /jobs/image-upload` | multipart (`file`) |
| `generate_image` | `POST /jobs/text-to-image` | JSON |
| `edit_image` | `POST /jobs/image-edit` | JSON |
| `generate_skybox` | `POST /jobs/text-to-worldbox` | JSON |
| `generate_skybox_from_image` | `POST /jobs/skybox-from-image` | JSON |
| `edit_skybox` | `POST /jobs/skybox-edit` | JSON |
| `retexture_model` | `POST /jobs/retexture` | JSON |
| `split_model_into_parts` | `POST /jobs/split-to-parts` | JSON |
| (no MCP tool) | `POST /jobs/upload-3d` | multipart (`file`: GLB, OBJ, FBX, STL, BLEND, PLY, USDC, USDA up to 500 MB). Free. Returns a `jobId` you own, ready for retexture or split |
| `get_job` | `GET /jobs/{jobId}` | |
| `get_credit_balance` | `GET /user/api-access/balance` | |

## Examples

```bash
# Balance
curl -s https://api.sloyd.ai/api/user/api-access/balance "${H[@]}"

# Text to 3D
curl -s https://api.sloyd.ai/api/jobs/text-to-3d "${H[@]}" -H "Content-Type: application/json" \
  -d '{"prompt":"low-poly wooden barrel with iron bands","genStyleId":"Polygonal","topology":"triangles","targetFaceCount":3000,"textureResolution":"1k"}'

# Image to 3D from a local concept
curl -s https://api.sloyd.ai/api/jobs/image-to-3d "${H[@]}" -F "file=@concepts/barrel.png" -F "targetFaceCount=3000"

# Image to 3D from an earlier image job (no re-upload)
curl -s https://api.sloyd.ai/api/jobs/image-to-3d "${H[@]}" -F "imageJobId=JOB_ID"

# Multi-view, textured (EnablePBR is a string)
curl -s https://api.sloyd.ai/api/jobs/multi-image-to-3d "${H[@]}" \
  -F "frontImage=@front.png" -F "leftImage=@left.png" -F "backImage=@back.png" -F "EnablePBR=true"

# Retexture and split a model job
curl -s https://api.sloyd.ai/api/jobs/retexture "${H[@]}" -H "Content-Type: application/json" \
  -d '{"jobId":"JOB_ID","prompt":"oxidized iron, orange rust in the crevices"}'
curl -s https://api.sloyd.ai/api/jobs/split-to-parts "${H[@]}" -H "Content-Type: application/json" \
  -d '{"jobId":"JOB_ID","method":"partition","numberOfParts":6}'

# Poll (REST has no wait parameter: poll every 5 to 10 seconds)
curl -s https://api.sloyd.ai/api/jobs/JOB_ID "${H[@]}"

# Download a finished model (public URL, no auth)
curl -o barrel.glb https://storage.googleapis.com/ai-services-quality/jobs/JOB_ID.glb
```

REST `GET /jobs/{jobId}` reports `status` (`pending`, `running`, `success`, `error`) but does
not include the `outputs` block that MCP `get_job` returns. Models are always at the public
`jobs/{jobId}.glb` path. For image and skybox URLs, prefer MCP `get_job` (the bundled
`scripts/sloyd.py wait JOB_ID` does this over plain HTTPS).

Errors use the same status codes as MCP: 401, 402 (`{available, error, message, required}`),
403, 404, 422, 429, 500.
