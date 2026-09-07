# Blue Buoy Migration Blueprint: FileMaker Pro → Go Web Stack

Structural blueprint and execution roadmap for replacing Blue Buoy's FileMaker system — scheduling, billing, attendance — with Go + Chi, Templ, htmx + Alpine.js, Tailwind, and PostgreSQL.

Synthesised from [`technical-prompt.md`](../../technical-prompt.md), the architecture brief, and the staff discovery questionnaire, which exists in two drafts: [`qa.md`](../../qa.md) is the current one, and [`qa1-1.md`](../../qa1-1.md) is the earlier draft it grew from. Question numbers below follow `qa.md`; where a finding survives only in the earlier draft, the citation says so.

**`qa.md` itself is still blank, but staff answers arrived by another route:** [`resources/BlueBuoy_Complete_Context_Package.md`](../../resources/BlueBuoy_Complete_Context_Package.md) folds a questionnaire round and ownership conversations into its Part A, and the reconciliation sweep of 2026-09-07 flipped every register row the package answers — twenty of thirty-six. Wherever this plan still rests on an unconfirmed reading, [`open-questions.md`](./open-questions.md) names the decision that answer blocks. Build on an assumption freely; confirm it before it prices anything. Where the package **corrected** an assumption this plan encodes, the affected section carries an explicit correction note rather than a silent rewrite.

Domain terms are defined once, in [`CONTEXT.md`](../../CONTEXT.md), and used as defined here.

## 1. Executive Summary & Risk Analysis

FileMaker handles Blue Buoy's routine cases and hands the rest to staff. The migration's substance is therefore not porting features. It is absorbing the manual layer — month-end hand-corrections, an entire institutional billing business that never touched the database, and meaning encoded in typography — into a system that carries it.

All three bottlenecks are discovery or verification problems. None is a construction problem.

### Bottleneck 1 — Fog: institutional billing has no digital trace

Fourteen charter schools and nine Regional Center agencies exist in FileMaker as a text note telling staff how to bill. Everything downstream happens in QuickBooks, Excel, email, and paper (qa.md Q4–Q13). The fog has since partially lifted: the context package (2.9, **Confirmed** with the billing team) documents the workflow — rates negotiated each July, deliberately above the auto-pay rate; families obtain their own funding and purchase orders, with **no authorization balance visible to Blue Buoy**; month-end invoicing by email/paper or through each school's own portal; payment a month or more later; **no supporting documentation required to release payment**; and the entire receivables trail living as free-text notes (`JAN 11237 $368`, `CK 7499`). What remains foggy: the two portal submission workflows (never examined), the QuickBooks handoff, and how the AR trail gets structured.

**Move:** the discovery track narrows to what's still dark — one real charter invoice, the tracking spreadsheet or QuickBooks view, and a walkthrough of each portal. The service log and authorization letter drop off the artifact list: both are now confirmed not to exist. Design of the payer subsystem is a live decision ticket on the wayfinder map (issue #4); Phase 4 is gated on it and the remaining artifacts.

### Bottleneck 2 — Money correctness has no clean oracle

Today's month-end run is manual posting, manual proration, a spreadsheet cross-reference against the card processor, manual referral-credit resets, and a void-or-refund window (qa.md Q24–Q34) — now **Confirmed** at 6–7 hours in a normal month and 10–12 across two days in summer, roughly 100 hours a year, with card mismatches every month (package 2.8). Because the outputs are the product of human correction, "match FileMaker" is not a trustworthy target: some of what it produced was wrong and staff caught it downstream — or didn't, as with a missed referral reset that silently keeps discounting a family (Q29).

**Move:** reconcile by **shadow run**. Price closed months in the new system, compare per household to the cent, and classify every difference as a bug to fix or a FileMaker error to record. The run is **green** when no unexplained difference remains. Green months, not feature completion, are what authorize cutover.

The avoidable half of this risk is the card vault. Cards on file live with Authorize.Net; keeping that gateway carries them across intact. Changing gateways at cutover forces re-collecting every card from every family — the most damaging self-inflicted wound available to this project.

### Bottleneck 3 — Capability regression in search and encoded meaning

Deck Manager's ad-hoc find and its Saved Finds are the staff's power tool, and `qa.md` names the failure directly: replacing a capable search with a prettier, weaker one is how this kind of project goes wrong. Alongside it, real operational data lives in typography — ALL CAPS first names, colour highlights, note shorthand like `AUG PO` and `MU` (Q67–Q69). A straight import reads those as ordinary strings and the meaning evaporates silently, with nothing left to alert anyone.

**Move:** make search parity an acceptance gate in Phase 3, measured against the daily searches and Saved Finds that answers to Q55–Q58 enumerate. Run a **decode pass** before import that converts each convention into typed data, and treat any convention still undecoded at import as a blocking defect.

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
- `eligibility_rule` — `class_type_id`, `min_age`, `min_level`, `effective_from`. Rules as data, so a confirmed answer to Q60–Q63 lands as a row rather than a deploy.
- `eligibility_override` — `student_id`, `class_type_id`, reason, `authorized_by`. Exceptions stay possible and visible.
- `price` — `class_type_id`, cadence, amount, `effective_from`, `effective_to`. Effective-dated, so the annual increase is a new row and history survives.
- `discount_step` — the ordered sibling ladder and its cap, as rows.

