# Operate and hand over a recurring workflow

## Choose the runtime

| Environment | Suitable use | Verify before relying on it |
| --- | --- | --- |
| Interactive Claude Code session or local loop | Teach the sequence and adjust the prompt with the operator present. | Close the session and inspect whether the task survives. Check the current scheduling behavior on that client. [Session scheduling](https://code.claude.com/docs/en/scheduled-tasks) |
| Claude-hosted scheduled task | A cloud run that has the required repository, connectors, account entitlements and approved network access. | Verify the actual execution identity, available secrets, time zone and destination. A local stdio server on a laptop needs a deployment path reachable by the cloud job. [Claude-hosted tasks](https://code.claude.com/docs/en/routines) |
| Dedicated Linux host with a timer | One entity's private extracts and a local durable review database. The supplied example uses this design. | Keep the host running, monitor disk and clock, back up the ledger, and demonstrate a restore. [systemd timers](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html) |
| Azure Container Apps scheduled job | A client with an Azure operations team and approved managed storage. | Move ledger semantics into durable transactional storage shared by executions, bind the job identity to one entity, and verify cron timing and log delivery. Local container files are unsuitable for the only copy of the ledger. [Azure jobs](https://learn.microsoft.com/en-us/azure/container-apps/jobs) |

The GitHub Pages tool runs in the visitor's tab. The public repository runs CI on synthetic data. Private schedules belong on the customer's approved infrastructure. GitHub notes that scheduled Actions can be delayed or dropped during high load, which matters to a finance cutoff. [GitHub workflow troubleshooting](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows)

## Rehearse locally

From the checkout root, run the following commands on the fictional fixture. The first command returns a draft ID. A second run returns the same ID and `created: false`. Substitute the returned ID wherever this example uses 1.

```sh
python -m lab.queue stage
python -m lab.queue stage
python -m lab.queue show 1
```

Read the packet, compare the figures with the finance reference, then exercise the human decision in a disposable lab ledger. An operator records their own review.

```sh
python -m lab.queue review 1 --decision changes_requested --reviewer "Lab operator" --note "Please supply the category bridge."
```

A changed input revision creates a new draft and supersedes an older pending one. A prior decision stays in history. The revision key hashes the normalized JSON with sorted object keys. SQLite commits the review and input revision together within each operation. On a shared production host use one private state directory and service identity per entity. Restrict the human review command and database access with the host's identity controls. The lab's reviewer text field records an asserted name.

**Optional Claude question.** With the operator's approval to send the verified packet to their configured model, run `python -m lab.queue stage --with-claude` on a pending draft. This adds one model-generated question for the controller. The model has no tools. The CLI receives a $0.25 budget per invocation and the worker waits up to 120 seconds. A three-minute lease allows recovery after a worker exits. A duplicate successful run reuses the saved question. After three claims the scheduler holds further attempts. An operator can diagnose the cause and invoke `python -m lab.queue retry-question 1` for an explicit additional attempt. The source packet survives provider failures. A crash after the provider responds and before local commit can consume an extra model call on retry. The ledger prevents a duplicate stored result.

## Install the timer on a private Linux host

1. Provision a dedicated unprivileged `fieldbook` user/group, Python 3.11+ at `/usr/bin/python3`, a root-owned checkout at `/opt/workflow-fieldbook` and a service-owned private `/var/lib/fieldbook-north/inbox`. Configure encrypted storage and backup according to client policy. Reserve administrative access for the operator.
2. The finance owner sets the approved `REPORT_PERIOD=2026-09` in `/etc/fieldbook/north-store.env` for the rehearsal. An authorized upstream adapter writes the complete normalized extract to a temporary file in the inbox and atomically renames it to `month.json` once the three source checks pass. Advance the approved reporting period as part of the close checklist. A mismatched snapshot fails validation.
3. Copy `ops/fieldbook-report.service` and `ops/fieldbook-report.timer` into `/etc/systemd/system/`. Run `systemd-analyze verify` on both files and `sudo systemctl daemon-reload`. Start the service once, inspect exit status and journal, and open the recorded draft. Only enable the timer after a human accepts this rehearsal.
4. Run `sudo systemctl enable --now fieldbook-report.timer`, inspect `systemctl list-timers fieldbook-report.timer`, and compare its next weekday 07:15 UTC run with the business timezone. `Persistent=true` catches a missed calendar trigger when the timer becomes active again. An extended outage needs an explicit inventory and replay of every missed business period.
5. The supplied unit stages deterministic drafts. To add Claude questions, install the CLI in the service's execution path, provide an authorized service credential through the client's secret facility and enable writable private CLI state under the service account. Add `--with-claude` to the existing service command using a reviewed drop-in. Test as the service identity, including provider failure and account cost controls. Keep review and release with the controller.

## Monitor, recover and teach back

| Signal | Example threshold for discovery | Response and evidence |
| --- | --- | --- |
| Last successful expected run | No draft or replay receipt 30 min after scheduled start | On-call checks timer, service status, host clock, inbox arrival and journal. Record missed periods and replay each approved snapshot. |
| Source validation failure | First entity, period, basis or completeness mismatch | Keep source privately, stop model execution and notify the data owner with entity, period and reason. |
| Model error or expired lease | First error logged; three claims per revision | Preserve verified facts, inspect credentials, provider and timeout. Resume after lease expiry. Human can review the evidence without a model question. |
| Review backlog | Pending beyond one business day | Controller reviews by ID, records evidence and either approves or requests changes. Maintain reviewer coverage during absences. |
| Access or records exposure | Unexpected entity, tool or recipient | Stop the timer, revoke the affected credential, preserve minimal audit evidence and involve the responsible administrator. |

Wire service failures and missing-success deadlines into the client's existing monitoring system. Rehearse alert delivery with the on-call owner. Restrict logs to time, run ID, revision, duration and failure class. Store packets and narratives only in the client's approved private location. For the local ledger, use SQLite's online backup or stop writers before copying. Restore into a separate directory, compare revision and review status by ID and replay the original input. The expected result is the same draft ID. Set a retention window and confirm who can delete expired backups.

**Stop or roll back.** Run `sudo systemctl disable --now fieldbook-report.timer`. Check whether the oneshot service is still running and stop it if necessary. Revert the deployed code to the previous reviewed revision. Preserve the ledger and approved inputs. Restore into a separate path if schema compatibility is uncertain, then rehearse one period before re-enabling.

## Handoff record

| Owner | Demonstration | Evidence to retain privately |
| --- | --- | --- |
| Executive | Start fresh, run the workflow, challenge one unsupported claim | Correct packet, redacted draft, duration and open question |
| Controller | Reconcile the three references, reject a flawed draft and review its replacement | Variance tie-out, decision, timestamp and revision |
| Platform owner | Stop/restart the timer, trigger a failure, restore a backup and replay without duplicating the draft | Run IDs, alert receipt, restore result and next scheduled time |
| Integration owners | Read an allowed record and demonstrate a denied boundary per system | Account binding, denied resource, report version and owner |

Agree on a first review date, operating owner, data deletion date and one next workflow. Mark any sandbox, access, billing or delivery dependency with its owner and expected verification date. Production acceptance requires observed evidence in the client's environment.
