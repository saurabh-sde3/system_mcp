"""Simple MCP server that returns host system information."""

from __future__ import annotations

import os
import platform
import socket
import sys
from datetime import datetime, timezone
from typing import Any, Dict

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings


def _bytes_to_gb(value: int | float) -> float:
    return round(float(value) / (1024**3), 2)


def _memory_info() -> Dict[str, Any]:
    """Best-effort memory information for Unix-like systems."""
    if not hasattr(os, "sysconf"):
        return {"available": False, "reason": "os.sysconf is not supported"}

    names = getattr(os, "sysconf_names", {})
    if "SC_PAGE_SIZE" not in names or "SC_PHYS_PAGES" not in names:
        return {
            "available": False,
            "reason": "Required sysconf keys are not available",
        }

    page_size = os.sysconf("SC_PAGE_SIZE")
    total_pages = os.sysconf("SC_PHYS_PAGES")
    total_bytes = page_size * total_pages
    return {
        "available": True,
        "total_bytes": int(total_bytes),
        "total_gb": _bytes_to_gb(total_bytes),
    }


def get_system_info() -> Dict[str, Any]:
    """Return basic runtime and host system details."""
    uname = platform.uname()
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "hostname": socket.gethostname(),
        "os": {
            "system": uname.system,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "processor": uname.processor,
            "platform": platform.platform(),
        },
        "python": {
            "version": sys.version,
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "cpu": {
            "logical_cores": os.cpu_count(),
        },
        "memory": _memory_info(),
        "environment": {
            "user": os.getenv("USER") or os.getenv("USERNAME"),
            "shell": os.getenv("SHELL"),
            "path_entries": len((os.getenv("PATH") or "").split(os.pathsep)),
        },
    }


def create_mcp() -> FastMCP:
    app = FastMCP(
        "system-info",
        # Lambda/API Gateway works best with stateless request handling.
        stateless_http=True,
        # Force JSON responses instead of long-lived streaming behavior.
        json_response=True,
        transport_security=TransportSecuritySettings(
            enable_dns_rebinding_protection=False,
        ),
    )
    app.tool()(get_system_info)
    return app


mcp = create_mcp()


if __name__ == "__main__":
    mcp.run(transport="stdio")
