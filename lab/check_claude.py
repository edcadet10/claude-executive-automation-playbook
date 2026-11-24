"""Optional live Claude Code check. Sends only the fictional packet to the configured model."""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

TOOL = "mcp__fieldbook__get_reporting_packet"
ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    "Call get_reporting_packet exactly once for north-store and 2026-09. "
    "Use its result to draft a short controller brief. Express the margin and floor as percentages, "
    "give the dollar shortfall and open pipeline in dollars, cite all three source IDs verbatim, "
    "and end with one question. If the tool fails, report the blocker."
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--use-login", action="store_true",
                        help="Use the signed-in Claude Code session for this supervised test")
    args = parser.parse_args()
    environment = os.environ.copy()
    runtime = ["--bare"]
    if args.use_login:
        environment.pop("ANTHROPIC_API_KEY", None)
        runtime = ["--setting-sources", "project", "--settings", '{"disableAllHooks":true}']
    command = ["claude", "-p", *runtime, "--model", "haiku", "--strict-mcp-config",
               "--mcp-config", str(ROOT / ".mcp.json"), "--tools", "", "--allowedTools", TOOL,
               "--permission-mode", "dontAsk", "--no-session-persistence", "--max-budget-usd", "0.25",
               "--output-format", "stream-json", "--verbose", PROMPT]
    try:
        run = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, encoding="utf-8",
                             errors="replace", timeout=120, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"Claude check could not finish ({type(exc).__name__}). Verify CLI access and retry.")
        return 2
    events = []
    for line in run.stdout.splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    calls = [item.get("name") for event in events if event.get("type") == "assistant"
             for item in event.get("message", {}).get("content", []) if item.get("type") == "tool_use"]
    final = next((event for event in reversed(events) if event.get("type") == "result"), {})
    if run.returncode or final.get("is_error") or calls != [TOOL]:
        print(f"Claude check held. CLI exit {run.returncode}. Expected tool calls observed: {calls.count(TOOL)}.")
        print("Check CLI authentication, the model alias and the MCP smoke test.")
        return 2
    brief = final.get("result", "")
    normalized = brief.replace(",", "").replace("**", "")
    references = ["CRM-SNAPSHOT-09", "QBO-PL-09", "POL-MARGIN-04"]
    patterns = [r"\b17(?:\.0+)?\s*%", r"\b18(?:\.0+)?\s*%", r"\b2500\b", r"\b60000\b"]
    if not all(ref in brief for ref in references) or not all(re.search(p, normalized) for p in patterns):
        print("Claude called the tool, but its narrative missed a required figure or source ID.")
        return 1
    print(brief)
    print("\nVerified one fieldbook tool call, four displayed figures and three source references.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
