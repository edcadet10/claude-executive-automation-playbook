"""Exercise discovery, a valid call and an out-of-scope call on a real stdio session."""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from lab.report import ENTITY, PERIOD


async def check():
    params = StdioServerParameters(command=sys.executable, args=["-m", "lab.mcp_server"])
    async with stdio_client(params) as (reader, writer), ClientSession(reader, writer) as session:
        await session.initialize()
        tools = await session.list_tools()
        assert [tool.name for tool in tools.tools] == ["get_reporting_packet"]
        valid = await session.call_tool("get_reporting_packet", {"entity": ENTITY, "period": PERIOD})
        assert not valid.isError
        packet = json.loads(valid.content[0].text)
        assert packet["gross_margin_pct"] == "17.00" and len(packet["sources"]) == 3
        for entity, period in [("south-store", PERIOD), (ENTITY, "2026-08")]:
            denied = await session.call_tool("get_reporting_packet", {"entity": entity, "period": period})
            assert denied.isError and "outside" in denied.content[0].text
        print("MCP verified: one tool discovered, valid packet reconciled, foreign store and period rejected.")


if __name__ == "__main__":
    asyncio.run(check())
