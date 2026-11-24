import {presets, makePlan, exportPlan} from "./presets.js";

const byId = id => document.getElementById(id);
const fields = ["title", "inputs", "success", "reviewer", "cadence"];
const selector = byId("preset");
let current = "weekly";
let plan;
let done;
const drafts = new Map();
const values = () => Object.fromEntries(fields.map(key => [key, byId(key).value.trim()]));

for (const [key, preset] of Object.entries(presets)) {
  selector.add(new Option(preset.label, key));
}

function progress() {
  byId("progress").textContent = done.filter(Boolean).length + " of " + done.length + " complete";
}

function render() {
  byId("result-title").textContent = plan.title;
  byId("meta").textContent = plan.cadence + " · Reviewed by " + plan.reviewer;
  byId("goal").textContent = plan.success;
  byId("prompt").textContent = plan.prompt;
  const steps = byId("steps");
  steps.replaceChildren();
  plan.steps.forEach(([heading, body], index) => {
    const label = document.createElement("label");
    label.className = "step";
    const check = document.createElement("input");
    check.type = "checkbox";
    check.checked = done[index];
    check.addEventListener("change", () => { done[index] = check.checked; progress(); });
    const detail = document.createElement("span");
    const name = document.createElement("strong");
    name.textContent = heading;
    detail.append(name, body);
    label.append(check, detail);
    steps.append(label);
  });
  progress();
}

function selectPreset(key) {
  current = key;
  const saved = drafts.get(key);
  const initial = saved?.values || presets[key];
  fields.forEach(field => {
    byId(field).setCustomValidity("");
    byId(field).value = initial[field];
  });
  plan = saved?.plan || (key === "custom" ? null : makePlan(initial, presets[key]));
  done = saved?.done || Array(5).fill(false);
  byId("notes").value = saved?.notes || "";
  byId("result").hidden = !plan;
  byId("status").textContent = plan ? "" : "Fill in the blank fields to build your first playbook.";
  if (plan) render();
}

selector.addEventListener("change", () => {
  drafts.set(current, {values: values(), plan, done, notes: byId("notes").value});
  selectPreset(selector.value);
});

function build() {
  if (!byId("setup").reportValidity()) return false;
  for (const key of fields) {
    if (!byId(key).value.trim()) {
      byId(key).setCustomValidity("Enter a value for this field.");
      byId(key).reportValidity();
      return false;
    }
  }
  const next = makePlan(values(), presets[current]);
  if (plan && JSON.stringify(next) !== JSON.stringify(plan)) done = Array(5).fill(false);
  plan = next;
  byId("result").hidden = false;
  render();
  return true;
}

byId("setup").addEventListener("input", event => {
  event.target.setCustomValidity?.("");
  if (event.target !== selector) byId("status").textContent = "Build your playbook to apply your edits.";
});

byId("setup").addEventListener("submit", event => {
  event.preventDefault();
  if (build()) {
    byId("status").textContent = "Playbook ready. Check off steps as you complete them.";
    byId("result").focus();
  }
});

byId("download").addEventListener("click", () => {
  if (!build()) return;
  const text = exportPlan(plan, done, byId("notes").value);
  const url = URL.createObjectURL(new Blob([text], {type:"text/markdown;charset=utf-8"}));
  const link = document.createElement("a");
  link.href = url;
  link.download = "workflow-playbook.md";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
  byId("status").textContent = "Playbook downloaded with your checklist and run notes.";
});

function preparePrint() {
  const fullNotes = document.createElement("p");
  fullNotes.id = "print-notes";
  fullNotes.textContent = byId("notes").value || "No notes recorded.";
  byId("print-notes")?.remove();
  byId("notes").after(fullNotes);
}
let promptWasOpen;
window.addEventListener("beforeprint", () => {
  promptWasOpen = byId("prompt-panel").open;
  byId("prompt-panel").open = true;
  preparePrint();
});
window.addEventListener("afterprint", () => {
  byId("prompt-panel").open = promptWasOpen;
  byId("print-notes")?.remove();
});
byId("print").addEventListener("click", () => { if (build()) window.print(); });
selectPreset(current);
