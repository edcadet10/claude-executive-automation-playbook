"""Exercise discovery, a valid call and an out-of-scope call on a real stdio session."""
import argparse
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from lab.report import ENTITY, PERIOD


async def check():
    params = StdioServerParameters(command=sys.executable, args=["-m", "lab.mcp_server"])
    async with stdio_client(params) as (reader, writer), ClientSession(reader, writer) as session:
        await session.initialize()
        tools = await session.list_tools()
        assert [tool.name for tool in tools.tools] == ["get_reporting_packet"]
        arguments = {"entity": ENTITY, "period": PERIOD}
        valid = await session.call_tool("get_reporting_packet", arguments)
        assert not valid.isError
        packet = json.loads(valid.content[0].text)
        assert packet["gross_margin_pct"] == "17.00" and len(packet["sources"]) == 3
        calls = [{"arguments": arguments, "isError": valid.isError, "result": packet}]
        for entity, period in [("south-store", PERIOD), (ENTITY, "2026-08")]:
            arguments = {"entity": entity, "period": period}
            denied = await session.call_tool("get_reporting_packet", arguments)
            assert denied.isError and "outside" in denied.content[0].text
            calls.append({"arguments": arguments, "isError": denied.isError, "result": denied.content[0].text})
        print("MCP verified: one tool discovered, valid packet reconciled, foreign store and period rejected.")
        return {"transport": "stdio", "tool": tools.tools[0].name, "calls": calls}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save", type=Path, help="Save the observed tool calls and their results as JSON")
    args = parser.parse_args()
    evidence = asyncio.run(check())
    if args.save:
        args.save.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8", newline="\n")
