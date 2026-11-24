# Jeff Cadet's practitioner briefing

I build tools that let someone check what an AI system did. In this workshop, I start with a number the executive already trusts. We work backward to the system that produced it, give Claude a bounded way to retrieve it, and ask the executive to challenge the resulting brief.

## What I would show on the fit call

| Public work | What to open | How I would use it with this executive |
| --- | --- | --- |
| [TradeProof MCP server](https://github.com/edcadet10/tradeproof-mcp-server/tree/89a86334f052abdc76ab4c0f56606dffb7eec7ef) | The server exposes contractor-license lookups and structured results from the TradeProof API. | Trace one lookup from the question to the API. Design the dealership equivalent around a single store and period. |
| [Write Goal](https://github.com/edcadet10/write-goal/tree/aa5988cbb76c277af1da2b79895867faaa2faa36) and [Disconfirm](https://github.com/edcadet10/disconfirm/tree/b37f4dd8cf4883f77c1294683516b87e8754be49) | Claude Code skills for observable completion conditions and tests that could overturn a claim. | Write the controller's acceptance test together. Try a wrong entity and a plausible but incorrect margin explanation. |
| [Agent Sarah](https://github.com/edcadet10/agent-sarah-web/tree/30bc0a6febed8de617c9acb6f38e6cdd4076bb52) | A grounded Azure AI Foundry help-desk agent and reference build for a hands-on Goodwill Columbus course lab. | Show how a learner checks a citation and handles an unanswered question. Apply the same exercise to a finance policy. |
| [MarcEddy](https://github.com/edcadet10/marceddy/tree/23833f73f7c8255606fb119c1a82ecb168c65649) | A multi-step agent with scheduling, deduplication and a human decision before external submission. | Follow one repeated input through its history. Ask where a controller should take ownership of a reporting draft. |
| [Microsoft 365 Audit Playbook](https://github.com/edcadet10/m365-audit-playbook/tree/e0bd32fcac603faae214b0e9e9f5b07418fde7ea) and [TradeProof cloud operations](https://github.com/edcadet10/tradeproof-cloud-case-study/tree/d5f9f48bbea04568d7b77d5abfa272268b571041) | Evidence collection in M365 and operational examples covering identity, scheduled jobs and recovery. | Map each entity's access and ask the operator to recover a failed job before enabling a timer. |

## How I would describe the engagement

“Bring one report you use to make a decision and one instance where Claude got it wrong. On day one we will reproduce the numbers and capture the business rules Claude has been missing. On day two you will run the workflow in a fresh session, explain an exception and recover a failed run. We will use a third day if your team wants to connect a sandbox or add another investment scenario.”

## Fit and scheduling notes

The public examples establish Claude Code skill development, MCP implementation, agent design, cloud operations, Microsoft 365 fieldwork and hands-on technical teaching. The HubSpot and QuickBooks modules in this repository are proposed integration work. Discuss any additional client-specific delivery history, executive references and disclosure permission privately. Confirm U.S. engagement eligibility and actual December 2026 or January 2027 dates directly before submitting a proposal.
