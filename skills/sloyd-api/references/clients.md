# Connecting other MCP clients

Server: `https://api.sloyd.ai/api/mcp` (Streamable HTTP). Auth: `x-client-id` and
`x-client-secret` headers, or `Authorization: Bearer <clientId>:<clientSecret>` for clients that
can only send a token. Keep the secret in the client's secret storage or an environment variable,
never in a shared or committed config file.

## Claude Code

```bash
claude mcp add --transport http sloyd https://api.sloyd.ai/api/mcp \
  --header "x-client-id: $SLOYD_CLIENT_ID" \
  --header "x-client-secret: $SLOYD_CLIENT_SECRET"
```

Installing this plugin also registers the server through `.mcp.json`, reading both values from
the environment at startup. Export them before launching `claude`; run `/mcp` to confirm `sloyd`
is connected.

## Cursor

`~/.cursor/mcp.json` (user-level, so the secret stays out of the repo):

```json
{
  "mcpServers": {
    "sloyd": {
      "url": "https://api.sloyd.ai/api/mcp",
      "headers": { "x-client-id": "${env:SLOYD_CLIENT_ID}", "x-client-secret": "${env:SLOYD_CLIENT_SECRET}" }
    }
  }
}
```

## VS Code

`.vscode/mcp.json`. VS Code prompts for the secret once and stores it securely:

```json
{
  "inputs": [{ "type": "promptString", "id": "sloyd-client-secret", "description": "Sloyd API client secret", "password": true }],
  "servers": {
    "sloyd": {
      "type": "http",
      "url": "https://api.sloyd.ai/api/mcp",
      "headers": { "x-client-id": "sok_live_...", "x-client-secret": "${input:sloyd-client-secret}" }
    }
  }
}
```

## Clients that only start local servers (Claude Desktop config file)

```json
{
  "mcpServers": {
    "sloyd": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://api.sloyd.ai/api/mcp", "--header", "Authorization:${SLOYD_AUTH}"],
      "env": { "SLOYD_AUTH": "Bearer sok_live_...:<your secret>" }
    }
  }
}
```

## Anthropic Messages API

```json
{
  "mcp_servers": [{ "type": "url", "url": "https://api.sloyd.ai/api/mcp", "name": "sloyd", "authorization_token": "sok_live_...:<secret>" }],
  "tools": [{ "type": "mcp_toolset", "mcp_server_name": "sloyd" }]
}
```

Send with the `anthropic-beta: mcp-client-2025-11-20` header.

## OpenAI Responses API

```json
{ "tools": [{ "type": "mcp", "server_label": "sloyd", "server_url": "https://api.sloyd.ai/api/mcp", "authorization": "sok_live_...:<secret>" }] }
```

claude.ai and ChatGPT connectors that require OAuth sign-in are not supported yet.

## No MCP at all

Use `scripts/sloyd.py` (standard-library Python over HTTPS) or curl, see `rest-fallback.md`.
