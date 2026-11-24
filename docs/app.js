import {presets, makePlan, exportPlan, readCopy} from "./presets.js";

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
  byId("example").textContent = plan.example;
  byId("automation").textContent = plan.automation;
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

function download(text, filename, type) {
  const url = URL.createObjectURL(new Blob([text], {type}));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
}

byId("download").addEventListener("click", () => {
  if (!build()) return;
  download(exportPlan(plan, done, byId("notes").value), "workflow-playbook.md", "text/markdown;charset=utf-8");
  byId("status").textContent = "Playbook downloaded with your checklist and run notes.";
});

byId("save-copy").addEventListener("click", () => {
  if (!build()) return;
  const copy = {format:"workflow-fieldbook/1", preset:current, values:values(), done, notes:byId("notes").value};
  download(JSON.stringify(copy, null, 2), "workflow-fieldbook.json", "application/json");
  byId("status").textContent = "Editable copy saved. Use Open a saved playbook to continue.";
});

byId("open-copy").addEventListener("click", () => byId("import-file").click());
byId("import-file").addEventListener("change", async event => {
  const input = event.target;
  const file = input.files[0];
  if (!file) return;
  try {
    if (file.size > 65536) throw new Error("File too large");
    const copy = readCopy(await file.text());
    drafts.set(current, {values:values(), plan, done, notes:byId("notes").value});
    drafts.set(copy.preset, {...copy, plan:makePlan(copy.values, presets[copy.preset])});
    selector.value = copy.preset;
    selectPreset(copy.preset);
    byId("file-status").textContent = "Saved playbook opened.";
    byId("result").focus();
  } catch {
    byId("file-status").textContent = "Choose an editable JSON copy saved by Workflow Fieldbook.";
  } finally {
    input.value = "";
  }
});

function preparePrint() {
  const fullNotes = document.createElement("p");
  fullNotes.id = "print-notes";
  fullNotes.textContent = byId("notes").value || "No notes recorded.";
  byId("print-notes")?.remove();
  byId("notes").after(fullNotes);
}
let printDetails;
window.addEventListener("beforeprint", () => {
  printDetails = Array.from(document.querySelectorAll("#result details"), item => [item, item.open]);
  printDetails.forEach(([item]) => { item.open = true; });
  preparePrint();
});
window.addEventListener("afterprint", () => {
  printDetails?.forEach(([item, wasOpen]) => { item.open = wasOpen; });
  byId("print-notes")?.remove();
});
byId("print").addEventListener("click", () => { if (build()) window.print(); });
selectPreset(current);
document.querySelector(".workspace").hidden = false;
