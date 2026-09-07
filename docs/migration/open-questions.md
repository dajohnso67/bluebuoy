# Open Questions Register

Every decision in [`PLAN.md`](./PLAN.md) that waits on an answer from [`qa.md`](../../qa.md). The questions themselves live in `qa.md` and are referenced by number here, never restated.

**Numbering:** rows cite `qa.md`, the current draft. The earlier [`qa1-1.md`](../../qa1-1.md) numbers its first 23 questions identically, then diverges, because `qa.md` inserts seventeen questions — the Monthly Billing Run and Payment Processing sections — at 24. From there on, `qa.md` = `qa1-1.md` + 17. The context package's Part C uses a third numbering (its shift-start PIN is Q87 where `qa.md` has Q83), so citations to it below name the package explicitly. A bare question number with no document is meaningless — never write one.

**Reconciliation sweep, 2026-09-07:** every `open` and `assumed` row was checked against [`resources/BlueBuoy_Complete_Context_Package.md`](../../resources/BlueBuoy_Complete_Context_Package.md), whose Part A folds in staff and ownership answers. Rows the package answers are flipped to `answered`, citing the package section and its confidence label. Three assumptions were **contradicted** by Confirmed findings (authorization tracking, payment documentation, refund basis) — the affected rows say so, and the schema redesign is tracked on the wayfinder map (issue #1, ticket #4). Four newly-surfaced questions gained rows, marked **(new)**.

**The rule:** build on an assumption freely; confirm it before it prices anything, enforces anything, or migrates anything irreversibly. An assumption reaching the money path unconfirmed is the failure this register exists to prevent.

**States:** `open` (no answer, no working assumption) · `assumed` (working assumption recorded below, safe to build on) · `answered` (confirmed; update the row and the affected section of `PLAN.md`).

## Blocks Foundations — the schema cannot settle without these

| Decision | qa.md | Working assumption · answer | State |
| --- | --- | --- | --- |
| Household or student as the billing account | Q49 | Household owes; student carries enrollment and payer. Both stay addressable. Package §7 recommends family-level billing with student line items but leaves the call to ownership (Part D). | open |
| Sibling discount: still policy, and is the 4th-slot cap deliberate | Q1 | Mechanics Confirmed in the DDR: full rate, then −1/−2/−3 discount steps, capped at 3× from the 4th slot. Whether the cap is *intended policy* still needs ownership (package 3.4, Part D). Encoded as ordered discount steps with the cap as data. | assumed |
| Class eligibility: exact age and level bars per type | Q60–Q63 | Age AND level. Package 3.1: Parent & Me ≤3, Group 7+ **and level 9+** (this register previously said 8+ — values disagree and both are marked approximate), Stroke Tech 10+ and level 10+. Capacity Confirmed: all three group types cap at 6. Exact bars still need staff. | assumed |
| Whether eligibility exceptions need an audit trail | Q63 | Override carries a reason and an author. Package 3.1 concurs: warn, allow override with reason. | assumed |
| Payer mix within one household | Q11 | **Confirmed (package 2.9):** mixed payers within one family are common; payer assignment is per student. New requirement: staff deliberately place the institutionally-funded child in the undiscounted first tier so the out-of-pocket sibling gets the discount — tier assignment must stay manually controllable. | answered |
| Prepay tiers actually in use, and what earns each | Q14 | **Confirmed (package 3.6):** duration-based — 4-month = 5%, 8-month = 10%. The full 0–100% ladder exists in FileMaker; which other tiers are genuinely offered still needs enumeration before seeding. | answered |
| Whether make-up credits expire | Q47 | None. Ownership decision still open; balances of 24–28 unused credits appear normal (package 3.9, Part D), so this is a real liability call, not housekeeping. | open |
| Which note abbreviations mean what (`AUG PO`, `WORK`, `MU`, `OUT`) | Q69 | Partial decode (package 3.2, 3.7): `$ OCT`-style notes = a billing adjustment due that month (Confirmed); `WORK`, `AUG PO` = hold reasons stored as text. Full glossary still needed; import preserves raw note text until decoded. | open |
| Which colour highlights and typing conventions carry meaning | Q67, Q68 | **Confirmed (package 3.2):** student first name in ALL CAPS = special needs (verified against `flag_Special_Needs`); parent first name in ALL CAPS = difficult account; bold at top of account = permanent info incl. UCI number and coordinator contacts; age highlight = under-4 swim-diaper requirement; blue/pink = gender; red note = needs attention; `$ OCT` = scheduled adjustment. | answered |
| Whether the ALL CAPS convention becomes a typed flag | Q71 | Split into `support_need` and `account_handling` flags, office-only for the latter. Package 3.2 recommends the same replacement; ownership sign-off pending (Part D). | assumed |
| How price changes actually propagate, given that pre-created future billing months keep the old rate while newly created ones take the new | `qa1-1.md` Q3, Q16 | **Confirmed (DDR + package 3.5):** rates are stamped by auto-enter at row creation; next year's rows are pre-generated in bulk, so pre-created months keep old rates while newly created rows take new ones. Prepay locks are maintained entirely by hand — twelve monthly negative adjustments per prepaid family per year. Import treats future billing months as intentions, never invoices (`PLAN.md` §5, Billing phase). | answered |
| **(new)** Make-up credit conversion ratios between lesson types | Q100 | Reported only (package 3.3): credits convert between types (~4 group ≈ 1 private; some group ≈ 1 semi-private). Ratios, permitted directions, and approval process unverified — and they change the credit model from six separate balances to one denominated system. | open |
| **(new)** Which FileMaker file is live: `BlueBuoy_FM` or `BlueBuoy_FM_2024` | Q99 | The analyzed schema is `BlueBuoy_FM`, but `BlueBuoy_FM_2024` exists on the host and hasn't been analyzed (package appendix). Until answered, the analyzed schema cannot be treated as canonical for the import. | open |

## Blocks Scheduling & search

| Decision | qa.md | Working assumption · answer | State |
| --- | --- | --- | --- |
| Which searches run daily, and which Saved Finds exist | Q55–Q58 | None. Parity cannot be asserted against an unknown set — this is the gate, not a preference. (Package 2.6 confirms heavy Find-mode usage and the searchable field list, not the daily set.) | open |
| Waitlist matching: what staff actually do to place a child | Q52–Q54 | **Confirmed (package 2.4, 2.5):** staff curate every placement and the system never auto-books; stated availability is a ranking signal, not a filter (families are routinely more flexible than filed); offers go to one family at a time — a manual convention today (`8/27 offrd T` in a notes field) that the offer queue formalizes. | answered |
| Whether group lessons schedule or price differently | Q59 | Structure Confirmed (package 3.1): seat-based, same model as private with capacity 6. Still open: minimum enrollment to run, whether price varies with fill, sibling-tier interaction, and what the Adult type even is (package Part D). | open |
| Late-cancellation cutoff, and whether it becomes a rule | Q46 | Current practice Confirmed discretionary (package 3.9); whether to formalize a cutoff is an ownership call. System records the decision either way. | open |
| Master closure calendar, or ad hoc | Q45 | Closures entered as they arise; the calendar is the new capability. DDR supports it: `Holiday_Dates` holds ~6 rows — a working set, not a durable calendar (package 3.8, Inferred). | assumed |
| Offline need on the pool deck | Q85, Q86 | Attendance works offline and syncs; assume dead zones exist. Package 2.1 raises the bar: cache the **full day's schedule for all instructors** on every device — dead-battery iPad handoffs are routine. | assumed |
| Whether attendance records who marked it | Q84 | Recorded silently, no extra step for instructors. Package 1.2 concurs: attribution as a passive byproduct at most — confirm staff want it at all. | assumed |
| PIN at shift start acceptable | Q82, Q83 | **Confirmed (package 1.2):** PIN at shift start establishes identity; switching the displayed schedule and marking your own attendance from any device stays instant and password-free — device independence is a hard requirement. Bounded PIN-session window, auto re-lock on inactivity, remote revocation. | answered |
| **(new)** Make-up offer response window | Q102 | An active offer genuinely holds the slot, then auto-cascades to the next family on expiry. The window's duration is unset — confirm with staff. | open |

## Blocks Billing and Institutional payers

| Decision | qa.md | Working assumption · answer | State |
| --- | --- | --- | --- |
| How a charter school is billed, start to finish | Q4, Q5 | **Confirmed (package 2.9):** rates negotiated ~July per school, deliberately above the auto-pay rate; families obtain their own funding/purchase orders; Blue Buoy invoices at month end against the PO — some schools by emailed/paper invoice, others through the school's own portal; payment lands a month or more later. Today's entire AR trail is free-text notes (`JAN 11237 $368`, `CK 7499`). | answered |
| Whether institutional payers authorize lessons or dollars, with expiry | Q6, Q7 | **Confirmed (package 2.9) — corrects the recorded assumption:** neither. Families hold their own funding; Blue Buoy has no visibility into balances and nothing to track against a cap. The real needs are a month-end "no PO yet" prompt and receivables aging. The replacement model is decided: funding references, never balances ([ADR-0002](../adr/0002-no-authorization-balance-tracking.md)). | answered |
| Whether Regional Center billing differs from charter billing | Q9 | **Confirmed (package 2.9):** it differs — annual family-arranged contracts, rates kept ≈ the auto-monthly rate (charters deliberately higher), some agencies require invoices while at least one sends checks directly; students carry a UCI number plus coordinator contacts, today as bold notes. | answered |
| Documentation required to release payment | Q12 | **Confirmed (package 2.9) — corrects the recorded assumption:** none. No attendance sheets or service logs are required by any payer. | answered |
| Negotiated institutional rates | Q10 | **Confirmed (package 2.9):** per-school contract rates set annually ~July; Regional Center ≈ auto-monthly rate. Per-payer price agreements stand. | answered |
| The real month-end steps and where the time goes | Q24–Q26, Q34 | **Confirmed (package 2.8):** the five understood steps are right. 6–7 hours in a normal month, 10–12 across two days in summer (~100 h/yr). Worst step: posting each family's lesson type at the right tier. Card mismatches occur monthly; the office misses a mid-month change 1–2×/month, caught only at the next run. | answered |
| Mid-month lesson type change: what gets charged | Q31 | **Confirmed (package 2.8):** prorate at the tier the student currently occupies — tier position is preserved across the type change (Parent & Me 1st tier → Semi-Private 1st tier). | answered |
| Proration rule for partial months | Q24, Q27 | Per-lesson proration against scheduled lessons in the period. Package 2.8 confirms proration is occasional (end-of-summer peak) and should compute from scheduled lessons; the exact arithmetic is still unconfirmed. | assumed |
| Prepay rate lock duration | Q15 | **Confirmed (package 3.6, 3.7):** the lock holds until the prepaid months are consumed. On an enrollment hold it survives up to one year from the pause (months restored at the locked rate); past a year it converts to a dollar credit at current rates — and that dollar credit never expires. | answered |
| Refund basis when a prepaid family leaves early | Q18 | **Confirmed (package 3.6) — corrects the recorded assumption:** months actually taken are recalculated at the tier the family genuinely earned, and the difference refunded (an 8-month 10% prepay stopped at month 4 recomputes those months at the 4-month 5% tier). Not "refund unconsumed lessons at the rate paid". | answered |
| What else adjustments are used for | Q20 | **Confirmed (package 3.5, 2.7):** dominated by the manual prepay-lock back-outs (12 per prepaid family per year — retired by price agreements) and `$ OCT` referral resets; plus courtesy credits and corrections. The full payment/adjustment type list is enumerated in the DDR. | answered |
| Void versus refund window and who decides | Q33 | **Confirmed (package 2.8):** refunds run after the 1st but before that week's scheduled lesson — roughly one week; deliberately discretionary, sometimes a make-up is offered instead. Preserve the discretion. | answered |
| Whether the two-payments-per-month cap matters | Q22 | **Confirmed (DDR; package 2.7):** `Amount_Paid_1/2` is a FileMaker structural limit; the new transaction ledger removes it. | answered |
| Card-on-file failures and follow-up today | Q39, Q40 | Handled manually. Account Updater status still unknown (package Part D). | open |
| Processing stack confirmation | Q35–Q38 | Affinity24 processor, Authorize.Net gateway, Wells Fargo settlement. Monthly volume answered "550–700" — almost certainly transaction count, unit unconfirmed (package Part D). The gateway stays regardless (master prompt rule 6); the package's Stripe recommendations are superseded architecture advice. | assumed |
| Whether December/January closure bills normally | Q41, Q42 | **Confirmed (package 3.8, 3.5):** full monthly amount, no credit — the two-week closure is absorbed into the flat annual tuition model (`Billing_Months` has no lesson-count field). | answered |
| Whether one-off closures always credit | Q43, Q44 | **Confirmed (package 3.8, 3.9, live records):** yes — a bulk closure action issues make-ups to everyone affected (Memorial Day and Presidents Day closures seen on real student records); the legacy "do not issue" guard covers the exceptions. | answered |
| **(new)** Military discount: amount and stacking | Q101 | A military discount exists (families need somewhere to attach ID proof) but appears nowhere else in the corpus. Amount, and stacking with sibling and prepay discounts, unknown. | open |

## Shapes the build without blocking it

| Decision | qa.md | Note |
| --- | --- | --- |
| Past-due handling and whether lessons stop | Q50 | Drives dunning; a report suffices at launch. |
| What billing situations fall outside the system today | Q51 | Direct answer to what the replacement must absorb. |
| Access model: who may price, credit, and see billing | Q80 | Roles seeded conservatively; widened on answer. Package §1 proposes four roles incl. the Deck Manager surfaced from `Instructor_Entry`. |
| Shared logins and offboarding | Q87, Q88, Q91 | Per-person accounts from day one regardless of answer. Package 1.3 confirms at least one shared login ("deck manager") exists today. |
| Backup and restore reality, tolerable downtime | Q93–Q95 | Sets the recovery objective for Cutover. Whether a FileMaker restore has ever been tested is still unknown (package Part D). |
| Bulk texting use and unmet wants | Q72–Q74 | Scopes the fmSMS replacement. Confirmed (package 2.10): fmSMS is a Databuzz shell over a third-party SMS gateway — identify the configured provider from its Accounts/Gateways tab; inbound replies currently go nowhere and staff want them. |
| Instructor-authored progress notes | Q77, Q78 | Note audience model already supports it. |
| Allergy prominence | Q76 | Flag severity already supports it. |
| Devices and screen constraints | Q96–Q98 | Sets responsive floor. |
| Part 3 ideas worth building | Part 3 | Every one is a query over the model in `PLAN.md` §2; none needs new capture. |
| What takes way longer than it should | Part 2 | The highest-value answer in the document. Re-read it before every phase. |
