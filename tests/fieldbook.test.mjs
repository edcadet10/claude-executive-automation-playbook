import assert from "node:assert/strict";
import test from "node:test";
import {exportPlan, makePlan, presets, readCopy} from "../docs/presets.js";

const values = {title:"Choose supplies", inputs:"A shelf count", success:"Every shortage is counted",
                reviewer:"Coordinator", cadence:"Weekly"};
const copy = {format:"workflow-fieldbook/1", preset:"custom", values,
              done:[true,false,false,false,false], notes:"Check the paper stock."};

test("editable copies reproduce the saved workflow and run record", () => {
  const restored = readCopy(JSON.stringify(copy));
  const plan = makePlan(restored.values, presets[restored.preset]);
  const markdown = exportPlan(plan, restored.done, restored.notes);
  for (const text of ["# Choose supplies", "- [x] Choose a reference", "A shelf count",
                      "Coordinator", "Check the paper stock.", "## Optional automation"]) {
    assert.ok(markdown.includes(text));
  }
});

test("unsupported or malformed copies are rejected before changing the page", () => {
  for (const change of [{format:"v0"}, {preset:"toString"}, {notes:"x".repeat(5001)},
                        {done:[true]}, {values:{...values, cadence:"unknown"}}]) {
    assert.throws(() => readCopy(JSON.stringify({...copy, ...change})));
  }
});
