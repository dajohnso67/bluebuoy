# Blue Buoy — Export Session Findings (Addendum to the Context Package)

> **Committed copy, 2026-09-16 (reconciliation sweep 3).** The original lives gitignored in `resources/q-and-a-context/`. Two identifying details were generalised (a legacy key example built from a family's names; one student's age and tenure). Its "Round 3" answers are transcribed into `qa.md` and cited as "Findings §n"; its corrections are folded into `docs/migration/PLAN.md` and the context package v3 in the same change.

**Dates:** September 13–14, 2026
**Source:** Live FileMaker export work on the office laptop, with screenshots of the export dialogs, the resulting spreadsheets, and several live records. Everything below was seen directly in the data or stated by Eric during the session.
**Status:** Running document. Items marked **Correction** change something the context package currently says. Items marked **New** aren't in the package at all. Items marked **Open** need an answer from Jennifer, Cindy, or the developer.

This is an addendum, not a replacement. Fold it into the context package at the next full revision.

---

## 1. Export status and method

### Tables exported (all to `C:\BlueBuoy_Export`, Excel format, one row per record, header row present) — **complete as of Sept 14, 2026**

| File | Records | Size | Notes |
|---|---|---|---|
| Students_All | 9,443 | 11.6 MB | Card number and expiry columns deleted from the spreadsheet after export |
| Families_All | 13,782 | 16.0 MB | `Credit_Card_1/2`, `Additional_CC_Notes` excluded at export |
| Staff_All | small | 13 KB | |
| Lessons_All | — | 381 KB | |
| Lesson_Schedules_All | — | 34.1 MB | |
| Lesson_Attendance_All | 339,624 | 61.8 MB | ~14 min export |
| Lesson_Out_All | 82,599 | 15.1 MB | |
| Waitlist_All | — | 2.4 MB | |
| Billing_Rates_All | 7 | 6 KB | 2020–2026 |
| Billing_Years_All | 33,495 | 5.1 MB | |
| Billing_Months_All | 493,652 | 58.1 MB | ~5 min export |
| Notes_All | 830 | 161 KB | Used lightly by design (Round 3); nothing purged |
| Documents_All | 15,374 | 1.5 MB | Metadata only; the PDFs are in a container field and did not export |
| Audits_All | 5,958 | 732 KB | Lesson/schedule audit, not general |
| Preferences_All | 1–2 | 6 KB | Globals; screen state only |

`Holiday_Dates` **exists** (12 fields, 6 records, confirmed in Manage Database → Tables) but has no layout of its own, so it was not exported. Trivial for the developer to pull; or create a blank layout for it later. `Lesson_Out_Requests` and `Lesson_Rates` confirmed at 0 records.

### Full table inventory (Manage Database → Tables, Sept 14, 2026)

| Table | Fields | Records | Exported? |
|---|---|---|---|
| Audits | 10 | 5,958 | Yes |
| Billing_Months | 65 | 493,652 | Yes |
| Billing_Rates | 27 | 7 | Yes |
| Billing_Years | 32 | 33,495 | Yes |
| Documents | 17 | 15,374 | Yes (metadata only) |
| Families | 47 | 13,782 | Yes |
| Holiday_Dates | 12 | 6 | **No** — no layout; developer to pull |
| Lesson_Attendance | 45 | 339,624 | Yes |
| Lesson_Out | 44 | 82,599 | Yes |
| Lesson_Out_Requests | 17 | 0 | Skipped (empty) |
| Lesson_Rates | 11 | 0 | Skipped (empty) |
| Lesson_Schedules | 110 | 127,738 | Yes |
| Lessons | 64 | 975 | Yes |
| Navigation Menu | 11 | 6 | Skipped (UI) |
| Notes | 17 | 830 | Yes |
| Preferences | 93 | 1 | Yes |
| Recovered Library | 2 | 1 | Skipped (crash artifact) |
| Recovered Library 2 | 2 | 6 | Skipped (crash artifact) |
| Staff | 33 | 39 | Yes |
| Students | 323 | 9,446 | Yes (9,443 at time of export; 3 added since) |
| Virtual_List | 124 | 2,080 | Skipped (scratch) |
| Waitlist | 50 | 10,615 | Yes |

The exports are a snapshot as of Sept 13–14, 2026. Cutover will need a fresh pull.

### Deliberately skipped
T20_Navigation_Menu, T21_Virtual_List, T22_Lesson_Rates (empty), Lesson_Out_Requests (empty), Recovered Library and Recovered Library 2 (crash artifacts).

