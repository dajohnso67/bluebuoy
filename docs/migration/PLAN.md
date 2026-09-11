# Blue Buoy Migration Blueprint: FileMaker Pro → Go Web Stack

Structural blueprint and execution roadmap for replacing Blue Buoy's FileMaker system — scheduling, billing, attendance — with Go + Chi, Templ, htmx + Alpine.js, Tailwind, and PostgreSQL.

Synthesised from [`technical-prompt.md`](../../technical-prompt.md), the architecture brief, and the staff discovery questionnaire, which exists in two drafts: [`qa.md`](../../qa.md) is the current one, and [`qa1-1.md`](../../qa1-1.md) is the earlier draft it grew from. Question numbers below follow `qa.md`; where a finding survives only in the earlier draft, the citation says so.

**Staff answers arrive in rounds:** [`BlueBuoy_Complete_Context_Package.md`](./BlueBuoy_Complete_Context_Package.md) folds two questionnaire rounds and ownership conversations into its Part A. The reconciliation sweep of 2026-09-07 flipped every register row the first round answered — twenty of thirty-six — and the sweep of 2026-09-10 transcribed the second round ([Round 2](./BlueBuoy_Round2_Questions.docx.md)) into `qa.md` and flipped six more. Wherever this plan still rests on an unconfirmed reading, [`open-questions.md`](./open-questions.md) names the decision that answer blocks. Build on an assumption freely; confirm it before it prices anything. Where the package **corrected** an assumption this plan encodes, the affected section carries an explicit correction note rather than a silent rewrite.

Domain terms are defined once, in [`CONTEXT.md`](../../CONTEXT.md), and used as defined here.

## 1. Executive Summary & Risk Analysis

FileMaker handles Blue Buoy's routine cases and hands the rest to staff. The migration's substance is therefore not porting features. It is absorbing the manual layer — month-end hand-corrections, an entire institutional billing business that never touched the database, and meaning encoded in typography — into a system that carries it.

All three bottlenecks are discovery or verification problems. None is a construction problem.

### Bottleneck 1 — Fog: institutional billing has no digital trace

Fourteen charter schools and nine Regional Center agencies exist in FileMaker as a text note telling staff how to bill. Everything downstream happens in QuickBooks, Excel, email, and paper (qa.md Q4–Q13). The fog has since partially lifted: the context package (2.10, **Confirmed** with the billing team) documents the workflow — rates negotiated each July, deliberately above the auto-pay rate; families obtain their own funding and purchase orders, with **no authorization balance visible to Blue Buoy**; month-end invoicing by email/paper or through each school's own portal; payment a month or more later; **no supporting documentation required to release payment**; and the entire receivables trail living as free-text notes (`JAN 11237 $368`, `CK 7499`). What remains foggy: the two portal submission workflows (never examined), the QuickBooks handoff, and how the AR trail gets structured.

**Move:** the discovery track narrows to what's still dark — one real charter invoice, the tracking spreadsheet or QuickBooks view, and a walkthrough of each portal. The service log and authorization letter drop off the artifact list: both are now confirmed not to exist. The payer subsystem is decided — [ADR-0002](../adr/0002-no-authorization-balance-tracking.md), no authorization balance tracking (§2) — and the Institutional payers phase is gated on the remaining artifacts.

### Bottleneck 2 — Money correctness has no clean oracle

Today's month-end run is manual posting, manual proration, a spreadsheet cross-reference against the card processor, manual referral-credit resets, and a void-or-refund window (qa.md Q24–Q34) — now **Confirmed** at 6–7 hours in a normal month and 10–12 across two days in summer, roughly 100 hours a year, with card mismatches every month (package 2.8). Because the outputs are the product of human correction, "match FileMaker" is not a trustworthy target: some of what it produced was wrong and staff caught it downstream — or didn't, as with a missed referral reset that silently keeps discounting a family (Q29).

**Move:** reconcile by **shadow run**. Price closed months in the new system, compare per household to the cent, and classify every difference as a bug to fix or a FileMaker error to record. The run is **green** when no unexplained difference remains. Green months, not feature completion, are what authorize cutover.

