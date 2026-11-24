export const presets = {
  weekly: {
    label: "Plan my week",
    title: "Choose this week's three priorities",
    inputs: "My calendar, task list and deadlines",
    success: "Three priorities fit the available time and every fixed deadline has a slot.",
    reviewer: "Me",
    cadence: "Weekly",
    automation: "Start with a calendar export and a task list. Ask for a proposed schedule with three priorities. Compare it with your fixed commitments before creating or moving an event.",
    check: "Move a deadline forward by one day. Which commitment needs to change?",
    example: "Reserve two hours for a Friday deadline, then check that the calendar has two free hours."
  },
  team: {
    label: "Team operations",
    title: "Prepare the service desk handoff",
    inputs: "The open ticket list, shift rota and service targets",
    success: "Each overdue ticket has an owner and a next action tied to its ticket ID.",
    reviewer: "Shift lead",
    cadence: "Daily",
    automation: "Start with a read-only ticket export. Compute age from timestamps and show each ticket ID. Ask an assistant to summarize exceptions. The shift lead decides any assignment change.",
    check: "Remove one ticket's owner. The handoff should flag the gap.",
    example: "Choose one overdue ticket and verify its age and owner in the queue."
  },
  dealer: {
    label: "Dealership reporting",
    title: "Review the store's gross margin",
    inputs: "Closed-month P&L, month-end open deals and approved margin policy",
    success: "The margin and target gap tie to the controller's figures. Pipeline appears separately.",
    reviewer: "Controller",
    cadence: "Monthly",
    automation: "Freeze the month's open-deal snapshot, reconcile the closed P&L, then read the approved margin policy. Use the MCP reporting lab to obtain the verified packet and ask Claude for a controller draft.",
    check: "Substitute a P&L for a different store. The run should stop.",
    example: "Income of $250,000 and cost of goods sold of $207,500 produce a 17% margin against an 18% floor."
  },
  housing: {
    label: "Housing investment review",
    title: "Stress-test a community's occupancy",
    inputs: "Dated rent roll, lot count, rent assumptions and operating expenses",
    success: "Base and downside net operating income reconcile to the assumptions and the reviewer can reproduce the difference.",
    reviewer: "Investment lead",
    cadence: "Per opportunity",
    automation: "Read one dated rent roll and expense statement. Compute occupied lots × monthly rent × 12, subtract operating expenses, then compare two occupancy assumptions. Have the investment lead verify the inputs.",
    check: "Reduce occupied lots while holding rent and stated expenses fixed. Trace the change in annual net operating income.",
    example: "At $500 monthly rent, losing two occupied lots for 12 months cuts annual rental income by $12,000."
  },
  custom: {
    label: "Start from scratch", title: "", inputs: "", success: "", reviewer: "", cadence: "As needed",
    automation: "Choose one read-only source. Automate a single repeatable step, capture its result and compare it with a trusted example. Let the reviewer choose the next action before adding a schedule.",
    check: "Choose one missing, stale or contradictory input. Specify what should make the run stop.",
    example: "Choose a previous result you trust and compare it with a fresh run."
  }
};

export function makePlan(values, preset) {
  const {title, inputs, success, reviewer, cadence} = values;
  const steps = [
    ["Choose a reference", "Find one completed example of “" + title + "”. Record how long it took and one thing the result helped you decide."],
    ["Gather the evidence", "Collect " + inputs + ". Mark the owner and date on each source. Pause when a required source is missing."],
    ["Run one small case", "Use a single period or example. The acceptance test is “" + success + "”."],
    ["Challenge the result", preset.check + " Record the expected and observed behavior."],
    ["Review and repeat", reviewer + " reviews the evidence and records corrections. Repeat on this cadence: " + cadence.toLowerCase() + "."]
  ];
  const prompt = [
    "Help me " + title + ".",
    "Use only the evidence I supply from these sources: " + inputs + ".",
    "Ask for missing inputs. Identify the source for each factual claim. Separate facts, assumptions and proposed actions.",
    "Check the result against this condition: " + success,
    "Return a draft and unresolved questions for " + reviewer + ". Wait for review before any external action."
  ].join("\n");
  return {title, inputs, success, reviewer, cadence, steps, prompt, example: preset.example, automation: preset.automation};
}

export function exportPlan(plan, done, notes) {
  const lines = ["# " + plan.title, "", "Reviewer: " + plan.reviewer, "Cadence: " + plan.cadence,
    "Sources: " + plan.inputs, "Success condition: " + plan.success, "", "## Run checklist", ""];
  plan.steps.forEach(([heading, body], index) => {
    lines.push("- [" + (done[index] ? "x" : " ") + "] " + heading + ". " + body);
  });
  lines.push("", "## Worked example", "", plan.example, "", "## Optional automation", "", plan.automation,
    "", "## Prompt to use with an assistant", "", plan.prompt, "",
    "## Run notes", "", notes.trim() || "Record the source checked, the result, and your next action.", "");
  return lines.join("\n");
}

export function readCopy(text) {
  const data = JSON.parse(text);
  if (data?.format !== "workflow-fieldbook/1" || !Object.hasOwn(presets, data.preset))
    throw new Error("Unrecognized playbook");
  const limits = {title:160, inputs:750, success:750, reviewer:100, cadence:40};
  const values = {};
  for (const [field, limit] of Object.entries(limits)) {
    const value = data.values?.[field];
    if (typeof value !== "string" || !value.trim() || value.length > limit)
      throw new Error("Invalid workflow field");
    values[field] = value.trim();
  }
  if (!["As needed","Daily","Weekly","Monthly","Per opportunity"].includes(values.cadence)
      || !Array.isArray(data.done) || data.done.length !== 5 || data.done.some(x => typeof x !== "boolean")
      || typeof data.notes !== "string" || data.notes.length > 5000)
    throw new Error("Invalid run record");
  return {preset:data.preset, values, done:data.done, notes:data.notes};
}