### Method that works
1. Layout menu → **Maintenance** submenu → pick the `T##_` layout for the table. These are plain one-per-table layouts and are the right starting point for every export.
2. Show All; confirm the record count matches the table total.
3. File → Export Records → file type **Excel Workbooks (.xlsx)**, saved to the local folder, not OneDrive.
4. Excel Options: tick **Use field names as column names in first row**; worksheet named for the table.
5. Field dialog: dropdown set to **Current Table** (not Current Layout, which only offers fields placed on the layout, and not any Related Table entry, which multiplies rows). Clear All, Move All, then remove the exclusions below. "Apply current layout's data formatting" **unchecked**.
6. Naming convention: `<TableName>_All.xlsx`.

### Fields excluded on purpose (developer should know these are missing)
- `Char`, `Char Copy`, `Char_*` — progressive-prefix search-key calculations (e.g. `B, BR, BRA, BRAN…`). Enormous, derived, not data. These triggered the Excel truncation warning.
- `_kz_*`, `index_usage`, `FoundSetIDs_SMS` — index / working fields.
- All `g_*` fields — FileMaker globals; session state, identical on every row. (Exception: Preferences was exported in full, since globals are its contents.)
- `c_vl_code`, `c_vl_JSON` (Attendance) — Virtual List scratch calculations.
- All `sum_*` fields — summary fields recomputed per row; harmless but slow.
- `c_Header_DELETE`, `Image` (container; won't export anyway).
- `Credit_Card_1`, `Credit_Card_2`, `Additional_CC_Notes` (Families); card number columns deleted from the Students spreadsheet post-export.

### Things that went wrong, for the record
- First attempt was CSV: no header row, records split across ~9 lines each, control characters rendered as boxes. Unusable.
- Second attempt exported one record because the found set was a single student.
- Third attempt pulled related-table fields and produced one row per related schedule record.
- First correct-format Excel export stopped at ~794 rows (creation order, 1999–2017). Most likely cause: the laptop went to sleep mid-export; sleep was turned off afterward and the rerun completed. The separate "data will be truncated" warning was caused by oversized calculated fields (`Char`, `Char Copy`, etc.), which were then excluded. Both changes were made before the successful run, so the two causes weren't isolated.
- **Practical note:** disable sleep on the exporting machine for any long export.
- The export folder was inside OneDrive. Files were moved to `C:\BlueBuoy_Export`. **Still to do:** empty the OneDrive recycle bin at onedrive.com to remove the earlier copies (including the CSV with full card numbers).

### Export speed is driven by calculated fields, not row count
Students (9,443 rows) took roughly an hour; Lesson_Schedules (tens of thousands of rows) took under a minute. The difference is the volume of unstored calculations on Students that reach into related tables (weekly grid, age, MU totals, unpaid-lesson counters, balance due). Each student row pulls related schedule/billing/attendance records to evaluate them. Implications: (a) Billing_Months and Attendance may export faster than their size suggests if their fields are mostly stored; (b) this is the mechanism behind the legacy system slowing as records accumulate and the reason families are archived to `FM_2024`. A normal indexed schema removes the problem; performance-driven archiving should not be needed in the new system.

### What's on the Desktop that's fine to leave
The `AI FILEMAKER DATABASE` folder contains the DDR XML exports only (schema, no records). Safe in OneDrive.

---

## 2. Corrections to the context package

### 2.1 ALL-CAPS names are calculated, not typed — **Correction**
The Students table has both `Name_First` (stored, normal case: "Brandon", "Lucas", "Memphis") and `Name_First_calc` (the capitalized version). The capitalization is produced by a formula, almost certainly from `flag_Special_Needs`. The package says capitalization is part of the stored value and requires a human pass over every caps name before normalizing. **That landmine largely disappears**: stored names are clean and the flag already exists as a real field.

**Resolved (Round 3):** Cindy confirms the field is formatted for title case and upper-cases the first name only when Special Abilities is checked. No one types caps by hand. Capitalized *last* names are data-entry noise with no meaning; Cindy wants them in title case. **Migration rule:** apply title case to all names; drive the special-needs display from `flag_Special_Needs`. **Parent first name in caps — confirmed by Eric.** This one *is* typed by hand and means "handle with care": the parent complains, struggles to understand, or is needy. **Migration rule:** capitalized *parent* first names must be flagged before normalizing, unlike student names. **Design (agreed with Eric):** store as an office-only "handle with care" flag plus a short reason note; **display the parent's name in caps on office screens when the flag is set**, so the glanceable convention survives. Never shown to instructors or on parent-facing output. Same pattern as the student special-needs caps in FileMaker.

### 2.2 Card storage is mixed, not uniformly plain-text — **Correction (partial)**
`Credit_Card_Num_1` on Students holds two patterns:
- Some records: a full card number in plain text.
- Many records: `first-four  brand  online  last-four` (e.g. "4100 visa online 4888"), which reads as a note that the card is stored online (presumably Authorize.Net) with just enough to identify it.

So the practice changed at some point and older records kept the old format. The exposure is real but narrower than "every record." Card fragments also appear in free-text notes fields, which no column deletion fixes.

**Resolved (Round 3):** All cards are stored in Authorize.Net and monthly charges run from there. "online" means exactly that. FileMaker's copies are redundant, so **the scrub can start immediately** with no sequencing risk. The expiry field also carries free-text notes (whose card, when updated) that the migration should parse or preserve. Full-number records go back an unknown number of years; scrub all of them.

**New finding, and the real ongoing leak:** only Jen and Cindy have Authorize.Net access. When a family calls the office to pay, staff have to write the card down somewhere and pass it along. That is where card fragments in notes fields come from, and scrubbing old records won't stop it.

**Decision (Eric):** the school does *not* want to widen Authorize.Net access. The preferred path is **sending the family an invoice** from Authorize.Net so the family enters their own card. Jen also wants assurance that the amount charged is the right one.

**Design for the new system:** office staff never see or enter a card. A payment request (invoice / hosted payment link) is generated with the amount computed from the family's account, optionally reviewed by billing before it goes out, and the payment outcome posts back to the ledger automatically. This satisfies both constraints: no staff card access, and no hand-typed amounts.

**Invoicing is already enabled and has been used.** Two known costs today (Eric): (1) the payment has to be matched by hand to the right family when it arrives; (2) enrollment can't be confirmed until the family pays, and some families are slow.

**Decisions (Eric, Jen):**
- Jen sends invoices. Office staff request; Jen sends.
- Authorize.Net's built-in invoice is email-only. Texting would be preferred. **New-system design:** generate a hosted payment link from the family record and send it by SMS through the texting gateway (Authorize.Net supports hosted payment pages; developer to confirm the exact product). Payment posts back to the right account automatically, so the manual matching disappears.
- **Enrollment hold rule (confirmed):** when a family is offered a lesson time pending payment, the slot is held **until 5:00 pm the following day**. If unpaid by then, the hold releases, the slot returns to availability, and the invoice is cancelled. Reuses the held-seat mechanism in 3.1 with a fixed expiry.

**Interim:** use invoices for phone payments now; accept the manual matching as the cost of not writing cards down.

### 2.3 A soft-delete flag already exists — **Correction**
`flag_trashcan` is present on both Students and Families. The package says the legacy system has no deletion safeguard at all. Something exists; whether it's wired into the UI, and whether the deletion incident bypassed it, is unknown.

### 2.4 An `Audits` table exists — **Correction, with a limit**
It appears in the Maintenance layout list and has been exported. Structure: an ID, links to lesson / lesson schedule / student, created-by and timestamp, and a free-text `Log`. So it audits **lesson and schedule changes per student**, not billing or family edits. The package's assumption of a general audit log is only partly right; the developer should read a sample of `Log` entries to confirm scope.

### 2.5 Contact relationship labels already exist — **Correction**
Families has `Primary_Relation` and `Secondary_Relation`. The package recommends modeling contacts as "name + relationship label"; that's already structured data, not something to invent.

### 2.6 Single notes table — **Confirmed**
`T18_Notes` is one table. The two channels are distinguished by `flag_instructor` and `flag_deck_manager`; `flag_checked` carries the acknowledge/dismiss state; each note can link to a specific attendance record (`id_attendance`) as well as student and instructor. Instructor and student names are also stored as text on the note (`Name_Instructor`, `Name_Student`).

### 2.7 The "50% off PRIV" case and the caps example are the same student — **Correction**
The package cites these as two separate findings. They are one record: an adult student with a developmental disability who has attended for decades, takes private lessons, and years ago was offered private at the semi-private price. **Eric confirmed this is discretionary, not policy.** The package's framing (management-approved override with a recorded reason) is correct; the example should carry the reason so nobody later reproduces "50% off PRIV" as a rule.

Related: a note on that record moves 10 make-up credits to a grandchild "as SP only, not PRIV, since 50%." So a private credit purchased at half price converts at semi-private value, not private value. This interaction between a pricing override and credit conversion is not in the package.

### 2.8 Make-up balances are larger than the package suggests — **Correction**
The package's example was 28 unused private credits. Visible in the export: 58, 62, and 90 private; 81 semi-private. `OLD_MU_REMAINING` on Students means some balances were carried over from the *previous* migration, so part of today's liability may predate the current system. Strengthens the case for the expiry decision and the outstanding-credit report.

### 2.9 Billing_Rates facts — **New detail**
Seven rows, 2020–2026. Private is exactly double semi-private every year (260/130 → 368/184). Group, Parent & Me, and Stroke Tech share one price (78 → 105). Sibling-discount step is $8 for private and $4 for everything else, unchanged across all years. Prices rose every year. Pre-2020 billing has no rate row; the developer should confirm pre-2020 Billing_Months rows carry stamped amounts.

### 2.10 Waitlist review is already timestamped — **New detail**
Waitlist has `Last_Checked` and `Last_Checked_Initials`. The weekly manual review the staff want automated leaves a trace on each record; useful for measuring how often requests are actually looked at.

### 2.11 Text-based instructor join is confirmed on three tables — **Confirmation**
`Instructor_Name_First` sits alongside `id_staff` on Lessons, Lesson_Schedules, and Lesson_Out. The developer should count rows where the name doesn't match the ID.

### 2.12 Previous migration used names as keys — **New detail**
`OLD_FAMILY_ID` on Families is the family's names concatenated (the family's first and last names run together in lower case). Explains the package's warning about integrity on older records.

