# Teach an advanced Claude workflow

## Set context by entity

For a classic Claude Project, create one private project per permitted business and add a brief containing entity name, authorized sources, reporting calendar, accounting basis, glossary, reviewer and escalation rule. Add the current policy and one accepted, redacted example to project knowledge. In a fresh chat ask for the effective policy and its source. Verify the answer against the document. Record what your plan and project interface actually share between sessions. [Claude Projects](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects)

In Claude Code, open an entity-specific private checkout. Keep stable operating instructions in `CLAUDE.md`, repeatable tasks in skills and changeable facts in dated source records. Use a small, versioned checkpoint with entity, period, last accepted revision, pending decision, owner and next permitted action. Start an empty session and reconstruct the work from the checkpoint. Project context gives the model instructions. The connector identity and server-side bindings enforce access. [Claude Code memory](https://code.claude.com/docs/en/memory) · [Skills](https://code.claude.com/docs/en/skills)

## Connect the local lab

Install Python 3.11+, uv and Claude Code for the technical track. Inspect the repository's `.mcp.json` and `lab/mcp_server.py`. From the checkout root, install the locked dependencies once and run the protocol check.

```sh
uv sync --frozen
uv run --frozen --offline python -m lab.check_mcp
claude --strict-mcp-config --mcp-config .mcp.json
```

In the interactive session, inspect `/mcp`, verify that fieldbook exposes `get_reporting_packet`, and use `/month-end-brief north-store 2026-09`. Review the requested tool call. The skill asks Claude to retrieve the packet, draft a brief, then pass the packet and draft to the tool-free reviewer. Record the actual invocation in the session. If a subagent is unavailable, score the draft manually and record the missing review step. [Claude Code MCP configuration](https://code.claude.com/docs/en/mcp) · [Custom subagents](https://code.claude.com/docs/en/sub-agents)

The public MCP server reads one committed fixture. It accepts an entity and period, opens a fixed path and returns a structured packet. Changing an argument cannot switch credentials or select a different source file. Tool annotations describe behavior. The server's implemented operations and data binding determine what callers can access. The protocol check launches a real process, negotiates a session, lists tools and calls the server with allowed and disallowed inputs. [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) · [MCP transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports)

## Evaluate the model and teach the difference

For a supervised live check with a working Claude login, run `python -m lab.check_claude --use-login`. For a configured Anthropic API key, run `python -m lab.check_claude`. The command uses the selected account, sends the fictional case and sets a $0.25 CLI budget and a two-minute process timeout. It checks the tool invocation, numeric figures and citations. The human reviewer still checks meaning, tone and any causal claims. During publication, the real stdio protocol test passed. The model provider declined authentication for the optional narrative test, so a generated narrative and the skill-to-reviewer conversation remain for a supervised run.

| Round | Executive drives | Jeff checks |
| --- | --- | --- |
| Baseline | Ask “How did the store do?” Save the output verbatim in the private workpaper. | Which facts have evidence? Is scope clear? Record unsupported statements and review minutes. |
| Structured task | Request one store and period, cite each metric, separate pipeline and state a controller question. | Compare with the three-source reference. Score entity/period, margin, threshold/gap, pipeline, source IDs and unsupported causes as six pass/fail items. |
| Review | Give the reviewer a draft claiming $60,000 in recognized income and a one-percent decline from last month. | It should identify pipeline versus income and point out the absence of a prior-month comparison. |
| Fresh session | Provide only the entity checkpoint and skill invocation. | Executive reproduces the brief and locates the input for each number. A correct answer from the wrong source fails. |

For automation, use a bounded programmatic call after deterministic validation. Set allowed tools, turn limit, timeout and spending limit supported by the selected runtime. Keep credentials in the host secret store. If the service is unavailable, retain the packet and mark narrative drafting pending. Never let text from an email, CRM note or document authorize tool expansion, sending or a business-system write. [Programmatic Claude Code](https://code.claude.com/docs/en/headless) · [Permission controls](https://code.claude.com/docs/en/permissions)

## Example handoff after the fictional run

| Field | Value |
| --- | --- |
| Entity and period | north-store • September 2026 • USD accrual |
| Evidence | CRM-SNAPSHOT-09 • QBO-PL-09 • POL-MARGIN-04 |
| Known result | 17% achieved versus 18% floor, $2,500 below target |
| Unresolved | What explains the variance by product or unit category? |
| Owner and next step | Controller to reconcile a category bridge and review the draft |

Update the checkpoint after an accepted revision. On the next run, re-read the current source and policy before carrying a figure forward.