**Scheduling**

- `slot` — `instructor_id`, weekday, `start_time`, duration, `class_type_id`, capacity, active range. The recurring place a family holds.
- `enrollment` — `student_id`, `slot_id`, date range, `price_agreement_id`. The billable relationship.
- `lesson` — `slot_id`, `during` (a `tstzrange`), `instructor_id`, status. One dated occurrence.
- `attendance` — `lesson_id`, `student_id`, status, `marked_by`, `marked_at`, `device_id`, `client_uuid` unique. The last column makes offline replay safe.
- `closure` — date range, scope, reason, `issues_credit`. The master calendar Q45 asks about.
- `waitlist_entry` — `student_id`, desired class type, stated availability, `created_at`.

**Money**

- `payer` — type (`household`, `charter_school`, `regional_center`), name, terms. The 14 and the 9 become rows, not a note.
- `payer_assignment` — `student_id`, `payer_id`, share, date range. Siblings on different payers, which Q11 asks about, becomes the normal case rather than an exception.
- `authorization` — `payer_id`, `student_id`, `lessons_authorized`, `dollars_authorized`, `starts_on`, `expires_on`. Consumption is a query against it, so teaching past a cap becomes visible before it becomes unpaid work.
- `price_agreement` — `enrollment_id`, amount, source (`list`, `sibling`, `prepay_lock`, `negotiated`), reason, date range.
- `invoice` — `payer_id`, period, `issued_at`, status, total.
- `invoice_line` — `invoice_id`, `student_id`, `enrollment_id`, description, quantity, `unit_amount`, amount. `unit_amount` is a snapshot: reprinting a two-year-old invoice reproduces it exactly.
- `credit` — subject, kind (`makeup`, `referral`, `gift`, `courtesy`, `account`), amount or count, `valid_from`, `valid_to`, reason, `issued_by`.
- `credit_application` — `credit_id`, target line or lesson, `applied_at`. Credit and application together form the ledger; a balance is a query, never a field.
- `payment` — `payer_id`, amount, method, `gateway_txn_id`, `received_at`, `settled_at`. No cap on payments per month.
- `adjustment` — `invoice_id`, amount, `reason_code`, `created_by`. For genuine one-offs, once the routine cases stop needing one.
- `billing_run` — period, mode (`dry_run`, `shadow`, `committed`), state, timestamps.
- `billing_run_exception` — `run_id`, `household_id`, code, detail. The queue that replaces the spreadsheet cross-reference.

> **Correction pending — wayfinder ticket #4.** The context package (2.9, **Confirmed**) contradicts the `authorization` model above: charter and Regional Center funding is held by the *family*; Blue Buoy has no visibility into balances or caps, so there is no consumption to track and nothing to warn against. The confirmed needs are a month-end "enrolled institutional students with no purchase order yet" prompt and per-payer receivables aging. Until that ticket lands, treat as up-for-redesign and **do not build**: the `authorization` table, the `attendance.marked` consumption handler and `authorization.nearing_limit` event (§3), the nightly authorization check (§3), the `GET /api/v1/payers/{id}/authorizations` endpoint (§4), and the service-log half of invoice packets (§4) — service logs are Confirmed unnecessary to release payment (qa.md Q12).

**Flags, notes, documents**

- `flag` — `student_id`, kind (`allergy`, `support_need`, `swim_diaper`, `account_handling`), severity, detail. Typed data replacing typography.
- `note` — subject, body, audience (`office`, `instructor`, `all`), author, `created_at`.
- `document` — kind (`invoice_pdf`, `service_log`, `intake_form`), storage key, subject. Container fields and the institutional paper trail land here.

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
| Make-up credits accumulate invisibly — one student holds 28 unused private credits (Q47) | The ledger makes balances queryable and expiry a policy field | The surprise, and the unused-credit report comes free |

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
| `attendance.marked` | Consume an authorization unit, advance progression signals |
| `invoice.issued` | Render the PDF, attach it to the payer, start the terms clock |
| `payment.failed` | Raise an exception, notify the office, flag the card |
| `authorization.nearing_limit` | Alert the office before the cap is passed rather than after |

### Scheduled server scripts become cron jobs

Each holds a Postgres advisory lock and is idempotent on its period key, so a retry, an overlap, or two instances racing produce one outcome.

| Job | Cadence | Does |
| --- | --- | --- |
| Billing run | Monthly | Prices active enrollments, raises exceptions, issues invoices on commit |
| Credit expiry sweep | Nightly | Expires credits past `valid_to`, which is what retires the manual referral reset |
| Authorization check | Nightly | Flags institutional authorizations near their cap or expiry |
| Card expiry notice | Weekly | Surfaces cards on file about to lapse, ahead of a failed charge |
| Lesson materialization | Nightly | Extends `lesson` rows from `slot` definitions across the rolling window |
| Progression and attrition signals | Weekly | Feeds the Part 3 reports, all of them queries over the model above |

