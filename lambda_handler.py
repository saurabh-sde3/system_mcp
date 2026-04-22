"""AWS Lambda entrypoint for the FastMCP Streamable HTTP app."""

from mangum import Mangum

from server import create_mcp


def handler(event, context):
    # Mangum runs ASGI lifespan per Lambda invocation; FastMCP's streamable HTTP
    # session manager is single-use, so create a fresh stateless app each time.
    asgi_app = create_mcp().streamable_http_app()
    return Mangum(asgi_app)(event, context)