The avoidable half of this risk is the card vault. Cards on file live with Authorize.Net; keeping that gateway carries them across intact. Changing gateways at cutover forces re-collecting every card from every family — the most damaging self-inflicted wound available to this project.

### Bottleneck 3 — Capability regression in search and encoded meaning

Deck Manager's ad-hoc find and its Saved Finds are the staff's power tool, and `qa.md` names the failure directly: replacing a capable search with a prettier, weaker one is how this kind of project goes wrong. Alongside it, real operational data lives in typography — ALL CAPS first names, colour highlights, note shorthand like `AUG PO` and `MU` (Q67–Q69). A straight import reads those as ordinary strings and the meaning evaporates silently, with nothing left to alert anyone.

**Move:** make search parity an acceptance gate in the Scheduling & search phase, measured against the daily searches and Saved Finds that answers to Q55–Q58 enumerate. Round 2 already named the one staff use all day — the schedule board's absence lookup — and asked that it stay an instant action rather than a report. Run a **decode pass** before import that converts each convention into typed data, and treat any convention still undecoded at import as a blocking defect.

### Concurrent locking is a solved case, not a bottleneck

FileMaker's record locking becomes ordinary Postgres transactions plus two named invariants: an exclusion constraint making instructor double-booking impossible to commit, and a period-unique billing run making a double-charge impossible to commit (§2). The database enforces both, rather than discipline, which is why neither earns a risk entry.

## 2. Data Schema Mapping

### FileMaker construct → PostgreSQL

The trap is table occurrences. A FileMaker relationship graph carries dozens of occurrences over a handful of base tables; migrating occurrence-by-occurrence manufactures tables that were never entities.

| FileMaker | Target |
| --- | --- |
| Table occurrence | Not a table. Collapse to its base table; the occurrence's path becomes an explicit foreign key or join |
| Base table | Table, normalized |
| Portal | Child rows over a foreign key, rendered as an htmx fragment |
| Global field | Request or session state, or a `setting` row. Never a column |
| Stored calculation field | Generated column, or a view where it spans rows |
| Unstored calculation field | Computed in the service layer at read |
| Auto-enter calculation | Column default, or resolved by the service on write. Prices resolve once and persist as a snapshot |
| Repeating field | Child table rows |
| Value list | Lookup table plus a foreign key |
| Container field | Object storage key on a `document` row |
| Script trigger | Domain event, handled in the service |
| Server-scheduled script | Cron job holding an advisory lock, idempotent on its period key |
| Saved Find | `saved_search` row holding structured criteria |
| Record lock | Transaction, plus the invariants below |

### Core schema

The brief's four entities map onto Blue Buoy as: **Customers** → `household` and `person`; **Schedules/Appointments** → `slot`, `enrollment`, and `lesson`; **Line Items** → `invoice_line`; **Invoices** → `invoice`.

**Identity**

- `household` — the billing family unit. Siblings share one.
- `person` — `household_id`, name, contact, date of birth. One row per human.
- `household_member` — `person_id`, `household_id`, role (`student`, `guardian`, `billing_contact`). An adult student holds two roles rather than occupying two records.
- `student_profile` — `person_id` primary key, `level_id`, status. Swim-specific attributes only.
- `instructor` — `person_id` primary key, employment status.

**Catalog and pricing**

