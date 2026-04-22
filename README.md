# system_mcp

Simple Python MCP server that exposes one tool: `get_system_info`.

## What it returns

The tool provides:
- hostname
- OS details (system, release, machine, processor)
- Python runtime details
- CPU logical core count
- memory total (best effort)
- basic environment metadata (user, shell, PATH size)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run locally (stdio transport)

```bash
python server.py
```

This mode is useful for local MCP clients that launch a process directly.

## Deploy to AWS Lambda (HTTP MCP server)

This repo includes:
- `lambda_handler.py` (Lambda entrypoint)
- `template.yaml` (AWS SAM template)
- FastMCP configured for stateless JSON HTTP responses (Lambda friendly)

### Prerequisites

- AWS account + credentials configured (`aws configure` or SSO)
- AWS SAM CLI installed
- Python 3.12 available for SAM build

### Build and deploy

```bash
sam build
sam deploy --guided
```

On first deploy, `--guided` asks for stack settings and saves them in `samconfig.toml`.

After deployment, copy the `FunctionUrl` output.

### MCP endpoint URL

FastMCP exposes streamable HTTP at `/mcp`, so your final endpoint is:

```text
https://<function-id>.lambda-url.<region>.on.aws/mcp
```

## MCP client config for remote HTTP

Use this shape in clients that support remote MCP over streamable HTTP:

```json
{
  "mcpServers": {
    "system-info": {
      "url": "https://<function-id>.lambda-url.<region>.on.aws/mcp"
    }
  }
}
```

## Optional: local HTTP run (without Lambda)

If you want to test the same HTTP app locally:

```bash
uvicorn lambda_handler:asgi_app --host 127.0.0.1 --port 8000
```

Then point your MCP client to `http://127.0.0.1:8000/mcp`.
