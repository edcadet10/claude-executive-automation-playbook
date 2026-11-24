# Lab • A dealership margin review

The GM has time for one follow-up with the controller. Is September's recognized gross margin below policy? The sales manager also wants open pipeline on the page. A deal still in the pipeline has an uncertain close date and carries no recognized income in this calculation.

## Run the reference

From the checkout root, use Python 3.11 or newer. The pilot uses the standard library and the committed fictional snapshot.

```sh
python -m lab.report
python -m unittest discover -s tests -v
```

Read the [source packet](../fixtures/dealer-month.json) before opening the answer. It represents normalized extracts. The CRM slice contains only open deals from the signed month-end snapshot. The controller has marked the accrual P&L closed. The policy covers the full calendar month. A store label inside an extract is a validation aid. A live adapter must obtain the entity from the authenticated portal, realm or tenant/site mapping.

| Question | Independent reference | Evidence |
| --- | --- | --- |
| What is still open in sales? | D-101 at $28,000 and D-102 at $32,000 give $60,000 in open pipeline. | CRM-SNAPSHOT-09 |
| What gross profit did the store recognize? | $250,000 income less $207,500 cost of goods sold gives $42,500. | QBO-PL-09 |
| Did the store meet its floor? | $42,500 ÷ $250,000 = 17%. Policy calls for 18%, or $45,000 at this level of income. The store is 1.00 percentage point and $2,500 below the floor. | QBO-PL-09 and POL-MARGIN-04 |
| What caused the miss? | The packet has no unit mix, incentives, warranty or acquisition-cost breakdown. Ask the controller for a by-category bridge. | Open question for review |

**Disconfirmation exercise.** Before running, predict that changing only pipeline leaves gross margin unchanged and that changing any source's store blocks the draft. Set open deals to an empty list in a private copy. Then change the P&L entity to `south-store`. Run `python -m lab.report --input your-copy.json --entity north-store --period 2026-09`. The first change yields zero open pipeline and 17% margin. The second should exit 2 and identify the mismatched source. Capture exit code, actual values and reviewer initials.

**Precision exercise.** Change COGS to $205,000.01 and gross profit to $44,999.99. Display rounding shows 18.00%. A one-cent miss still puts the store below the floor. Ask the executive which field determines the threshold verdict and have them demonstrate it.

## Transfer exercise • Manufactured housing

A fictional 80-lot community has 72 occupied lots, a $500 monthly site rent, and $180,000 annual operating expenses. Assume full collections, flat rents, no ancillary income and fixed expenses. The base case gives $432,000 annual site rent and $252,000 NOI. At 68 occupied lots, income is $408,000 and NOI is $228,000. Explain the $24,000 downside using four lots × $500 × twelve months.

Have the executive replace one assumption at a time, identify the dated rent roll and expense statement that support the change, then repeat the arithmetic without Claude. Debt service, capital costs and investor tax effects require separate analysis. The assignment ends with an assumptions table, two reconciled scenarios and one diligence question for the investment lead.