### 2.13 Weekly grid columns are stale for inactive students — **New detail**
The `c_Week*` / `c_1…c_52` columns on Students hold 2020 dates for most records and only refresh for currently scheduled students. Don't assume they're current.

### 2.14 Charter school is recorded in the Payment Plan field — **Confirmation**
A student's `Payment_Plan` showed a charter school's name. Consistent with the package; confirm this is the only place institutional payer is recorded.

### 2.15 Instructor-to-office notes also live on the attendance row — **New detail**
`Intructor_Notes_to_Office` (sic) is a field on each Lesson_Attendance record, separate from the Notes table. Reconstructing note history means reading both.

### 2.16 "No Partner" lives in free text — **Confirmation**
Lesson schedule notes contain "No Partner" for the solo-semi-private arrangement described below. There is no structured flag.

---

## 3. New business rules from conversation with Eric

### 3.1 Held seats (solo semi-private) — **New**
A special-needs student, or a child who is struggling, is sometimes placed in a semi-private slot with no partner. It's temporary ("a few weeks or so"), unpredictable, and sometimes requested by the teacher. Sometimes the family is steered toward private lessons instead.

**Requirement:** a "held open" flag on a seat so matching stops offering it, with a **review date** and a prompt when it's been held longer than expected. Settable in seconds from the office. Not a student attribute; a seat attribute.

