---
name: month-end-brief
description: Build a source-linked dealership brief for one entity and reporting period from the fieldbook MCP evidence packet.
disable-model-invocation: true
---

Ask for the entity and month when either is missing. The public exercise uses north-store and 2026-09. Call `mcp__fieldbook__get_reporting_packet` with exactly the requested entity and period. If the call fails, state the blocker and stop.

Draft up to 120 words for the operating meeting. Identify entity and month. State gross profit, gross margin, policy floor, signed percentage-point variance and dollar variance. Describe open pipeline separately. Cite the returned source IDs alongside the figures they support. Never infer a cause from the variance alone.

Ask the `brief-reviewer` subagent to check the draft against the packet supplied in its task. Include its correction or unresolved finding. Finish with one question for the controller and the status “Draft for controller review.”
