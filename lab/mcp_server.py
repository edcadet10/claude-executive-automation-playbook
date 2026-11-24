"""Serve a single read-only synthetic reporting tool over stdio."""
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from lab.report import ENTITY, PERIOD, SAMPLE, InputError, build_packet, load_snapshot

server = FastMCP("Workflow Fieldbook")


@server.tool(annotations=ToolAnnotations(readOnlyHint=True, idempotentHint=True))
def get_reporting_packet(entity: str, period: str) -> dict:
    """Read the approved dealership packet. The public lab covers north-store, 2026-09."""
    if (entity, period) != (ENTITY, PERIOD):
        raise InputError("Entity or period is outside this server's reporting assignment")
    return build_packet(load_snapshot(SAMPLE), ENTITY, PERIOD)


if __name__ == "__main__":
    server.run(transport="stdio")