**Resolved (Round 3):** Two distinct mechanisms, not one:
1. **Student-seat hold** — a semi-private slot blocked from a second student for a set number of weeks, typically 4, when a teacher thinks a child needs it temporarily. Design: held-seat flag with a review date defaulting to 4 weeks.
2. **Instructor time block** — the teacher's regular break, or an ad hoc block for a day (coming in late, leaving early, out sick and the office doesn't want to offer the time to callers). This already exists in FileMaker as "create a break" (`flag_has_break`). Design: keep as a separate object with day-level lifetime.
Both must be excluded from availability in every matching feature. They are different things and should not share one flag.

### 3.2 Discretion is a design requirement — **New**
Eric wants to keep using judgment across many situations (trades, goodwill credits, refunds vs. make-ups, special pricing). The design answer is a short set of general-purpose override actions, each requiring **who** and **a one-line reason**: adjust a bill by a dollar amount; set a special price; issue or waive a make-up credit; hold a seat; refund or offer a make-up instead. Do not try to anticipate every case.

### 3.3 Trades / barter — **New**
Blue Buoy occasionally trades lessons for goods or services. Today Jennifer marks the family **"do not bill"** so month-end skips them; the value of the trade is recorded nowhere.

**Resolved (Round 3):** trades are rare ("special circumstances") and Cindy is fine with a note. **Requirement:** a `Trade` payment type with a dollar value and note; nothing more. Still ask the accountant how trades should be recorded.

### 3.4 "Do not bill" carries multiple meanings — **New**
The single "do not bill" plan type covers trades, and likely staff families and other arrangements, indistinguishably. **Requirement:** "do not bill" carries a reason (trade / staff / funded elsewhere / other) plus a note, so a report can list every do-not-bill family with why, and migrated records aren't ambiguous.