- `class_type`, `level` — lookup tables replacing value lists.
- `eligibility_rule` — `class_type_id`, optional `slot_id`, age range, level range, `effective_from`. Rules as data, so a confirmed answer to Q60–Q63 lands as a row rather than a deploy. Round 2 confirmed the group bars (Parent & Me 0–3 with no level; Group 7+ and level 9–12; Stroke Tech 10+ and level 10–12; Adult 16+; all capped at 6), and the deck screen shows Group classes banded per class (`lv 8/9/10` beside `lv 9-10`) — hence the optional slot scope.
- `eligibility_override` — `student_id`, `class_type_id`, reason, `authorized_by`. Exceptions stay possible and visible.
- `price` — `class_type_id`, cadence, amount, `effective_from`, `effective_to`. Effective-dated, so the annual increase is a new row and history survives.
- `discount_step` — the ordered sibling ladder and its cap, as rows. Tier assignment order is staff-controllable per household: the confirmed strategy places an institutionally-funded child in the undiscounted first tier so the out-of-pocket sibling gets the discount, and a group lesson goes first for the same reason (Round 2 Q3).
- `household_discount` — `household_id`, kind (`first_responder`), percent, `verified_at`, `verified_by`, `document_id`. The 10% first-responder discount (Round 2 Q16, Confirmed) stacks with the sibling steps and the prepay discount; the verification columns are the "ID provided" flag staff asked for.
- `credit_conversion_rate` — `from_denomination`, `to_denomination`, `from_count`, `to_count`, `effective_from`. The confirmed exchange table (2 semi-private = 1 private, 2 group = 1 semi-private, 4 group = 1 private, every direction; Group, Stroke Tech and Parent & Me are one `group` denomination). Rates as data, so a changed ratio is a row.
- `class_pack` — `student_id`, `class_type_id`, size (1, 4, 8), `purchased_at`, `invoice_line_id` (the snapshot price), `valid_to` (from the `class_pack_expiry_months` rule; null = never); `class_pack_use` — `class_pack_id` (nullable: a deficit), `attendance_id` unique, so an offline replay can never consume twice. A **billing mode** on the enrollment (`monthly` or `class_pack`) decides whether the billing run prices it or skips it; a rule row names which class types sell packs (seeded: Adult). A pack sale is an `invoice` of kind `class_pack` with one line at a `price` row of cadence `per_pack`. Consumption happens on `attendance.marked` present; an empty pack never gates the roll — the balance goes to −1 and a `class_pack_deficit` exception sends the office to sell the next pack. Packs are purchases, not credits: never a denomination of the make-up ledger. The no-show rule (`adult_no_show_consumes`, `adult_notice_hours`), expiry, and whether household discounts reach a pack are rule rows awaiting staff (qa.md Q110). Settled by [ADR-0004](../adr/0004-adult-class-packs.md).

**Scheduling**

- `slot` — `instructor_id`, weekday, `start_time`, duration, `class_type_id`, capacity, active range. The recurring place a family holds.
- `slot_override` — `slot_id`, date, `class_type_id`, reason. An empty group slot lent for one day to semi-private, private, make-ups or Parent & Me when a sub is needed (Round 2 Q1) — a dated action, never an edit to the slot.
- `enrollment` — `student_id`, `slot_id`, date range, `billing_mode` (`monthly`, `class_pack`), `price_agreement_id` (monthly only). The billable relationship.
- `lesson` — `slot_id`, `during` (a `tstzrange`), `instructor_id`, status. One dated occurrence.
- `attendance` — `lesson_id`, `student_id`, status, `marked_by`, `marked_at`, `device_id`, `client_uuid` unique. The last column makes offline replay safe.
- `closure` — date range, scope, reason, `issues_credit`. The master calendar Q45 asks about.
- `waitlist_entry` — `student_id`, desired class type, stated availability, `created_at`.

**Money**