### The billing run is a state machine, not a script

`draft → priced → exceptions_cleared → committed`. It prices every active enrollment, and any household it cannot price cleanly becomes a `billing_run_exception` rather than a silent guess: an unresolved mid-month change, a prepaid family whose lock expired, a card that failed last period, an institutional student past their authorization. Staff clear the queue; commit is available once it is empty. The same machine runs in `shadow` mode against closed months, producing a comparison instead of invoices.

This is the design answer to Q24–Q34. The month-end work becomes clearing a short exception list rather than performing the whole run by hand.

### Rules live as data

Eligibility bars, sibling discount steps, prepay tiers, closure credit policy, and cancellation cutoffs are rows, not code. Answers to `qa.md` arrive as configuration a staff member can change, and each carries `effective_from`, so changing a rule leaves last year's invoices reproducible.

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
| `GET` | `/api/v1/payers/{id}/authorizations` | Authorized, consumed, remaining, expiring |
| `POST` | `/api/v1/payers/{id}/invoice-packets` | Institutional packet: invoice plus service logs for a period |
| `GET` | `/api/v1/students/{id}/credits` | Credit ledger and balance |

### Integrations

- **Authorize.Net** — kept, with Customer Information Manager holding the card vault so cards survive cutover. Enable Account Updater, which Q39 suggests is off and which turns a failed charge into a silent refresh.
- **SMS** — replaces fmSMS. Inbound replies need a destination, which Q74 decides.
- **PDF** — server-side rendering of invoices and service logs, stored as `document` rows.
- **Object storage** — S3-compatible, holding what FileMaker container fields held plus institutional documentation.

## 5. Phased Execution Roadmap

Each phase ends on a gate. A gate is checkable and exhaustive by design: passing it is an observation, not a judgement.

### Phase 1 — Data extraction and DDR analysis

Run the Database Design Report to inventory base tables, table occurrences, calculations, scripts, and value lists. In parallel, and on the critical path, run the two discovery tracks the DDR cannot serve: **archaeology** for the institutional business, collecting the four real artifacts, and the **decode pass** that turns every typographic convention into a documented rule.

Get `qa.md` back. Answers to Q49, Q1, and Q60–Q63 gate the schema; Q4–Q13 gate the largest subsystem.

**Gate:** every FileMaker base table appears in the mapping with a target or a recorded reason for dropping it; every question in `qa.md` carries a state in the register; the four institutional artifacts are in hand; no undecoded convention remains.

### Phase 2 — Core backend and database

Build the schema in §2, the Go service layer over it, and the import. Import runs repeatedly and non-destructively until it reconciles, with the decode pass feeding typed flags rather than raw strings.

FileMaker's pre-created future billing months need a decision of their own before the import runs. They are not history, they are pre-materialized future state, and some of them hold prices that went stale the day the price list changed. Import them as invoices and the staleness crosses into the new system wearing the authority of a record. Import them as what they are — a queue of intentions — and they become enrollments the billing run will price when each period arrives.

**Gate:** household, student, enrollment, and open-credit counts match FileMaker exactly; ten sampled households match field by field, including flags and notes; and every future-dated billing month is accounted for as either an enrollment or a discard with a reason.

### Phase 3 — Scheduler UI

The deck view, enrollment, waitlist, closures, attendance, and search. Search is the phase's centre of gravity, not a feature within it: `saved_search` plus a criteria builder reaching every field staff currently search, seeded with the Saved Finds Q56 names. Attendance ships as an offline-capable PWA with the PIN-at-shift-start model from Q83.

**Gate:** every search from Q55–Q58 returns the same set as FileMaker on the same data, and deck staff run one full week of real scheduling in the new UI alongside the old.

### Phase 4 — Billing and PDF generation

The billing run state machine, pricing, credits, proration, invoice and service-log PDFs, the Authorize.Net integration, and the institutional subsystem the archaeology defined. Dry runs only; nothing charges a card.

**Gate:** a dry run of the last closed month reproduces every FileMaker invoice to the cent, or names the difference and its cause.

### Phase 5 — Parallel run and cutover

Shadow runs monthly against live data while FileMaker stays the system of record. Differences resolve into fixed bugs or recorded FileMaker errors. Staff work both systems for scheduling and attendance; billing commits in one place only.

**Gate:** three consecutive shadow months land green.

**Cutover:** freeze FileMaker writes, run the final import, verify counts, point the gateway at the new system, and keep FileMaker readable for a year. The card vault stays where it is, so no family is asked for a card.

**Rollback:** available until the first committed billing run in the new system. Past that point, FileMaker no longer holds the month, and recovery is forward — which is why three green months, and not two, is the bar.
