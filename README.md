# My plan for your advanced Claude engagement

**Jeff Cadet · Private, one-on-one consulting and implementation · 14–21 workshop hours**

I’d start by asking you to show me the last business decision where you used Claude and still had to check or redo part of its work. We’ll use that example to choose one recurring workflow, build it together, and test whether you can operate it on your own. My proposed starting point is a dealership month-end review. If underwriting a manufactured-housing acquisition is the more pressing decision, we’ll build around the rent roll and investment assumptions instead.

[Read the client presentation](https://edcadet10.github.io/claude-executive-automation-playbook/) · [Download the engagement plan (PDF)](docs/Jeff-Cadet-Claude-Engagement-Plan.pdf)

## Before the workshop

| When | How I’ll work with you | What you’ll have afterward |
| --- | --- | --- |
| **30-minute fit call** | You walk me through a recent decision and the answer Claude gave. I show a comparable MCP tool from my TradeProof work. We identify which parts of your process deserve our time. | One candidate project, a business owner and a decision on whether to proceed. |
| **Separate discovery meeting, 45–60 minutes** | We replay the current workflow with a redacted example. I record preparation and review time, sources, corrections, entity boundaries and who approves the result. We compare the dealership, investment and cross-business reporting candidates. | A one-page scope naming the pilot, source systems, baseline, success test, reviewer and access dependencies. |
| **My preparation** | I build an exercise from your approved sample, independently reconcile the expected result, and introduce one realistic failure. I prepare the Claude project, tool contract and teaching materials around your environment. | A tailored workspace, a reference result you trust, and a day-one agenda you can review. |

## Day one · Build the workflow around your decision · 7 hours

You show me how you do the work today. Together we trace the inputs, agree on the definitions, and preserve the context a fresh Claude session will need. For a dealership close, that includes the accounting company, reporting period, definition of gross profit, approved margin floor and the controller who reviews exceptions.

I demonstrate the first run. Then you turn the procedure into a reusable Claude Code skill and run it on a known case. We compare its draft to your reference, correct it, and save the instructions and evidence needed for a second run. **You leave day one with a working pilot on approved sample data and a record of where Claude still needs supervision.**

## Day two · Connect, challenge and operate it · 7 hours

We define the narrow read each system needs to support. In the dealership example, HubSpot supplies the open-deal snapshot, QuickBooks Online supplies the closed P&L, and Microsoft 365 holds the approved policy. We inspect an MCP tool call together and test the wrong company or period. Where sandbox access is ready, we trace an authorized read back to its source. Where access is pending, we use the agreed export and assign an owner for the live check.

We wire the verified figures into a Claude draft and give a separate reviewer agent the source packet to check its claims. You then drive the failure exercise: interrupt a run, replay it and inspect the review queue. The controller owns release. **You leave with the reusable skill, tool configuration, review procedure and a runbook for scheduling, monitoring, retries and recovery.**

## Optional day three · Take the pilot further · 7 hours

We choose one outcome at discovery. If deployment matters most, we connect the next approved source and rehearse the schedule, failure alert and restore on your private host. If investment analysis matters most, we apply the same method to a manufactured-housing deal, change an occupancy assumption and reconcile the effect on net operating income. The result is either an operating rehearsal with the platform owner or a second workflow you can reproduce.

## How you and I will judge success

In a fresh session, you run the pilot without my guidance. You identify the entity and period, trace the material figures to their sources, catch a deliberately bad input and replay the job without duplicating the draft. You explain which facts support the decision and which question still needs a human answer. Together we compare preparation time, review time and corrections against the baseline.

I hand over the workspace, skill and agent definitions, connector map, operating instructions, and a list of remaining dependencies with owners. We agree on the first real cycle to review and what evidence would justify extending the approach to another business. The fit call, discovery and preparation sit outside the 14–21 workshop hours. We confirm dates and commercial scope on the fit call.

## A case you can inspect before we meet

The public dealership lab uses fictional data. A scoped MCP server returns $42,500 gross profit on $250,000 income, or 17% against an 18% policy floor. The $60,000 sales pipeline is reported separately. The executive’s task is to explain the $2,500 shortfall, challenge an unsupported explanation and check what happens when another store is requested. [Inspect the three recorded MCP calls](docs/mcp-session.json) · [Run the finance lab](playbook/reporting-lab.md)

The public implementation verifies MCP, reconciliation, timer replay and durable review. The model-generated narrative and reviewer-agent turn still need verification with a working Claude account. Live HubSpot, QuickBooks and Microsoft 365 commissioning is scoped to the client’s approved environment. [Commissioning guide](playbook/integrations.md) · [Operations guide](playbook/operations.md)

My teaching approach draws on the TradeProof MCP server, reusable Claude Code skills and the Agent Sarah hands-on training lab. For the detailed hour-by-hour facilitation guide, the implementation files and my public work, use the links below.

- [Workshop facilitation and discovery guide](playbook/engagement.md)
- [Claude Code skill, MCP and reviewer exercise](playbook/claude-workshop.md)
- [Jeff Cadet’s practitioner examples](playbook/jeff-cadet.md)
- [Optional discovery worksheet builder](https://edcadet10.github.io/claude-executive-automation-playbook/discovery.html)
