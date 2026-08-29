# Open Questions Register

Every decision in [`PLAN.md`](./PLAN.md) that waits on an answer from [`qa.md`](../../qa.md). The questions themselves live in `qa.md` and are referenced by number here, never restated.

**Numbering:** rows cite `qa.md`, the current draft. The earlier [`qa1-1.md`](../../qa1-1.md) numbers its first 23 questions identically, then diverges, because `qa.md` inserts seventeen questions — the Monthly Billing Run and Payment Processing sections — at 24. From there on, `qa.md` = `qa1-1.md` + 17. Answers returned on the earlier draft need that offset applied before they land here, and a reply citing "Q41" means different things depending on which document the respondent was holding.

**The rule:** build on an assumption freely; confirm it before it prices anything, enforces anything, or migrates anything irreversibly. An assumption reaching the money path unconfirmed is the failure this register exists to prevent.

**States:** `open` (no answer, no working assumption) · `assumed` (working assumption recorded below, safe to build on) · `answered` (confirmed; update the row and the affected section of `PLAN.md`).

## Blocks Phase 2 — the schema cannot settle without these

| Decision | qa.md | Working assumption | State |
| --- | --- | --- | --- |
| Household or student as the billing account | Q49 | Household owes; student carries enrollment and payer. Both stay addressable. | open |
| Sibling discount: still policy, and is the 4th-slot cap deliberate | Q1 | Current behaviour is intended; encoded as ordered discount steps with the cap as data. | assumed |
| Class eligibility: exact age and level bars per type | Q60–Q63 | Parent & Me ≤3; Group 7+ and level 8+; Stroke Tech 10+ and level 10+; Private, Semi-Private, Adult unrestricted. Age AND level. | assumed |
| Whether eligibility exceptions need an audit trail | Q63 | Override carries a reason and an author. | assumed |
| Payer mix within one household | Q11 | Per-student payer assignment, so siblings can differ. | assumed |
| Prepay tiers actually in use, and what earns each | Q14 | All seven tiers modelled as data; only the live ones seeded. | assumed |
| Whether make-up credits expire | Q47 | Credits carry an optional expiry, left null until policy is set. | open |
| Which note abbreviations mean what (`AUG PO`, `WORK`, `MU`, `OUT`) | Q69 | None. Import preserves raw note text until decoded. | open |
| Which colour highlights and typing conventions carry meaning | Q67, Q68 | Under-4 highlight means swim diaper; ALL CAPS name means support need **or** difficult parent, ambiguously. | open |
| Whether the ALL CAPS convention becomes a typed flag | Q71 | Split into `support_need` and `account_handling` flags, office-only for the latter. | assumed |
| How price changes actually propagate, given that pre-created future billing months keep the old rate while newly created ones take the new | `qa1-1.md` Q3, Q16 | Both behaviours are real and describe different rows. The new model materializes nothing ahead of issue, so the import treats a future billing month as an intention rather than an invoice. Confirm before the import runs. | open |

## Blocks Phase 3 — scheduler and search

| Decision | qa.md | Working assumption | State |
| --- | --- | --- | --- |
| Which searches run daily, and which Saved Finds exist | Q55–Q58 | None. Parity cannot be asserted against an unknown set — this is the gate, not a preference. | open |
| Waitlist matching: what staff actually do to place a child | Q52–Q54 | Rank by stated availability, eligibility, and wait time; staff confirm every placement. | assumed |
| Whether group lessons schedule or price differently | Q59 | Same model, capacity greater than one. | open |
| Late-cancellation cutoff, and whether it becomes a rule | Q46 | Discretionary. System records the decision rather than enforcing a cutoff. | open |
| Master closure calendar, or ad hoc | Q45 | Closures entered as they arise; the calendar is the new capability. | assumed |
| Offline need on the pool deck | Q85, Q86 | Attendance works offline and syncs; assume dead zones exist. | assumed |
| Whether attendance records who marked it | Q84 | Recorded silently, no extra step for instructors. | assumed |
| PIN at shift start acceptable | Q82, Q83 | Acceptable, with instant password-free switching between instructor schedules. | assumed |

## Blocks Phase 4 — billing and institutional payers

| Decision | qa.md | Working assumption | State |
| --- | --- | --- | --- |
| How a charter school is billed, start to finish | Q4, Q5 | None. Blocking — the subsystem cannot be designed from guesswork. | open |
| Whether institutional payers authorize lessons or dollars, with expiry | Q6, Q7 | Both shapes supported, with consumption tracked against the cap. | assumed |
| Whether Regional Center billing differs from charter billing | Q9 | Same model, different documentation and terms. | open |
| Documentation required to release payment | Q12 | Attendance-derived service log per student per period. | open |
| Negotiated institutional rates | Q10 | Per-payer price agreements, defaulting to list. | assumed |
| The real month-end steps and where the time goes | Q24–Q26, Q34 | The five understood steps are right and incomplete. | open |
| Mid-month lesson type change: what gets charged | Q31 | Prorate across the change date at each rate. | open |
| Proration rule for partial months | Q24, Q27 | Per-lesson proration against scheduled lessons in the period. | assumed |
| Prepay rate lock duration | Q15 | Holds until the prepaid lessons are consumed. | open |
| Refund basis when a prepaid family leaves early | Q18 | Refund unconsumed lessons at the rate paid. | open |
| What else adjustments are used for | Q20 | Courtesy credits and billing corrections. | open |
| Void versus refund window and who decides | Q33 | One week; office decides. | assumed |
| Whether the two-payments-per-month cap matters | Q22 | A FileMaker limit, not a policy. Removed. | assumed |
| Card-on-file failures and follow-up today | Q39, Q40 | Handled manually. Account Updater assumed off and worth enabling. | open |
| Processing stack confirmation | Q35–Q38 | Affinity24 processor, Authorize.Net gateway, Wells Fargo settlement. | assumed |
| Whether December/January closure bills normally | Q41, Q42 | Yes, full monthly amount, no credit. | assumed |
| Whether one-off closures always credit | Q43, Q44 | Always, unless marked otherwise on the closure. | assumed |

## Shapes the build without blocking it

| Decision | qa.md | Note |
| --- | --- | --- |
| Past-due handling and whether lessons stop | Q50 | Drives dunning; a report suffices at launch. |
| What billing situations fall outside the system today | Q51 | Direct answer to what the replacement must absorb. |
| Access model: who may price, credit, and see billing | Q80 | Roles seeded conservatively; widened on answer. |
| Shared logins and offboarding | Q87, Q88, Q91 | Per-person accounts from day one regardless of answer. |
| Backup and restore reality, tolerable downtime | Q93–Q95 | Sets the recovery objective for Phase 5. |
| Bulk texting use and unmet wants | Q72–Q74 | Scopes the fmSMS replacement. |
| Instructor-authored progress notes | Q77, Q78 | Note audience model already supports it. |
| Allergy prominence | Q76 | Flag severity already supports it. |
| Devices and screen constraints | Q96–Q98 | Sets responsive floor. |
| Part 3 ideas worth building | Part 3 | Every one is a query over the model in `PLAN.md` §2; none needs new capture. |
| What takes way longer than it should | Part 2 | The highest-value answer in the document. Re-read it before every phase. |
