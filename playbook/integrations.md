# Commission the three business integrations

Use the native connector for a supervised exploration when the account already permits it. For a repeatable close, agree on source IDs, effective dates, completeness and an entity-bound service identity. The public lab implements the normalized contract with fixtures. These commissioning steps belong in a client sandbox.

## HubSpot • Open deals

1. Ask the CRM owner for the portal, pipeline, authorized user and stage IDs that count as open. In a supervised session, enable the HubSpot connector for an approved user and inspect the tool list and permissions shown in the account. HubSpot applies the user's object visibility. Select the minimum permitted data and avoid sensitive properties for this exercise. [HubSpot connector for Claude](https://knowledge.hubspot.com/integrations/set-up-and-use-the-hubspot-connector-for-claude)
2. For unattended extraction, bind the adapter to one portal, allow the deals read scope `crm.objects.deals.read`, request the deal ID, pipeline, stage, amount and currency, and follow pagination to completion. Confirm the currency semantics for this portal. Map stage IDs to the approved open set and major units to exact integer cents. Require a stored month-end snapshot for a historical report. Today's open deals can differ after a subsequent close or stage correction. [HubSpot Deals API](https://developers.hubspot.com/docs/api-reference/crm-deals-v3/guide)
3. Reconcile the count and total to a saved view under the same user and snapshot time. Retain the snapshot ID, portal and as-of date. Test an inaccessible record or second portal. A truncated page, unresolved currency or missing historical snapshot holds publication. Cache the immutable extract so a retry uses the same inputs.

## QuickBooks Online • Closed accrual P&L

1. Register an Intuit app, create a sandbox company and complete the documented OAuth flow. Bind the returned `realmId` to the chosen company. Store tokens in the client's secret manager and persist updated refresh tokens together. Review the requested accounting scope. It can cover changes to accounting data, so expose only the required report read in the adapter and restrict its network route. [Intuit OAuth](https://static.developer.intuit.com/output_html/qbo/docs/develop/authentication-and-authorization/oauth-2.0.html) · [Intuit scopes](https://static.developer.intuit.com/output_html/qbo/docs/learn/scopes.html)
2. Fetch `GET /v3/company/{realmId}/reports/ProfitAndLoss` from the sandbox API host with explicit start/end dates and `accounting_method=Accrual`. Validate returned report header, period, basis and currency. Traverse group summaries to map income, COGS and gross profit. A controller confirms that the month is closed. Avoid adding parent summaries to their child rows. [Intuit Reports API and response structure](https://static.developer.intuit.com/output_html/qbo/docs/workflows/run-reports.html)
3. Compare the three amounts with an exported P&L under identical settings. Record the export reference and close sign-off. Check a zero-income month, a missing COGS section, revoked authorization and a second realm. Escalate ambiguous account mapping to the controller. A prepared export can stand in for the adapter during training.

## Microsoft 365 • Approved policy

1. For supervised search, have the authorized Entra administrator review connector consent and assign a suitable test user. Search for the exact policy within the permitted SharePoint content. The hosted connector acts with delegated rights. Verify the user can see the intended document and confirm the version and effective dates with the controller. [M365 connector setup](https://support.claude.com/en/articles/12542951-set-up-the-microsoft-365-connector) · [Security guide](https://support.claude.com/en/articles/12684923-microsoft-365-connector-security-guide)
2. For a separate unattended Graph app, choose the intended site and request `Sites.Selected`. An administrator consents, then grants the app a read role on that specific site. Obtain an app token with the selected permission and exercise access against both the granted site and another site. Use an approved drive/item ID for the policy, record its version or eTag and obtain the effective policy fields. Avoid a general mailbox or tenant-wide search for this job. [Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview) · [Graph file content](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0)
3. Compare the parsed threshold with the approved policy. Require human review for edits, overlapping policies or missing effective dates. Keep draft delivery separate from source access. A reviewer can place the approved document in the client's designated library using their normal release process.

## Integration desk card

| Symptom | Check first | Operator action |
| --- | --- | --- |
| No MCP tools appear | Session transport, executable path, working directory and SDK startup | Run the stdio smoke test; send diagnostics to stderr and reserve stdout for protocol messages. |
| OAuth request returns 401 | Token expiry, audience and realm/tenant binding | Refresh once with the stored current credential; on failure, pause for the identity owner. |
| Request returns 403 | User object visibility, selected-site assignment or admin grant | Record the denied resource and ask the source owner to verify the intended boundary. |
| Partial CRM total or API throttling | Next-page cursor, response count and retry guidance | Honor Retry-After, use bounded backoff and discard incomplete snapshots. |
| Finance totals diverge | Accounting basis, fiscal dates, duplicate summaries and policy version | Tie back one report line at a time. Hold the draft until finance confirms. |
| Remote MCP replaces local stdio | Client compatibility, user identity and resource-specific tokens | Use authenticated HTTPS and the protocol's authorization flow. Verify audience and approved tools before a data call. [MCP authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) |

Workpaper for each connector: `entity | source account | principal | allowed operation | denied resource | source reference | expected total | observed total | owner | sign-off`. A live integration earns acceptance when both the allowed read and the boundary check have been witnessed in the target environment.