**Resolved (Round 3):** about 20 families. Reasons: trade, staff family, friends of staff. **Requirement:** do-not-bill reason as a short pick-list (Trade / Staff family / Courtesy / Other) plus a note.

### 3.5 Pool load visibility — **New** (from Eric)
There is a practical crowding limit per pool that is well below the health-department capacity and is never approached, but distribution across pools can get lopsided: e.g. Saturday 10:00, nearly every lesson is in the outdoor (big) pool. Staff would like to see how many lessons are in each pool at each time slot.

**Requirement:** a per-slot count by pool on the schedule board ("Big: 9 / Small: 2"). Informational only; no enforced cap. The data (pool + time on every lesson) already exists.

### 3.6 When a student moves from the small pool to the big pool — **New** (from Eric)
The package notes that "Either" is a transitional pool state but not what drives the transition. Eric's working rule: a student is ready for the big pool when they can go from floating to standing independently in the shallow end of the small pool, which usually corresponds to about **Level 4**, *and* they are tall enough to stand in the big pool's shallow end (about 3 ft). If they can't reach the bottom out there, they can't practise the float-to-stand skill, so moving them early is counterproductive. Timing is hard to predict because it depends on age, level, and height together.

**Requirement:** don't automate the decision. When a student reaches Level 4, surface them as "assess for big pool" to the instructor. Height isn't stored today; a simple instructor-confirmed checkbox ("can stand in big-pool shallow end") would be enough to record the readiness judgment as a dated event.

---

## 4. Card data: agreed plan

1. **Use Authorize.Net invoices for phone payments** so no staff member handles a card. Confirm the feature is on and agree who sends them. Until this is in place, staff will keep writing numbers down, so this is the first step.
2. Stop typing card numbers into FileMaker, including notes fields, from now on.
3. Restrict the card fields to full-access only via Manage Security (field-level "no access" for instructor / deck manager / data entry privilege sets).
4. ~~Move cards into Authorize.Net~~ Already done; every card is there. Replace FileMaker's full numbers with last four at Jen's pace; no sequencing risk.
5. Manual sweep of notes fields for fragments.
6. Find and clean old backups and export copies; the frozen archive should be made **after** the scrub.
7. Fix the unencrypted server connection; consider FileMaker encryption at rest.
8. Talk to Affinity24 about PCI obligations.

---

## 5. Open questions added this session

| # | Question | Who |
|---|---|---|
| 1 | ~~How are monthly card charges run today?~~ Resolved: from Authorize.Net. | — |
| 2 | ~~What does "online" mean?~~ Resolved: stored in Authorize.Net. | — |
| 3 | ~~Capitalized last names?~~ Resolved: noise; normalize. | — |
| 4 | ~~What drives `Name_First_calc`?~~ Resolved: `flag_Special_Needs`. | — |
| 5 | How many records hold a full 16-digit card number? | Developer (from export) |
| 6 | ~~Do-not-bill count and reasons?~~ Resolved: ~20; trade / staff / friends. | — |
| 7 | ~~Trade frequency?~~ Resolved: rare; note is fine. | — |
| 8 | ~~Held seats?~~ Resolved: see 3.1. | — |
| 9 | Is `flag_trashcan` used by the UI, and did the deletion incident bypass it? | Developer |
| 10 | Do pre-2020 Billing_Months rows carry stamped amounts? | Developer |
| 11 | How should the accountant record trades? | Accountant |
| 12 | Does `T06_Documents` hold the PDFs as containers, and how will they be extracted? | Developer |
| 13 | ~~Notes count?~~ Resolved: lightly used by design. | — |
| 14 | ~~Invoicing?~~ Resolved: enabled; Jen sends. Texting a payment link is a new-system requirement. | — |
| 15 | ~~Parent-caps convention?~~ Resolved: real, typed by hand; keep caps display driven by a flag. | — |
| 16 | ~~Enrollment hold window?~~ Resolved: until 5 pm the next day, then release slot and cancel invoice. | — |
| 17 | Can a hosted Authorize.Net payment link be generated per family and sent by SMS? | Developer |

Round 3 answers received September 2026 from Jen and Cindy.

---

## 6. Housekeeping still owed
- Empty the OneDrive recycle bin (onedrive.com → Recycle bin) to remove the CSV and the first Excel attempts.
- Confirm no other copies of the exports exist on the Desktop or in Documents.
- Finish the remaining table exports (Section 1).
- Hand the folder to the developer directly; never via project knowledge or a shared drive.