- `payer` — type (`household`, `charter_school`, `regional_center`), name, terms, submission method (`invoice_email`, `invoice_paper`, `portal`, `direct_check`), billing contact. The 14 and the 9 become rows, not a note.
- `payer_assignment` — `student_id`, `payer_id`, share, date range, plus the student's identity with that agency: UCI number and coordinator contact, structured and restricted to billing/management roles. Siblings on different payers, which Q11 confirmed, is the normal case rather than an exception.
- `funding_reference` — `payer_id`, `student_id`, kind (`purchase_order`, `contract`), reference number, optional validity range, notes. Not a balance: per ADR-0002 there is no cap to consume — *absence for a billing period* is what surfaces, as a `billing_run_exception` and a coverage-view line. Validity granularity refines when the institutional artifacts land.
- `price_agreement` — `enrollment_id`, amount, source (`list`, `sibling`, `prepay_lock`, `negotiated`), reason, date range.
- `invoice` — `payer_id`, period, `issued_at`, status (`draft`, `submitted`, `partially_paid`, `paid`, `void`), `submitted_at`, submission method snapshot, total. Receivables aging is a query over open invoices by age.
- `invoice_line` — `invoice_id`, `student_id`, `enrollment_id`, description, quantity, `unit_amount`, amount. `unit_amount` is a snapshot: reprinting a two-year-old invoice reproduces it exactly.
- `credit` — subject, kind (`makeup`, `referral`, `gift`, `courtesy`, `account`), for make-ups a denomination (`private`, `semi_private`, `group`) and `origin_type` (the missed lesson's type, provenance only), count in whole lessons, `source_lesson_id`, `valid_from`, `valid_to` (stamped at issue from the `makeup_expiry_months` rule; null = never), reason, `issued_by`. Adult absences issue no credit — class packs cover attendance.
- `credit_application` — `credit_id`, target line or lesson, status (`reserved` → `consumed`, or `released`), `reserved_at`, `consumed_at`. Booking a make-up reserves the credit, the lesson occurring consumes it, a school-cancelled make-up releases it; a reserved credit is protected from the expiry sweep. Credit and application together form the ledger; a balance is a query, never a field.
- `credit_event` — kind (`conversion`, `transfer`, `reversal`, `expiry`, `void`), source credit, count consumed, resulting credit, rate applied, actor, `at`. A conversion consumes exactly `from_count` of one denomination and issues exactly `to_count` of another at the table rate, the new credit inheriting the earliest source `valid_to`; a transfer moves credits between siblings in a household, keeping origin and expiry; a reversal negates an earlier event and is management-only. The ledger is append-only. These are the hand-written notes staff keep today (Round 2 Q10), made explicable — settled by [ADR-0003](../adr/0003-denominated-makeup-credit-ledger.md).
- `payment` — `payer_id`, amount, method, reference (check number, gateway txn id), `received_at`, `settled_at`. No cap on payments per month.
- `payment_application` — `payment_id`, `invoice_id`, amount. One institutional check settling several students' invoices is the normal case.
- `adjustment` — `invoice_id`, amount, `reason_code`, `created_by`. For genuine one-offs, once the routine cases stop needing one.
- `billing_run` — period, mode (`dry_run`, `shadow`, `committed`), state, timestamps.
| `billing_run_exception` — `run_id`, `household_id`, code, detail. The queue that replaces the spreadsheet cross-reference — including the code for an institutional student with no funding reference for the period, which retires the month-end phone-around, and `class_pack_deficit` for an adult who attended past an empty pack.

> The institutional model above is [ADR-0002](../adr/0002-no-authorization-balance-tracking.md): **no authorization balance tracking** — the earlier cap-consumption design was a corrected over-design (package 2.10, Confirmed). QuickBooks stays the accounting system; the app reconciles with it. Service logs are gone from the model entirely: no payer requires documentation to release payment (qa.md Q12).

> The credit model is **one denominated system, not six balances** — Round 2 confirmed the exchange rates, that every direction is allowed, that staff choose at redemption, and that credits move between siblings (qa.md Q100), and the DDR then showed FileMaker's six `MU_*_Total` counters were never balances but derived sums of out-lessons issued minus make-ups redeemed, with the redeemed type already recorded per booking. [ADR-0003](../adr/0003-denominated-makeup-credit-ledger.md) settles the shape above: three denominations, whole-lesson units, conversion inside redemption, reserve-then-consume, expiry as a rule row, liability valued in private-lesson equivalents, and an import that **replays** history rather than copying counters.

**Flags, notes, documents**

- `flag` — `student_id`, kind (`allergy`, `support_need`, `swim_diaper`, `account_handling`), severity, detail. Typed data replacing typography.
- `note` — subject, body, audience (`office`, `instructor`, `all`), author, `created_at`.
- `document` — kind (`invoice_pdf`, `intake_form`), storage key, subject. Container fields and the institutional paper trail land here.

### Two invariants the database enforces

```sql
-- An instructor cannot be committed to two overlapping lessons.
CREATE EXTENSION IF NOT EXISTS btree_gist;
ALTER TABLE lesson ADD CONSTRAINT lesson_instructor_no_overlap
  EXCLUDE USING gist (instructor_id WITH =, during WITH &&)
  WHERE (status <> 'cancelled');

-- A period can be committed exactly once.
CREATE UNIQUE INDEX billing_run_one_commit_per_period
  ON billing_run (period) WHERE mode = 'committed';
```

### Three modelling decisions that retire manual work

Each replaces a recurring month-end task rather than reimplementing it.

| Today | Model | What stops happening |
| --- | --- | --- |
| Prices rise in January, the system applies the new rate to prepaid families anyway, and staff back out the difference every month afterwards (Q3, Q16) | `price_agreement` holds the locked rate with its own dates; `invoice_line` snapshots what it resolved | The monthly back-out, and the month somebody forgets (Q17) |
| A referral credit is a state someone must remember to clear next month; a missed reset discounts a family indefinitely with nothing flagging it (Q28, Q29) | A `credit` row valid for exactly one period, consumed by application and expired by date | The reset step, and the silent over-discount |
| Make-up credits accumulate invisibly — one student holds 28 unused private credits (Q47) — and convert between types at rates staff carry in their heads, with sibling transfers noted by hand (Q100) | One denominated ledger with a conversion-rate table and transfer events; expiry a policy field | The surprise, the arithmetic at redemption, the hand-written transfer note — and the unused-credit report comes free, valued in one denomination |

**The first row carries a finding the current questionnaire dropped.** FileMaker materializes billing months ahead of time, and a price change never reaches the rows it already created (`qa1-1.md` Q3) — while months created *after* the change take the new rate even for a family holding a locked prepay rate (Q16). Staff therefore correct in both directions, for opposite reasons, and the two corrections look nothing alike from the desk.

The new model materializes nothing ahead of issue. A future month has no row; the billing run prices it from the enrollment and its price agreement when the period arrives, and `invoice_line` snapshots the result at issue. Both corrections disappear along with the rows that required them.

## 3. Logic & Script Migration Strategy

### Calculations

Sort every FileMaker calculation by what it is for, because the three kinds land in different places:

- **Presentational** (a display name, a formatted total) — computed in the Templ template. Nothing persists.
- **Derived and cheap** (age from date of birth, a line total) — a generated column, or computed at read.
- **Monetary and decided** (the rate this enrollment pays) — resolved once by the pricing service and persisted. This is the important reclassification: FileMaker recomputes a price whenever anyone looks, which is precisely why a January price rise reaches families who locked last year's rate. A resolved price is a fact about an agreement, not a lookup.

### Script triggers become domain events

Each trigger becomes a named event the service publishes and handlers subscribe to, so one action can drive several consequences without any of them living inside a UI layout.

| Event | Handlers |
| --- | --- |
| `enrollment.created` | Resolve price agreement, apply sibling step, check eligibility and capacity |
| `enrollment.changed` | Close the outgoing price agreement, open the incoming one, mark the period for proration |
| `lesson.cancelled` | Issue a make-up credit where policy calls for one, notify the family |
| `closure.declared` | Cancel every lesson in range, issue credits where `issues_credit` holds, send the bulk notice |
| `attendance.marked` | Advance progression signals, feed the coverage view, consume a class-pack lesson for a pack-mode enrollment marked present (or record a deficit and raise the exception) |
| `invoice.issued` | Render the PDF, attach it to the payer, start the terms clock |
| `payment.failed` | Raise an exception, notify the office, flag the card |
| `makeup.booked` / `makeup.cancelled` | Reserve the credit (converting first if staff chose to) / release it in the denomination it holds |
| `credit.converted` / `credit.transferred` | Consume the source credits, issue the target at the table rate or to the sibling, record the actor |

### Scheduled server scripts become cron jobs

Each holds a Postgres advisory lock and is idempotent on its period key, so a retry, an overlap, or two instances racing produce one outcome.

| Job | Cadence | Does |
| --- | --- | --- |
| Billing run | Monthly | Prices active enrollments, raises exceptions, issues invoices on commit |
| Credit expiry sweep | Nightly | Expires credits past `valid_to` — never a reserved one — as an `expiry` event; this is also what retires the manual referral reset |
| Card expiry notice | Weekly | Surfaces cards on file about to lapse, ahead of a failed charge |
| Lesson materialization | Nightly | Extends `lesson` rows from `slot` definitions across the rolling window |
| Progression and attrition signals | Weekly | Feeds the Part 3 reports, all of them queries over the model above — including the two-weeks-absent-without-notice list staff asked for (Round 2 Q15) |
| Enrollment snapshot | Weekly | Counts active enrollments by class type for the week, so the year-over-year comparison staff compile by hand into Excel every day (Round 2 Q12) is a query |
| Prepay-ending and batch check | Monthly, before the 1st | Lists prepays ending with enrollment continuing, and each auto-pay student's tuition against the pending Authorize.Net batch — the two monthly searches staff run by hand, surfaced as exceptions |

### The billing run is a state machine, not a script

`draft → priced → exceptions_cleared → committed`. It prices every active enrollment, and any household it cannot price cleanly becomes a `billing_run_exception` rather than a silent guess: an unresolved mid-month change, a prepaid family whose lock expired, a card that failed last period, an institutional student with no funding reference for the period. Staff clear the queue; commit is available once it is empty. The same machine runs in `shadow` mode against closed months, producing a comparison instead of invoices.

This is the design answer to Q24–Q34. The month-end work becomes clearing a short exception list rather than performing the whole run by hand.

### Rules live as data

Eligibility bars, sibling discount steps, the first-responder percentage, prepay tiers, make-up conversion rates, make-up expiry (`makeup_expiry_months`) and the legacy Christmas redemption boundary (`makeup_redeem_before`, qa.md Q109), closure credit policy, cancellation cutoffs, and the class-pack rules (which class types sell packs, `adult_no_show_consumes`, `adult_notice_hours`, `class_pack_expiry_months`, `class_pack_discounts_apply`) are rows, not code. Answers to `qa.md` arrive as configuration a staff member can change, and each carries `effective_from`, so changing a rule leaves last year's invoices reproducible.

## 4. API Contract & Integration Outline

### Two surfaces, and no GraphQL

htmx wants HTML. The application's own screens are Templ fragments served straight from Chi handlers — no JSON round-trip, no client state to keep in sync. A separate, small JSON API serves the one client that genuinely needs data rather than markup: the pool-deck iPad taking attendance offline. GraphQL earns nothing here; it would add a schema layer for a single first-party consumer with a known access pattern.

### Scheduling conflict check

One endpoint answers every "can this student take this slot" question — booking, waitlist matching, and drag-and-drop rescheduling all call it — so the rules have a single home.

```
POST /api/v1/schedule/check
{ "student_id": "...", "slot_id": "...", "starts_on": "2026-09-08" }

200 OK
{
  "bookable": false,
  "conflicts": [
    { "code": "instructor_busy",    "detail": "Overlaps 4:15pm private" },
    { "code": "capacity_full",      "detail": "3 of 3 enrolled" },
    { "code": "student_double",     "detail": "Already enrolled 4:00pm Tue" },
    { "code": "eligibility_unmet",  "detail": "Group needs level 8, student at 6", "overridable": true },
    { "code": "closure",            "detail": "Pool closed Dec 22 – Jan 5" }
  ]
}
```

`overridable` is what keeps the office in charge: the system states the bar and who may pass it, and staff decide (Q63).

### Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/schedule/check` | Conflict and eligibility check |
| `POST` | `/api/v1/enrollments` | Book a slot. `409` on conflict, constraint-backed |
| `GET` | `/api/v1/slots/{id}/waitlist-matches` | Ranked candidates for an opening (Q52–Q54) |
| `POST` | `/api/v1/attendance:batch` | Offline roll sync, idempotent on `client_uuid` |
| `POST` | `/api/v1/closures` | Declare a closure, cancelling and crediting in one action (Q44) |
| `POST` | `/api/v1/billing/runs` | Start a run in a given mode. `202` with a run id |
| `GET` | `/api/v1/billing/runs/{id}` | State, totals, exception list |
| `POST` | `/api/v1/billing/runs/{id}/commit` | Issue invoices. Available on an empty exception queue |
| `GET` | `/api/v1/invoices/{id}.pdf` | Rendered invoice |
| `POST` | `/api/v1/invoices/{id}/void` | Void inside the window (Q33) |
| `GET` | `/api/v1/payers/{id}/receivables` | Open invoices aged: outstanding, per payer, for how long |
| `POST` | `/api/v1/payers/{id}/invoices` | Month-end institutional invoice batch for a period |
| `GET` | `/api/v1/students/{id}/credits` | Credit ledger and balance, per denomination |
| `POST` | `/api/v1/students/{id}/credits/convert` | Exchange credits between denominations at the table rate, recorded as an event; called inside make-up booking, standalone for management only |
| `POST` | `/api/v1/households/{id}/credits/transfer` | Move credits between siblings, recorded as an event |
| `GET` | `/api/v1/reports/enrollment-weekly` | Enrollment by class type per week against prior years — the daily hand-built Excel sheet |

### Integrations

- **Authorize.Net** — kept, with Customer Information Manager holding the card vault so cards survive cutover; Accept.js captures cards in the browser so numbers never touch the server, which ends the plaintext card fields; CIM charges a computed monthly amount (never ARB, whose fixed schedule cannot carry prorations and credits); the processor sits behind one internal interface. Enable Account Updater, which Q39 suggests is off and which turns a failed charge into a silent refresh. Volume is confirmed at $156k–$207k a month (Round 2 Q17), which is why the stack stays.
- **SMS** — replaces fmSMS, which the Round 2 screenshot shows is a Databuzz shell over a **Twilio** account; talk to Twilio directly and keep the sender number. Inbound replies need a destination, which Q74 decides.
- **QuickBooks** — stays the accounting system; the app produces clean exports (the general ledger, P&L and balance sheet the accountant receives each January, Round 2 Q13) rather than replacing it.
- **PDF** — server-side rendering of invoices, stored as `document` rows.
- **Object storage** — S3-compatible, holding what FileMaker container fields held plus institutional documentation.

## 5. Phased Execution Roadmap

Sequencing per [ADR-0001](../adr/0001-attendance-first-sequencing.md): **attendance-first**, targeting the December 2026 closure, with billing deliberately later. Phases carry names, not numbers — the two source documents numbered theirs incompatibly, and bare phase numbers are retired for the same reason bare question numbers were. Each phase ends on a gate; passing a gate is an observation, not a judgement.

### Foundations

The schema from §2 for identity, scheduling, and flags — money tables follow with Billing; the repeatable, non-destructive import against live exports for that slice; the **decode pass** narrowed to every deck-visible convention (ALL-CAPS student names → `support_need` flag, the under-4 diaper rule), with the full decode still gating the wider import; the auth model — individual accounts, PIN at shift start, session and device management; hosting, backup, and point-in-time recovery with one tested restore. An **archive** concept from the start — households restorable, never deleted — because `BlueBuoy_FM_2024` exists only as a performance workaround (families idle ten years moved out of the live file, Round 2 Q18), and what the import does with it is a map decision. The **archaeology** track (institutional artifacts) runs alongside without gating this phase.

**Gate:** the import runs from `BlueBuoy_FM` — confirmed live (Round 2 Q18) — and the `BlueBuoy_FM_2024` archive is accounted for per the archive decision; household, student, enrollment, and flag counts reconcile against FileMaker; ten sampled households match field by field, including flags and notes; no deck-visible convention remains undecoded.

### Attendance — target: December 2026 closure

The strict slice from ADR-0001: roster view on all form factors (tablet-first), present/absent, backfill of a prior day, free instructor switching, profile-note indicator with the read-only two-channel display, diaper badge, offline caching of the full day's schedule for all instructors, PIN at shift start. Explicitly excluded: make-ups, scheduling changes, waitlist, billing visibility. Staff train during the two-week closure; the app is system of record at the January reopening.

**Gate:** a 2–4 week parallel run from the January reopening with attendance reconciled nightly against FileMaker — and instructors prefer it. If they don't, that gets fixed before any later phase proceeds.

### Scheduling & search

Enrollment, schedule editing, waitlist, closures, and search. Search is the phase's centre of gravity, not a feature within it: `saved_search` plus a criteria builder reaching every field staff currently search, seeded with the Saved Finds Q56 names. Plus make-up credit issuance and redemption — including conversion between denominations and sibling transfers, per [ADR-0003](../adr/0003-denominated-makeup-credit-ledger.md) — closure handling (scheduled vs incidental, with bulk make-ups), eligibility validation with override and per-class group bands, one-day repurposing of an empty group slot, the absence lookup as an instant action on the schedule board, the substitute-finding flow with its three constraints (instructor gender, level pairing, sibling proximity), and the deck-manager tools held out of the December slice.

The make-up ledger imports here by **replay**: every `Lesson_Out` row becomes an issued credit (rows flagged do-not-issue import as issued-then-voided), every make-up on `Lesson_Schedules` a consumption in the denomination `Lesson_MU_to_use` names, and the replayed balance is compared per student to the stored `MU_*_Total` — every difference is a reconciliation exception, with two known causes already named (an attendance script that edits counters directly; the do-not-issue flag that never suppressed the credit flag).

**Gate:** replayed make-up balances match FileMaker's stored counters per student, or every difference is classified; every search in the [parity enumeration](../discovery/search-parity-enumeration.md) — the scripted and structured searches the DDR encodes plus the daily finds and Saved Finds from Q55–Q58 — returns the same set as FileMaker on the same data, and deck staff run one full week of real scheduling in the new UI alongside the old, including one full make-up cycle.

### Billing

Constrained by ADR-0001: begins only after the December 2026 rollover has run in FileMaker, and never cuts over in a peak month. The billing run state machine, pricing, credits, proration, rate-lock price agreements, the first-responder discount, enrollment holds and the one-year hold clock, class packs consumed on attendance ([ADR-0004](../adr/0004-adult-class-packs.md) — legacy has nothing to replay: each adult's hand-typed `Adult_Credit` imports as one opening pack of unknown price and every adult lands on a review list; FileMaker's monthly Adult rate rows import like any other pre-created month), the full transaction ledger, invoice PDFs, the Authorize.Net integration, and the monthly prepay-ending and tuition-vs-batch checks as exception views. Dry runs only; nothing charges a card until the shadow gate is green.

FileMaker's pre-created future billing months need a decision of their own before this phase's import runs. They are not history, they are pre-materialized future state, and some of them hold prices that went stale the day the price list changed. Import them as invoices and the staleness crosses into the new system wearing the authority of a record. Import them as what they are — a queue of intentions — and they become enrollments the billing run will price when each period arrives.

**Gate:** open-credit counts reconcile per denomination and every future-dated billing month is accounted for as either an enrollment or a discard with a reason; a dry run of the last closed month reproduces every FileMaker invoice to the cent, or names the difference and its cause; then shadow runs monthly against live data until **three consecutive months land green** — every difference resolved into a fixed bug or a recorded FileMaker error.

### Institutional payers

The payer subsystem as decided by the authorization-model ticket, built on the collected artifacts: per-payer configuration (contract rates, submission method, billing contact), month-end invoice generation, the no-PO-yet prompt, receivables aging, and structured invoice/check references replacing the free-text trail.

**Gate:** one full month invoiced through the system for every active institutional payer, with the receivables trail structured rather than free-text.

### Cutover

Freeze FileMaker writes, run the final import, verify counts, point the gateway at the new system, and keep FileMaker readable for a year alongside a permanent frozen archive that includes `BlueBuoy_FM_2024`. The card vault stays where it is, so no family is asked for a card.

**Rollback:** available until the first committed billing run in the new system. Past that point, FileMaker no longer holds the month, and recovery is forward — which is why three green months, and not two, is the bar.
