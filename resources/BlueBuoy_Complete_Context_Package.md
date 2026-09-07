# Blue Buoy Swim School — System Replacement: Complete Context Package

**Purpose:** everything gathered so far about how the business actually operates, assembled so development can begin with the domain understood rather than discovered mid-build.

---

## How to read this document

**This is context, not a specification to implement literally.** The architecture recommendations are the weakest part and should be replaced by whoever is building. The *business findings* are the valuable part — they came from conversations with the people who run the school, and much of it exists nowhere in the software.

**Confidence levels are marked throughout:**
- **Confirmed** — verified in the DDR export, seen in a live screenshot, or stated directly by ownership/staff
- **Reported** — described by staff but not independently verified
- **Inferred** — reasoned from available evidence; treat as a hypothesis
- **Open** — genuinely unknown, listed at the end

**Known errors already corrected in this document** (recorded so the pattern is visible): an assumption that SMS capability had been lost when it hadn't; a guess that the prepay rate lock worked by script timing when it's fully manual; an over-designed authorization-tracking requirement for charter schools that doesn't match how funding actually works; a proposal to use lesson attendance for payroll verification that doesn't hold up. Several more were corrected by staff during review. **Expect more of these — verify before building.**

---

## How this was assembled

1. **FileMaker DDR export analysis** — the full Database Design Report for `BlueBuoy_FM.fmp12` (~40MB XML), plus the `20 Time` and `Instructor_Entry` companion files. Tables, fields, relationships, scripts, calculations, and layouts were parsed directly.
2. **Live screenshots** of the working system — office desktop and pool-deck iPads.
3. **Extended conversation with ownership** about daily operations.
4. **A written questionnaire answered by the scheduling and billing staff** (included in full below).

**The most important finding overall:** roughly a dozen significant business rules and workflows exist **nowhere in the database** — they live in staff knowledge, visual conventions, free-text notes, spreadsheets, and habit. No amount of code analysis would have surfaced them. Examples: the entire charter school billing operation, the manual monthly prepay adjustments, ALL-CAPS names signalling special needs, and colour highlights carrying safety requirements.

**Practical consequence:** continue asking the staff questions during the build. The discovery rate did not slow down.

---

## System at a glance

| | |
|---|---|
| **Current system** | FileMaker Pro, ~20 years of accumulated logic |
| **Main file** | `BlueBuoy_FM.fmp12` — 22 base tables, 341 table occurrences, 316 relationships, 340 scripts, 70 layouts |
| **Companion files** | `Instructor_Entry` + `Launcher_Teacher` (iPad apps, no data of their own), `fmSMS` (commercial bulk-texting add-on), `20 Time` (legacy roll sheets), plus several unidentified legacy files |
| **Scale** | ~9,428 student records; 13,729 families; 492,824 billing rows; 334,399 attendance rows |
| **Users** | Instructors (pool-deck iPads), deck managers, scheduling office, management |
| **External systems** | Humanity (staff scheduling/time), Paychex (payroll), QuickBooks + Excel (institutional billing), Authorize.Net + Affinity24 (card processing), fmSMS (texting) |

---

## Technical appendix: FileMaker system reference

Useful when reading legacy data or writing migration code.

### Lesson type codes
These appear throughout the schema — rate tables, make-up counters, discount tiers.

| Code | Meaning |
|---|---|
| `PR` | Private |
| `SP` | Semi-Private |
| `ST` | Stroke Prep (staff term; some fields say "Stroke Tech") |
| `GR` | Group |
| `PM` | Parent & Me |
| `AD` | Adult |

### Naming conventions
- `T##_` prefixes on table occurrences indicate the originating layout context (`T02_Students`, `T16b_months_RATES`) — an anchor-buoy relationship graph, not meaningful table names.
- Scripts are numbered by module: `0xxx` navigation/utility, `1xxx` students, `2xxx` staff, `3xxx` out lessons, `4xxx` lessons/attendance, `5xxx` billing, `6xxx` schedules, `8xxx` reports, `9xxx` settings.
- `OLD_*` columns (`OLD_STUD_ID`, `OLD_FAMILY_ID`) are artifacts of a **previous migration** — referential integrity on older records cannot be assumed.
- `flag_*` fields are booleans; `g_*` fields are FileMaker globals (session state, not data).

### Core entity relationships (verified join predicates)
- `Students.id_family = Families.ID_Family`
- `Lesson_Schedules.id_student = Students.ID_Students`
- `Lesson_Schedules.id_lesson = Lessons.ID_Lessons`
- `Lesson_Schedules.id_staff = Staff.ID_Staff`
- `Billing_Months.id_student = Students.ID_Students` **and** `Billing_Months.id_family = Families.ID_Family` (both populated — authority unclear)
- `Lesson_Attendance` joins to student, staff, lesson, and schedule simultaneously

### Key billing calculations (verbatim from the DDR)
```
Monthly_Fee = Round(
  (Rate_1 + ... + Rate_8 + Drop_Off_Rate_1 + Drop_Off_Rate_2)
  * (1 - Prepay_Discount), 0)

Monthly_Balance    = Monthly_Fee - (Amount_Paid_1 + Amount_Paid_2) + Adjustment_Credit
Cumulative_Balance = Monthly_Balance + Prev_Cumulative_Balance
```
`Rate_1`–`Rate_8` are the per-slot sibling discount tiers, computed via `Evaluate()` on dynamically constructed field names — effectively runtime `eval()`. `Rate_1` is full price; `Rate_2` less one discount step; `Rate_3` less two; `Rate_4`–`Rate_8` less three (capped).

**These are auto-enter calculations on Normal fields**, triggered by the lesson-type field — meaning rates are *stamped in and frozen*, not live lookups. This is why price changes don't propagate.

### Known data landmines
1. **Text-based instructor matching.** At least two relationships join on `Staff.Name_First = Instructor` rather than `id_staff`. Two instructors sharing a first name, or any renamed instructor, will silently misjoin.
2. **Dual billing keys.** `Billing_Months` carries both `id_student` and `id_family`; which is authoritative is undefined. Audit for rows where they disagree.
3. **ALL-CAPS names carry meaning** (see PRD 3.2). Extract before normalizing — this is irreversible if done in the wrong order.
4. **`OLD_*` columns** indicate a prior migration; verify integrity on older records.
5. **Free-text fields carry structured data**: invoice numbers and check references in billing notes, `8/27 offrd T` in waitlist notes, `$ OCT` for scheduled billing adjustments, UCI numbers and coordinator contacts in bold header notes.
6. **Zero-record tables** (`Lesson_Rates`, `Lesson_Out_Requests`) and FileMaker crash-recovery artifacts (`Recovered Library`) should not be migrated.
7. **Unknown values are real.** Students exist with no level, no age, and no payment plan. Don't default them.

### Data profiling still needed
Not answerable from the DDR — requires a CSV export:
- Actual date range of records; how much is genuinely active vs. historical
- Count of instructors sharing a first name
- Count of billing rows where student's family ≠ row's family ID
- Count of ALL-CAPS names, and how many correlate with `flag_Special_Needs`
- Active family count and real monthly card volume

---


# PART A — Product Requirements

*What the system needs to do. Business rules are high-confidence; architecture recommendations are not.*


## 1. User Roles & Permissions

The legacy system runs 9 accounts across 5 privilege sets. Analysis of the `Instructor_Entry` file (the actual iPad-facing app) surfaced a fourth role not visible in the main file — a **Deck Manager**, distinct from a rank-and-file instructor, who can search and act across *all* staff's schedules rather than just their own. The web app should use four roles, matching how the business actually operates (office desk vs. pool deck vs. deck supervision vs. administration):

| Role | Maps to legacy | Core access |
|---|---|---|
| **Instructor** | "Instructors" privilege set; confirmed via `Launcher_Teacher` | View their own daily/weekly roster; mark attendance for their assigned lessons, including **backfilling a missed day** by navigating to a past date; **freely switch the displayed schedule to any other instructor** with no re-authentication (a routine, frictionless action on shared iPads — see 1.2); view student notes relevant to their lessons (medical/special-needs flags); no access to billing, family contact info edits, or editing other instructors' schedules |
| **Deck Manager** | Confirmed via `Instructor_Entry` (`Open_Deck_Manager_Lesson_Search`, etc.) — the login credential itself is literally saved as "deck manager," confirming this is a distinct, named account type in daily use, not just a DDR inference | Everything an Instructor has, plus: search/view *any* instructor's schedule by day, time, lesson type, make-up status, or pool; issue make-ups and manage the waitlist from the deck; view payments-due and free-trial-conversion reports; log deck-level notes; create instructor schedule breaks |
| **Desk Staff** | "Data Entry Only" | Full student/family CRUD; create and edit class schedules; process make-up lesson requests and cancellations; view (but not necessarily edit) billing status; cannot change tuition rates or discount tiers |
| **Management / Admin** | "Full Access" | Everything Desk Staff has, plus: rate and discount-tier configuration; year-end billing rollover; staff account management; financial reporting (payments due, family balances); audit log access |

**Permission notes carried over from the legacy system:**
- The legacy DDR shows a manual audit-log pattern (`AUD_Create_Audit_Log`) rather than relying on platform-native change tracking — the new app should retain this as an explicit, queryable `audit_log` table (who changed what, when) rather than depending solely on Postgres's built-in row versioning, since staff/management will want to review it directly.
- Instructor access should be scoped to **their own assigned lessons only** — the legacy relationship graph joins Staff to schedules by `id_staff`, and in at least two places by instructor *name* instead of ID. The web app must enforce this scoping at the API/query layer using instructor ID exclusively (see Section 4 — this is a known legacy bug, not a pattern to repeat).
- Read-only "view student medical/special-needs notes" access for instructors should be limited to students on *their own* roster — not a searchable directory of all students. Deck Managers, by contrast, legitimately need broader visibility across students/instructors, since that's the point of the role.

### 1.1 Deletion Safety Controls
Prompted by a real incident: desk staff have accidentally deleted a student/family's entire record while viewing their account. The legacy system has no meaningful guardrail against this — a delete is immediate and permanent. This needs to be designed deliberately, not left as a default:

1. **No permanent deletion from normal staff roles.** Desk Staff and Deck Manager actions "remove" a student, family, or lesson slot by archiving it (an `is_archived`/`archived_at` flag), never a true database delete. An archived record disappears from active views and search but still exists.
2. **True/permanent deletion is Management-only**, and only reachable from an explicit "Archived Records" area — never a one-click action available while looking at an active account. This makes accidental deletion during normal day-to-day use structurally impossible for the roles most likely to trigger it.
3. **Destructive actions require explicit confirmation** — e.g. typing the student's name or clicking a clearly-labeled second confirmation step — for archiving a whole student/family record or deleting a whole day's worth of lesson slots at once. Routine single-field edits don't need this; whole-record removal does.
4. **A recovery window before anything is unrecoverable.** Archived records stay restorable (by Management, or by whoever archived them, within a short window) rather than requiring a database restore to undo a mistake.
5. **Billing and attendance history is never deleted, even when a family is archived.** A family becoming inactive shouldn't erase their payment or attendance history — that data has to survive for financial recordkeeping regardless of the family's active status.
6. The existing audit log (see above) already tells you *who* did something — this adds the ability to actually *undo* it, which the legacy system has neither of.

### 1.2 Fast, Protected Device Access
**Current state (confirmed with ownership):** `Launcher_Teacher` presents a login prompt that can simply be **cancelled** — the app opens to the schedule anyway. In practice there is **no authentication barrier** on the instructor-facing iPads today, which display student names, ages, levels, and profile notes including allergies and special-needs details. An iPad left in the poolside rack, or one that leaves the property, exposes all of it. This isn't cause for alarm, but it should be a deliberate decision in the new system rather than an inherited default.

**Critical workflow to preserve — identity and viewing context are different things.** Instructors routinely pick up *any* available iPad, switch the name selector to their own schedule, and **take their actual roll from it** — not just look. This happens daily by evening as batteries die, and it requires no login change today. This interchangeability is a hard requirement, and "frictionless" must cover the whole action, not just viewing:

- **Viewing context** — whose schedule is displayed. Switchable instantly, no re-authentication.
- **Acting on it** — marking attendance for your own lessons from someone else's device. Equally frictionless. This must never be gated.
- **Identity** — who is physically holding the device. Established once by PIN at shift start, primarily so a lost iPad isn't wide open, not as a gate on routine work.

**Device independence is a hard requirement.** Any instructor must be able to complete their roll from any available device at any time. This rules out binding devices to people ("Sarah's iPad") or requiring a specific device to complete a specific instructor's attendance.

If attribution is captured at all, it should be a passive byproduct — the lesson still belongs to its scheduled instructor, and the system may quietly record which session entered the record. It should never introduce a prompt or a barrier. (Worth confirming with staff whether attribution is wanted at all; the workflow matters more.)

**The everyday trigger for re-entry:** iPads sit in a slotted rack by the pool between lessons, and the top button routinely gets bumped when one is set into a slot, locking the screen. Waking it should not require a full login — the app hasn't closed, only the screen locked. Two things need to work together:

1. **Quick unlock via PIN**, not a full password, for getting back in day to day — a short numeric code is far more workable with wet hands or through a waterproof case than a keyboard.
2. **The session itself survives an app restart or the iPad powering off** — the device stays signed in underneath (a securely stored session token), so a restart only requires the quick PIN, not a full re-login. Losing power isn't the same as losing your session. A simple screen lock (the common poolside case) should need even less than that — the PIN screen appears on top of a still-running app, with nothing lost.
3. **Unlocking returns directly to where they were** — their current day's roster, not a home screen or menu they have to renavigate. The goal is that turning the iPad back on and entering a PIN gets an instructor back to taking attendance in seconds.
4. **Protection comes from limits around that convenience, not from removing it:**
   - The quick-PIN session stays valid for a bounded window (e.g., the day, or some hours of inactivity) — after that, a full login is required again, so a PIN alone can't grant indefinite access if a device is ever lost.
   - Genuine inactivity (iPad left untouched for a few minutes) re-locks to the PIN screen automatically.
   - Management can remotely revoke a specific device's session instantly — useful if an iPad is lost, or when a staff member leaves — without needing physical access to reconfigure it, which is a real gap in the legacy FileMaker Go account model.

### 1.3 Remote Access, Account Security & Offboarding
**Context:** the current FileMaker system is already accessible from the public internet (`fmp.bluebuoy.com`) — staff use it from home laptops and personal phones today. The web app does not introduce new exposure; it makes existing exposure explicit and manageable. Two current weaknesses it should fix outright:

- **Unencrypted connections.** The FileMaker host displays "Connection is not encrypted," meaning student and family data travels unprotected. Worth addressing on the legacy system immediately, independent of this project.
- **Shared credentials.** At least one account is a shared role login ("deck manager"). Shared logins make individual revocation impossible and destroy accountability — you cannot tell who did what, and you cannot remove one person's access without disrupting everyone.

**Requirements:**

1. **Individual accounts only — never shared logins.** Every person gets their own credentials. This is the foundation everything else depends on.
2. **Instant deactivation.** Disabling an account takes effect immediately, including terminating any active sessions on any device. A departing employee's access ends the moment the box is unchecked, not whenever their session happens to expire.
3. **Session and device visibility.** Management can see active sessions — who, what device, where, last active — and revoke any of them individually. This covers the lost-iPad case and the "did someone leave themselves logged in" case.
4. **Access logging.** Record logins (who, when, from what device and approximate location) and significant actions. Combined with the audit log in 1.0, this answers "who accessed this family's record last Tuesday?" — currently unanswerable.
5. **Multi-factor authentication for elevated roles.** Management and anyone with billing or bulk-export access should use MFA. Instructors on shared pool-deck iPads should not — the PIN model in 1.2 is the right fit there. Match the friction to the risk.
6. **Bulk export is the real data-loss risk, not day-to-day access.** A departing employee downloading the full student list matters more than them viewing a record. Restrict export by role, log every export (who, what, when, how many records), and consider alerting management on large exports.
7. **Automatic session expiry** for browser sessions, with a shorter window for billing/admin functions than for schedule viewing.
8. **A written offboarding checklist** — deactivate account, revoke sessions, confirm no shared credentials remain, review recent exports. A feature nobody remembers to use is not protection; the process matters as much as the capability.
9. **Optional, worth considering:** restricting billing and admin functions to known networks (office/home IPs), or alerting on logins from unexpected locations. Useful if the team is small and predictable; unnecessary friction if not.

**On monitoring generally:** the goal is accountability, not surveillance. Staff should know access is logged — that transparency is both fairer and a more effective deterrent than covert monitoring.

---

## 2. Core Feature Workflows


### 2.1 Pool Deck Attendance
Replaces the legacy `(1043) STU_Open_Attendance_Window` → `Lesson_Attendance` table flow, and is now directly confirmed by the actual iPad-facing app (`Instructor_Entry`) rather than inferred — that file has no data tables of its own; it's a thin UI layer pointing back at the same `BlueBuoy_FM` tables, which is the pattern worth carrying forward (a real client/API split, not a duplicated database).

1. Instructor opens their roster for the current day/session on an iPad (touch-first UI, must load in under 2 seconds — see Section 4 for why this is a hard requirement, not a nice-to-have).
2. Roster is a single pre-joined payload: student name, lesson time, lesson type, and any medical/special-needs flag — no live multi-table joins on load.
3. Instructor marks each student present or absent with one tap.
4. Marking a student **absent** immediately surfaces a "Schedule make-up?" prompt (this replaces the legacy `STU_New_Out_Lesson` → `STU_New_Out_Lesson_Finish` chain).
5. Attendance writes are optimistic and offline-tolerant: the tap registers instantly in the UI and syncs to the server in the background, queuing locally if pool-deck Wi-Fi drops. This directly replaces the legacy's confirmed server-offload pattern (`Create_Attendance_Record_PSOS` / `Remove_Attendance_Record_PSOS`), which exists for exactly this reason today.
6. **Deck-level notes**: staff on deck can log a quick note tied to a student or a lesson (confirmed via `STU_Create_Deck_Manager_Note`) — separate from a student's general profile notes. Keep this as a lightweight, timestamped note type in the new app rather than folding it into general notes, since it's clearly used for in-the-moment operational context (e.g. a pool closure, a same-day account change) rather than permanent student records.
7. **Payments-due and free-trial-conversion visibility** should be reachable from the same deck interface, not just the office — confirmed as an existing capability (`RPT_Payments_Due`, `RPT_Free_Trials_Mark_Read`) that desk/deck staff already rely on today.
8. **Backfilling a missed day.** Instructors can navigate to a previous date (not just today) and mark attendance retroactively via a dedicated catch-up action, confirmed as an existing workflow in `Launcher_Teacher` — needed for the common case of forgetting to take roll on the day itself. Backfilled records should be flagged as retroactive (date marked vs. date the lesson occurred) so reporting can distinguish same-day from after-the-fact attendance.
9. **Viewing the schedule works even with no internet at all**, not just queuing writes during a brief drop. The app should proactively cache **the full day's schedule for all instructors** on every device whenever it successfully syncs — not just the current user's roster. This matters because iPads are shared and batteries die: an instructor grabbing a colleague's device late in the day must still find their own schedule there, even if connectivity is also down. Cached data should be clearly marked as a last-synced snapshot, not live. Anything requiring a fresh server query (a new report, a full waitlist match) still needs connectivity. Attendance marked while fully offline queues locally and syncs once the connection returns.
10. **Two-way notes, confirmed live**: there are actually two distinct note channels, not one. A per-lesson "note to instructor/office" (shown with an unread-alert icon directly on the roster row) for quick operational flags, and a separate "Create Note to Scheduling Office" action from a student's full record for something that needs the office's attention specifically. The new app should keep these as two distinct, purpose-built channels rather than merging into one generic notes field — they're used differently (in-the-moment roster flag vs. a deliberate message to the office).
11. **Daily digest tools worth carrying forward**, confirmed live on the Deck Manager home screen: a "Free Trials" view with an unread-count badge (trials needing follow-up/conversion), a "Students with Start Date Today" view (new enrollments starting that day), and a capacity view showing available vs. total slots per instructor ("Total/Avail: 2/2") — directly useful for the waitlist-matching and availability-search features in 2.2/2.3, since instructor capacity is already tracked at this granularity.
12. **Account contact lookup from the roster.** Tapping a student's name opens a small popup showing who is on their account — with relationship labels ("Mom / Sylvia", "Dad / Jeff"). Instructors use this to know which adult they're speaking to at drop-off or pickup.
    - **Not always parents.** Grandparents, guardians, and other caregivers appear here. The data model should treat this as *account contacts with a relationship label*, not a fixed mother/father pair.
    - **Names only.** The popup deliberately does not expose phone numbers, email addresses, home addresses, or payment details — appropriate scoping for a shared device on a pool deck. Preserve that boundary; instructors need to identify the right adult, not access the family's record.
    - Contact details remain available to desk and management roles, per Section 1.

### 2.2 Make-Up Slot Assignment
Replaces the legacy `Lesson_Out` table and its associated MU-credit accumulator fields on Students.

1. When a lesson is marked absent, the system creates a **make-up credit** record (student, lesson type, date issued, expiration policy if any) — this replaces the legacy pattern of six separate accumulator fields on the Students record (`MU_GR_Total`, `MU_PM_Total`, etc.), one per lesson-type letter code.
2. Desk staff (or the family, if self-service booking is in scope) can view a student's available make-up credits and book them against any open slot matching the original lesson type.
3. Booking a make-up slot decrements the credit balance and creates the new scheduled session; cancelling a booked make-up restores the credit — mirroring the legacy `STU_Delete_Out_Lesson` reversal logic, including its conditional "do not re-issue" guard for cases where the make-up was cancelled for cause rather than a scheduling change.
4. Credits should carry an explicit type (matching the legacy PR/SP/ST/GR/PM/AD lesson-type codes, renamed to something readable) so make-up slots can only be booked into matching lesson types.
5. **Ad hoc availability search for phone-in requests.** When a family calls in looking for a make-up and gives a range of days/times rather than a specific slot, desk staff enter that range (plus the student's lesson type/age/level, pulled automatically from the student record) and get back a list of every open slot that fits — instead of manually scanning the schedule. This is a one-time, on-demand version of the same lookup used in Waitlist Matching (2.3) — same underlying "find open slots matching these criteria" logic, just triggered by a phone call instead of a stored waitlist entry, and with no need to save the search afterward. Worth building as one shared matching capability rather than two separate ones.

### 2.3 Daily Attendance Review & Coverage Check
**Confirmed with ownership.** Every day, after instructors take roll, **office staff review the previous day's entries and authorize them** to post to each student's account — applying level changes, pool changes, and make-up redemptions, and confirming each lesson taken is actually paid for.

This explains the `ATD_Update_Level_to_Student_Sched` / `ATD_Update_MU_to_Student` scripts, the `flag_update` fields, and the PSOS batch routines in the legacy system: attendance is captured by the instructor but doesn't propagate until authorized. **Two layers exist — what the teacher entered, and what's been accepted as true.** That gate is deliberate and worth preserving.

**But it should be exception-based, not a full daily sweep.** Most rows are "present, nothing changed." Auto-apply those; queue for review only what carries consequence:
- Level changes (affects eligibility, pairing, parent expectations)
- Pool changes
- Make-up redemptions (consumes a credit — errors cost money)
- Backfilled entries from a previous day
- Blank rows where nothing was marked
- Inconsistencies (marked present for a cancelled lesson; student appearing twice)

**Coverage check — lessons taken without payment.** The second half of this review confirms each lesson delivered is covered by *something*: a payment, prepaid credit, a make-up credit, or an institutional payer.

*Real example:* a family took a free trial, returned the next week for what should have been their first paid lesson, hadn't paid, and it was another week before payment arrived — the child swimming throughout. Not bad faith; simply invisible without a daily check.

This is what the `Unpaid Lessons` counters on the student record (broken out by SP/PR/ST/PM/GR/AD) are tracking.

**Surface it as an exceptions view rather than a manual sweep** — the system knows the lesson happened and knows what covers it:
- **Lessons taken with no coverage** — how many, and how long it's been running
- **Trial converted but not yet paid** — precisely the gap above
- **Prepaid credit nearly exhausted** — paid-through month approaching
- **Institutional students with no purchase order** for the current month (the same problem on the charter side, currently driving month-end calls)

The unifying concept: **lessons delivered without coverage**, whoever the payer is. Catching it on day two rather than week three is the difference between an easy conversation and an awkward one.

### 2.4 Waitlist Matching
Automates a comparison staff currently do by eye. The legacy `Waitlist` table already carries nearly every field this needs (`Student_Age`, `Student_Level`, `Student_Gender`, `Lesson_Type`, `Day`, `Time_Start`, primary/secondary instructor preference, `Priority`, `Date_Drop`) — this feature connects those fields together rather than introducing new data.

**Staff stays in control — this surfaces candidates, it does not auto-book.** Fit isn't fully capturable in data (teacher/student chemistry, sibling dynamics, a family's actual flexibility vs. what they originally told the desk), so the system's job is to narrow a large list down to a short, ranked one for a human to decide on — never to book automatically.

Two lookup directions, both needed:
1. **Opening → candidates.** When a slot opens (a drop, a confirmed cancellation, or a planned future drop via `Date_Drop`), show every waitlisted student whose age, level, lesson type, and stated availability could fit — ranked by `Priority` and request date, with `flag_push_to_top` as a manual override. Two-week lookahead on planned drops lets staff reach out before the slot is actually empty.
2. **Student → all openings.** For any single waitlisted student, show every open or upcoming slot that matches their age/level/lesson type — **not limited to the availability window originally on file.** Parents routinely turn out to be more flexible than what they told the desk initially, so this view should default to showing all qualifying openings, with the stated window as a filter staff can apply or ignore, not a hard boundary the system enforces on its own.

Every match in both views is a suggestion staff act on manually (contact family, confirm, then book) — the system never contacts a family or reserves a slot on its own.

### 2.5 Make-Up Requests & the Offer Queue
**Confirmed with ownership.** Make-ups are booked **one week out**. Families currently request by phone or email; the office looks up options manually and replies.

**Two kinds of availability, both maintained:**
- **Standing availability** — a family's general day/time flexibility, kept on their profile. Used for *proactive* matching: when a slot opens, who could take it. Treat as a **ranking signal, not a filter** — families routinely turn out more flexible than what's on file, so never hide an option because stored availability doesn't cover it. Timestamp it and prompt periodic refreshes.
- **Per-request availability** — what a family submits for a specific week when asking for a make-up. Short-lived and specific.

**The request workflow:**
1. Family submits availability for the coming week (via portal, or entered by staff from a call/email).
2. **System validates they hold an unused make-up credit of the right lesson type** before queueing — no point routing a request that can't be fulfilled.
3. Office is notified; the request arrives with **matching slots already populated** — ranked by closeness to their stated availability, wider matches shown below rather than hidden.
4. **Office curates.** Staff drop anything that's a poor fit for reasons the system can't know — instructor chemistry, student pairing, sibling logistics. This step is deliberate and stays.
5. Curated options go to the family by text or email.
6. Family accepts one; it books, and the credit is consumed.

**This already exists as a manual convention.** A live waitlist row showed `8/27 offrd T` — "offered Tuesday, 8/27" — recorded as free text in a notes field, alongside a drop date. So staff are already running an offer process by hand; the design below formalizes what's being done rather than introducing a new workflow.

**Slot contention — sequential offers, not simultaneous:**
A slot is offered to **one family at a time**. If they don't respond within a set window, the offer expires and **automatically advances to the next candidate** in the queue. Requirements:
- A **configurable response window** (confirm the right duration with staff).
- The slot is **genuinely held** during an active offer, so no double-booking is possible.
- **Automatic cascade** on expiry — staff shouldn't have to notice and re-offer manually.
- **Staff visibility** into where a slot sits in its queue: who holds the current offer, how long remains, who's next.
- Staff can **override the queue order** — priority cases exist.

**When nothing matches:** the office should see that immediately and respond in one action — rather than discovering it by scanning an empty list. Offer to carry the request into the following week, or add the family to a notify list for that slot type.

**Proactive use of the same engine:** when a slot opens unexpectedly, standing availability lets the system surface families who could take it — turning banked, unused make-up credits into filled lessons. (Relevant given one student was found holding 28 unused credits.)

### 2.6 Search & Filtering Capability (Do Not Regress)
**Confirmed from a live screenshot of `L008_Deck_Manager_Search`:** staff are using FileMaker's native Find mode directly — compound find requests, Include/Omit logic, query operators, multi-request searches, sorting, and Saved Finds. This is a power tool, and it is the engine underneath the waitlist matching (2.3) and ad hoc make-up search (2.2).

**Searchable fields observed:** student name, search group, age, level, pool, lesson type, make-up flag, hold status, hold notes, start date, end date, instructor, time, day, instructor gender, lesson notes, and **Total/Available capacity** — plus a Group vs. Non-Group toggle distinguishing group lessons from private/semi-private.

**This is the highest adoption risk in the whole project.** The common modernization failure is shipping clean filter dropdowns that cover most cases, then discovering staff relied daily on a compound query the new UI can't express. Everything else can improve and the system will still be called "worse than the old one." Requirements:

1. **Match or exceed current query power**, including: multiple criteria across all the fields above, negation/exclusion ("all Level 5 semi-privates on Friday, *excluding* anyone on hold"), date ranges, and numeric comparison on capacity.
2. **Don't require FileMaker knowledge to get that power.** Today staff must understand find requests and operator syntax. The new app should express the same logic through a UI that doesn't assume prior training — power without arcana.
3. **Saved searches are a real feature, not a nice-to-have** — the presence of Saved Finds suggests staff run the same queries repeatedly. Worth asking which ones; those become named presets ("Fridays with openings," "students on hold over 30 days").
4. **Capacity is a first-class search dimension.** That `Total/Avail` field is searchable today, which means "show me where I actually have room" already works. The waitlist and make-up matching features depend on this and should build on it rather than reinvent it.
5. **Group vs. non-group is a distinguishing dimension** throughout — confirm with staff whether group lessons have separate scheduling/pricing rules not yet captured in this document.

### 2.7 Family Tuition & Billing
Replaces the legacy `Billing_Months` / `Billing_Years` monthly ledger and the `Preferences`-driven rate/discount tables.

1. Each family has a running monthly ledger: tuition charged, discounts applied, payments received, and running balance — directly modeled on the legacy `Monthly_Fee` → `Monthly_Balance` → `Cumulative_Balance` chain, since that rollover logic is sound and worth preserving.
2. Tuition for a given student/lesson slot is computed from a rate table (rate per lesson type, per year) plus the multi-child/multi-lesson discount (see Section 3).
3. Stripe Billing handles payment collection, card storage/tokenization, recurring charge scheduling, and dunning/retry logic. **The database remains the source of truth for the computed invoice amount** — the app calculates what's owed (rates + discounts), and hands that number to Stripe to collect; Stripe does not compute pricing.
4. Desk staff and management can view family balances, payment history, and outstanding amounts; only management can adjust rates or issue manual credits/adjustments.
5. **Payment plan types, confirmed from the DDR.** Families fall into several distinct arrangements, not one: monthly auto-charge (`CC Monthly` / `Auto CC`), prepay, card-on-file-pending, and explicit do-not-bill. **Prepay carries a tiered discount** — the system offers 0%, 5%, 10%, 15%, 20%, 25%, 50%, and 100% steps, applied as a multiplier against the computed monthly fee. Confirm with the billing team which tiers are actually in current use and what determines the tier (prepay length? lesson volume?), since the value list is broader than what's likely used day to day.
6. **Payment and adjustment types to support**, confirmed from the DDR: Auto CC, Credit Card, Check, Cash, Direct Deposit, Transfer Credit, Adjustment, Carryover balance, Referral Credit, Refund, Reversal, Gift Certificate (both physical and online), NSF Check, No Charge, Late Fee, and house credit. The new system needs a proper **transaction/adjustment ledger** supporting all of these — not just "amount paid" fields. Note the current design only allows **two payment slots per month** (`Amount_Paid_1/2`), which is a real constraint the new model should remove.

### 2.8 The Monthly Billing Run
**How it works today (described by ownership):** the month-end "auto billing" is substantially manual. The current sequence:

1. **Manually post each family's lesson type for the month** — this is what triggers the rate auto-enter calculation. Billing does not derive from the schedule.
2. **Manually compute prorated amounts** for families taking a partial month (e.g. only a couple of lessons).
3. **Cross-reference a spreadsheet from the credit card processor** against what the system says each family should be charged, line by line.
4. **Manually reset families who received referral credits** back to their normal monthly fee for the following month.
5. **Handle voids and refunds** for families who cancel after processing — roughly a one-week window.

This runs alongside the per-family prepay adjustments described in 3.4, making month-end the most labor-intensive and error-prone process in the business.

**Confirmed with the billing team:**
- **Time cost: 6–7 hours in a normal month; 10–12 hours across two days in summer** (peak enrollment). Roughly 100 hours a year.
- **The worst step is posting each family's lesson type and getting the tier right** — the single highest-value thing to eliminate.
- **Credit card mismatches occur every month** (a small number), almost always caused by a staff change made without notifying billing.
- **The office fails to communicate a mid-month change 1–2 times per month.** Discovered only when the next billing run is reviewed, after charges have gone out — requiring a separate correction charge and a fix to the auto-billing.
- **Mid-month lesson type change rule:** prorate at whatever tier the student is currently in (e.g. Parent & Me 1st tier → Semi-Private 1st tier).
- **Referral credit resets are tracked with a "$ OCT"-style key note** — a text reminder that an adjustment is due in the named month. Rarely missed, but entirely dependent on a person reading and acting on a note.
- **Refund/void practice:** refunds are given after the 1st but before that week's scheduled lesson. Deliberately flexible — sometimes a make-up is offered instead of a refund, at staff discretion. Preserve this discretion; don't automate it away.
- **Prorated amounts are needed occasionally**, most often at end of summer when families stop mid-month for the school year.

**Failure modes this creates:**
- A missed referral-credit reset means a family is silently under-billed **indefinitely** — nothing flags it, and it compounds each month.
- Reconciliation is a manual comparison between two systems that cannot talk to each other; a discrepancy is found only if someone spots it.
- Proration is computed by hand, so it's inconsistent and unauditable.
- Every step scales linearly with family count.

**Design requirements:**

1. **Charges derive from the schedule, not from manual monthly entry.** The system already knows each student's scheduled lessons and type. Monthly posting of lesson type should not exist as a task.
2. **Proration is computed automatically** from actual scheduled lessons in the period, with the calculation visible and auditable rather than done by hand.
3. **One-time credits expire by design.** A referral credit applies to a specific month and does not carry forward. Manual reversal should be impossible to forget because it isn't a step. Any credit that *should* recur is configured as recurring explicitly.
4. **Payment reconciliation is automatic.** Stripe reports charge outcomes (succeeded, failed, refunded, disputed) directly back into the ledger. The credit-card spreadsheet cross-reference disappears entirely; only genuine mismatches surface, as flagged exceptions.
5. **Void and refund are first-class actions** with a defined window, reason codes, and audit trail — not a manual out-of-band correction.
6. **The billing run becomes a guided workflow**, not a checklist held in someone's head:
   - **Preview** — what will be charged, to whom, totals
   - **Exceptions** — new students, mid-month changes, holds, expiring rate locks, unusual amounts, families with a balance
   - **Approve** — a human reviews and confirms
   - **Execute** — charges submitted
   - **Reconcile** — outcomes recorded automatically; failures surfaced for follow-up

   The reviewing step is preserved deliberately. The goal is to remove the clerical work while keeping human judgment over what gets charged.

### 2.9 Third-Party Payers (Charter Schools & Regional Center)
**Confirmed with the billing team.** This is entirely absent from the FileMaker system today — it runs on QuickBooks, Excel, paper, and the charter schools' own portals.

**Charter schools — how it actually works:**
- Rates are negotiated **around July** for the coming school year, under contract with each charter school.
- Charter rates are **higher than the auto-pay monthly rate**, deliberately, because payment is delayed.
- **Families obtain their own funding/purchase orders** — Blue Buoy has no visibility into or authorization over the family's funding. *(This corrects an earlier assumption: there is no authorization balance to track or warn against.)*
- At the **end of each month of lessons**, Blue Buoy invoices against the purchase order.
- **Two different submission workflows:** some charter schools require an emailed/paper invoice; others require confirming lessons taken through **their own portal**.
- Payment often arrives **a month or more later**, sometimes longer for new contracts.
- **No supporting documentation is required** to release payment — no attendance sheets or service logs.

**Regional Center:**
- Funding contracts are typically **annual**, arranged by the family (with Blue Buoy's help).
- Rates are kept **similar to the auto-monthly rate**.
- **Some agencies require invoices; at least one sends checks directly** without invoicing.
- Students carry a **UCI number** (Regional Center identifier) plus **coordinator contact details** (name, phone, email) — currently stored as bold notes at the top of the family account.

**Mixed payers within one family are common and must be supported:**
- One child funded by a charter school, a sibling paid out of pocket
- Regional Center for one child, charter school for a sibling
- **Deliberate tier strategy:** where a family has both, the charter/agency-funded student is placed in the **first (undiscounted) tier**, so the out-of-pocket sibling receives the tiered discount and the family's own cost is lower. This is intentional and the new system must let staff control tier assignment order rather than assigning it automatically.

**Collections in practice:** rather than tracking authorizations, staff **text or call families near month end** when no purchase order has appeared, to confirm whether they're continuing. Unpaid departures are rare. **The most frustrating part is payment delay**, not collection.

**Requirements for the new app:**
0. **Invoice and payment tracking currently lives in a free-text notes column.** Confirmed from a live payments screen: entries read `JAN 11237 $368`, `FEB 11257 $368 (sent 1/15)`, `MARCH INV 11309 $368 (sent 4/2)`, alongside check references (`CK 7499`, `MAX CK 4953`). **This is the entire accounts-receivable trail for institutional payers** — invoice number, amount, send date, and payment reference, all as unqueryable text in a monthly notes field. Nothing can report on what's outstanding, how long it's been outstanding, or which invoices were paid by which check. Structuring this is the single biggest improvement available on the payer side.
1. **Payer as a first-class entity** separate from the family — family, charter school, or Regional Center agency, assignable per student.
2. **Per-payer configuration**: contract rates (set annually, July for charters), submission method (invoice vs. portal vs. direct payment), and billing contact.
3. **Manual tier assignment control** so the sibling-discount strategy above can be applied deliberately.
4. **Month-end invoice generation per payer**, batching that payer's students for the period.
5. **Accounts receivable aging** — what's outstanding, per payer, and for how long. This is the actual pain point: visibility into delayed payments.
6. **A month-end prompt listing enrolled institutional students with no purchase order yet**, replacing the manual check that currently drives those calls and texts.
7. **Payment recording that reconciles with QuickBooks** rather than replacing it — confirm with the team whether QuickBooks stays as the accounting system (recommended) and what the handoff should look like.
8. **Store UCI numbers and coordinator contacts as structured fields**, not free-text notes.
9. **Access sensitivity.** Regional Center involvement indicates a student's developmental-disability status. Restrict payer detail to billing/management roles; keep it off general rosters.

### 2.10 Broadcast Notifications
Today this already exists as a real bulk-send tool, not a manual one-by-one process — desk staff find/select a set of student records on screen, then run a bulk-SMS action that hands the whole selected list off to a separate FileMaker file (`fmSMS`) to actually send. **Confirmed directly**: `fmSMS` is a commercial FileMaker add-on from Databuzz (not custom-built), which itself is just an interface — it doesn't send messages itself, it connects to one of roughly 20 supported third-party SMS gateway providers (Twilio, ClickSend, MessageMedia, etc.) that the business has a separate account with. This is good news for the rebuild: **the new app likely doesn't need Databuzz/fmSMS involved at all** — it can call whichever underlying gateway provider is actually configured directly from its own API. **Next step: check the Accounts/Gateways tab inside fmSMS** to identify which specific provider is connected — that single detail resolves whether to keep using that same vendor (less disruption, existing account) or deliberately switch as part of the rebuild. The underlying data needed either way already exists: `Pool` is already a field on Lessons/Lesson_Schedules, and `Families` already carries `Phone_Text`, `Email_Primary`, and `Email_Secondary`.

1. Desk staff or management select an **audience** by one of: a specific instructor's full schedule (for a sub notice), a specific pool/location for a given date (for a closure), or a specific date range/lesson type — then optionally narrow further before sending.
2. The audience is built by querying active, currently-scheduled students matching the selection — not a static list — so it's always correct for "today" without anyone maintaining a separate contact list.
3. Staff see a **preview of who's included** (names, count) before sending — never a silent blast — with the ability to remove individual recipients.
4. Message goes out by text and/or email, using either a quick free-text message or a saved template (e.g. "Sub notice," "Pool closure") for common cases.
5. Delivery status (sent/failed per recipient) is visible afterward, so staff know if someone needs a manual follow-up call.
6. **Inbound replies — a confirmed staff request.** Today families are explicitly told **not to reply** to texts and to call instead, because replies go nowhere anyone sees. Staff would like notification when a family replies. Requirements:
   - Capture inbound replies and attach them to the family/student record.
   - Notify desk staff when a reply arrives.
   - Stop telling families not to reply — a text that can't be answered is a worse experience for them and generates phone calls that a reply could have resolved.
   - Note: fmSMS already has a **Replies** tab, so the underlying gateway likely supports this. It's plausible this capability exists today and simply isn't surfaced or monitored — worth checking before building.

### 2.11 Instructor Availability, Qualifications & Coverage

**Nothing exists today.** The Staff table has no hours, days, or availability fields — only name, contact, role, CPR certification, and active status. Availability is *implied* by which lesson slots happen to exist. Consequences: nothing knows an instructor doesn't work Mondays; nothing prevents creating a 6am slot; and matching can only find **existing empty slots**, never "times this instructor could teach but nothing is scheduled yet." That last point limits the waitlist and make-up features directly.

**Boundary with Humanity:** staff shift scheduling, on-call availability, and guard shifts live in **Humanity** and stay there. The new app should not attempt to own staff availability it cannot be authoritative about.

**What the app should own:**

1. **Regular teaching hours** — each instructor's normal teaching window per weekday, with date-effective changes (availability shifts seasonally). This enables "could a lesson go here?" rather than only "is this slot empty?" It's about lesson scheduling capacity, not staff employment hours, so it doesn't duplicate Humanity.
2. **Teaching qualifications** — which lesson types and levels each instructor can teach. Humanity has no idea about this and neither does the current system; it lives in staff knowledge. It's the missing input for both routine scheduling and finding substitutes.
3. **Breaks within a schedule** — the legacy `flag_has_break` / `Create Break` mechanism carries over.

**Known limitation:** because guard shifts live only in Humanity, the app **cannot detect** a lesson scheduled during an instructor's lifeguard shift. Today staff knowledge prevents this. Options if it proves to be a real problem: a read-only import of shift data from Humanity (if its API allows), or accept the limitation. **Confirm whether this conflict actually occurs before building for it.**

### 2.12 Emergency Coverage (Teacher Call-Out)
**Real scenario:** a teacher called out at lunch before a 2pm shift. With no on-call sub available, staff redistribute that teacher's students into other instructors already on site, wherever a fit exists.

This is the **fourth use of the same matching engine** (with waitlist, ad hoc make-up search, and the offer queue) — but it has distinct characteristics:

- **It's a re-allocation puzzle, not a lookup.** A whole shift is placed at once, and each placement consumes capacity affecting the next. The system must track remaining capacity as staff work the list, not match against a stale snapshot.
- **Constrained to instructors already on site** for that shift — not all qualified staff.
- **Time-pressured**, often handled from a phone. Different UI demands than desktop scheduling work.

**Requirements:**
1. **Find matches within a configurable time window** — default ±20 minutes, ranked closest-time-first, with wider options shown below rather than hidden (parents often flex more than expected).
2. **Respect qualifications and eligibility** — the covering instructor must be able to teach that lesson type and level.
3. **Keep siblings together.** Placing two children from one family 40 minutes apart creates a new problem for that parent; treat them as a unit.
4. **Handle the students who can't be placed** — those lessons are cancelled, which means issuing make-up credits and notifying parents. One workflow: place who you can, auto-issue make-ups for the rest, then message both groups in a single action (ties to 2.10).
5. **Suggest, never auto-assign.** Parent agreement is required, and instructor/student fit remains a human judgment.

### 2.13 Level & Pool Assessment
**A design flaw worth fixing deliberately.** Instructors currently take roll *by selecting the student's level for that day's lesson* — so the level field is touched at every lesson. This means the data is never stale, but it can be **falsely fresh**: "the teacher assessed this and it's still Level 5" is indistinguishable from "the teacher tapped the pre-filled value at the end of a long shift."

That's worse than obviously-old data, which at least announces itself. The office then pairs students on levels it reasonably believes are current — and a mismatch surfaces at the poolside, in front of a parent.

This is a design problem, not a staffing one: a pre-filled default that must be selected to complete a required task will produce pass-through selections regardless of diligence.

**Requirements:**
1. **Separate the fact from the judgment.** Marking attendance is a fact — one tap, no level selection required to complete roll. Changing a level is a judgment — a distinct, easy, *optional* action that isn't a gate on finishing.
2. **Record level changes as dated events** ("moved to Level 6 on Aug 12, by Eric") rather than overwriting a field. This yields real progression history and makes *last actually changed* a meaningful number instead of *last touched*.
3. **Periodic deliberate prompts** replace constant implicit ones: "It's been 7 weeks since Emma's level changed — still Level 5?" An occasional question gets genuine thought in a way a per-lesson dropdown never will.
4. **Show data age at pairing time.** When the office matches two students, display when each level was last confirmed. A level changed last week and one untouched since March should not look identical.
5. **Warn on mismatch at scheduling time**, not at the pool — if paired students differ in level or pool beyond normal tolerance.
6. **Pool assignment follows the same rules.** Note that **"Either"** is a legitimate transitional state (a student moving toward the big pool), not an unresolved question — distinguish "either works" from "nobody has decided," ideally with a date so students don't sit in limbo.
7. **Confirmed mechanism:** the attendance grid stores **the student's level in each weekly cell** (a level number, or `A` for absent), organized by lesson type across the year. That's why level selection is bound to roll-taking — and it's a genuinely useful record of progression over time. Preserve the *history* while decoupling the *act* per points 1–3 above.
8. **Unknown values must be representable.** A sibling record showed age as `?`, and newly registered students appear with **no level and no payment plan assigned yet**. The schema must allow level, age, and payment plan to be genuinely absent rather than defaulting to a value — an unassessed student is not "Level 0."

### 2.14 Parent Portal
**Nothing exists today** — all parent interaction is by phone, email, or conversation at the pool, and most scheduling happens off-site.

**Framing that matters:** the portal's job is **not** to let parents schedule themselves. It's to replace unstructured email and voicemail with structured requests. A make-up request arriving through the portal carries the student, their credit balance, and their availability already attached — the office still decides everything, but stops doing data entry to reach the decision.

**Phased by value per unit of effort:**

1. **Digital intake and waivers** — likely the highest ROI, and not primarily about parent convenience. Photo consent, medical info, allergies, emergency contacts, and authorized pickup captured directly from the parent instead of transcribed from paper. Fixes the "NO PHOTOS lives in a free-text note" problem at its source. One-time interaction, so adoption isn't a barrier.
2. **Read-only account view** — make-up credit balance, current enrollment, paid-through month, upcoming lessons. Pure information, no workflow, eliminates a category of phone call. Nothing can go wrong.
3. **Availability maintenance** — parents keep standing availability current (see 2.5); they benefit directly through faster make-up offers.
4. **Structured requests** — make-up, cancellation, hold. Creates a queue; books nothing. Staff retain control.

**Out of initial scope: self-service booking.** Fit involves judgment the system can't make.

**Honest costs:** parents who can't log in will call about *that* — this adds a support surface as well as removing one. Adoption will be partial, so phone and email continue regardless. And a portal creates an expectation of responsiveness that voicemail doesn't: a request visibly sitting unanswered for three days feels worse than one that vanished into an inbox.

**Recommendation:** ship items 1 and 2 as a small first release; expand only after observing real usage.

### 2.15 Documents & Forms (Per Student)
**Confirmed from live screens.** Each student record has a Forms tab with document slots. Four exist — Registration & Liability, Payment, Other, Withdrawal — but **only Registration & Liability and Withdrawal are used**. Documents arrive either from website registration or on paper at the pool and are uploaded per child, with a submission date.

**Requirements:**
1. **Per-student document storage** with type, submission date, and preview — carrying forward the two types actually in use.
2. **Don't rebuild unused slots.** Payment and Other are dead; replace with a general attachment capability rather than fixed empty categories.
3. **Military ID upload — a requested addition.** Families with a military discount need somewhere to attach proof. This implies a **military discount** exists that isn't yet captured elsewhere in this document; confirm the discount amount and how it interacts with sibling and prepay discounts.
4. **Digital intake ties in directly** (see 2.14) — registration and liability captured through the portal lands here automatically instead of being uploaded by staff.

### 2.16 Notes History (Instructor & Deck Manager)
**Confirmed from live screens.** A dedicated tab holds a **permanent, dated history** of notes in two separate channels:
- **Notes From Instructor** — date, instructor name, lesson type, day, time, and the note text
- **Notes from Deck Manager** — timestamp and note text

Notes carry an action control (dismiss / acknowledge), and history is retained indefinitely for reference. This confirms the two-channel design in 2.1 and adds an important property: **these are a durable record, not transient flags.**

**Critically — chemistry and fit are already being recorded.** Real examples include *"Bad match"* against a specific instructor, and notes about a student regressing with a particular pairing. Earlier this document assumed instructor/student fit was judgment the system couldn't hold. It can, because staff already write it down.

**Requirements:**
1. **Preserve both channels with full history**, dated and attributed.
2. **Feed prior notes into the matching engine.** When suggesting a make-up slot, waitlist match, or emergency substitute, the system should **surface prior negative-match notes** for that student/instructor combination — and rank accordingly. This makes 2.4, 2.5, and 2.12 meaningfully better than the manual process rather than merely faster.
3. **Structured "do not pair" flag.** Free-text "bad match" notes should be complemented by an explicit student↔instructor exclusion staff can set, so matching can honor it reliably rather than depending on text parsing.
4. **Acknowledge/dismiss states persist** — a note acted on should be visibly resolved without being deleted.

### 2.17 Student List Conventions (Confirmed)
The student list panel encodes information visually:
- **Green dot** = actively enrolled. **No dot** = not currently enrolled.
- **Blue name beneath the student** = the parent's first name — how staff disambiguate similar student names at a glance.
- Search by last name surfaces similar-beginning matches, not exact matches only.
- **ALL-CAPS student names** appear here too (see 3.2).

**Requirements:** carry all of these forward as explicit, labeled UI (enrollment status badge, parent name line, fuzzy last-name search) rather than color/typography alone — same reasoning as 3.2.

---

## 3. Business Rules

### 3.1 Lesson Types, Class Structure and Eligibility
**Lesson type codes** (decoded — these appear throughout the legacy schema in rate tables, make-up counters, and discount tiers):

| Code | Class | Group? | Eligibility | Capacity |
|---|---|---|---|---|
| `PR` | Private | No | — | 1 |
| `SP` | Semi-Private | No | — | 2 |
| `PM` | Parent & Me | **Yes** | Age 3 and under *(confirm)* | 6 |
| `GR` | Group (staff also call this Stroke Prep) | **Yes** | Age 7+ **and** Level 9+ | 6 |
| `ST` | Stroke Technique | **Yes** | Age 10+ **and** Level 10+ | 6 |
| `AD` | Adult | *Unknown* | *Unknown* | *Unknown* |

**Three distinct group class types**, all capped at **6 students**. Confirmed with ownership.

**Schema implication — no special handling needed.** The legacy `Lessons` table already carries `Slots_Total` and `Slots_Available`, with `Lesson_Schedules` linking students to a lesson. A group class is one lesson record with 6 seats and up to 6 student rows attached — structurally identical to a private (1 seat) or semi-private (2 seats). **Capacity is simply a per-type number.** This is what the "Total/Avail" figures on the Deck Manager search display.

**Matching implication — this does change the search logic.** For group and semi-private types, "is there an opening?" means *is there a free seat in an existing class*, not *is this time slot empty*. Every matching feature (2.4, 2.5, 2.12) must evaluate **remaining capacity**, not emptiness — and for groups, must also check that the student's level fits the class.

**Open questions affecting scheduling logic** (see questionnaire):
- Minimum enrollment — does a group with one student run, get cancelled, or merge?
- Does price vary with how full a class is?
- Does a group student occupy a sibling-discount tier slot the same way a private student does?
- Is Adult group or individual, and what is its capacity and eligibility?

**Eligibility requirements** — certain class types have age and skill-level prerequisites. Values below are **approximate and need confirmation with ownership/staff before building**:


**Age representation — important detail:** ages display as **decimal years, base 10** (e.g. `3.9` ≈ 3 years 11 months), *not* years-and-months. Misreading `3.9` as "3 years 9 months" produces wrong eligibility results, and wrong in the risky direction near the age-4 threshold. Age is computed from date of birth (already stored), so the new app should keep deriving it rather than storing it — and should consider displaying it unambiguously (e.g. "3y 11m") while keeping the decimal form available, since staff are used to it.

**Swim diaper requirement (safety/hygiene policy):** all students **under age 4** must wear both a disposable *and* a reusable swim diaper in the pool. Today this is conveyed by highlighting the age field on the roster — a business rule encoded as a background color.

- Surface this as an **explicit labeled badge** on the deck roster, not color alone. Color doesn't survive printing or screenshots, isn't reliable for colorblind staff, and can't be searched or reported on.
- Because it's keyed to age, the requirement **ends automatically when the student turns 4** — no manual cleanup needed.
- Worth surfacing at enrollment/intake too, so parents know before the first lesson rather than at the pool.

**Age thresholds drive several rules at once** — the diaper requirement (turning 4), aging out of Parent & Me, Group eligibility (7), Stroke Tech eligibility (10). Handle them with one shared mechanism: thresholds as configurable data, evaluated continuously, with upcoming crossings surfaced proactively rather than discovered late.

**Design requirements:**
1. **Eligibility is a modeled rule, not tribal knowledge.** Store min/max age and min level per lesson type as configurable data, so requirements can be adjusted without code changes. Note that bounds run both directions — Parent & Me has a ceiling, the others have floors.
2. **Validate at scheduling time.** When a student is placed into a class type they don't qualify for, warn clearly — but allow an override with a reason (management judgment should beat a rule; there will be legitimate exceptions).
3. **Waitlist and make-up matching must respect eligibility**, not just lesson type. A student can't be matched into a Group slot they don't yet qualify for — this is an additional filter on top of the matching logic in 2.2 and 2.3.
4. **"Almost eligible" is a valuable report.** Students one level away from qualifying for Group or Stroke Tech are a natural progression conversation with parents, and a retention lever. The data supports this today; nothing surfaces it.
5. **Aging out needs proactive handling.** Because Parent & Me has an age ceiling, students continuously age out of it. The system should flag upcoming transitions ("these students turn 4 next month") so staff can plan the move rather than discover it late.

### 3.2 Information Encoded in Formatting & Color (Migration-Critical)
**Confirmed with staff.** Meaning is encoded in typography and color in several places. None of this is visible to database analysis — it exists only in layout formatting and staff knowledge.

**In the data itself (migration-critical — capitalization travels with the record):**
- **Student first name in ALL CAPS** = special-needs student. (Verified: a record showing `BRANDON` also had "Special Abilities" ticked.)
- **Parent first name in ALL CAPS** = staff shorthand for a difficult account.
- **Bold text at the top of a family account** = permanent information that persists year to year — e.g. Regional Center notes, **UCI number** (the student's Regional Center identifier), and coordinator contact details (name, phone, email).

**Display-only conventions (not in the data, but carry real meaning):**
- **Age field highlighted** = student is under 4, so **swim diapers required** (disposable *and* reusable).
- **Blue** on a profile = boy; **pink** = girl.
- **Red highlight on a note** = needs attention.
- **"$ OCT"-style key notes** = a reminder that a billing adjustment is due in the named month. This is how referral-credit resets are tracked — a text convention standing in for a scheduled task.

**Why the data-embedded ones are migration-critical:** capitalization is part of the stored value. Migrating names as-is makes `BRANDON` permanently his name, appearing on invoices and parent-facing output. Auto-normalizing first destroys the signal, which is recorded nowhere else. **Order matters: extract the meaning, then normalize.**

**Design requirements:**
1. **Every one of these becomes a structured field or badge.** Special-needs flag (already exists as `flag_Special_Needs`), gender (already a field — the color is just its display), swim-diaper requirement (derived from age), UCI number and coordinator contacts (structured fields, not bold notes), note priority (a real attribute).
2. **The "$ OCT" convention becomes a scheduled action**, not a note. A billing adjustment due in a future month should be a dated, tracked item that surfaces automatically in that month's billing run — and ideally shouldn't exist at all, since one-time credits should expire by design (see 2.6).
3. **Never rely on color alone.** Colors don't survive printing or screenshots and aren't reliable for colorblind staff. Pair every color cue with a text label or icon.
4. **The "difficult parent" flag needs a deliberate replacement, not a direct port.** As it stands it's a subjective judgment permanently attached to a person's name, with no reason, author, date, or review, visible to anyone with access, and capable of leaking into parent-facing output. A better design serves staff *more*: an access-controlled account note recording what happened, who logged it, and when. Restrict to desk/management roles.
5. **Migration requires a human pass over ALL-CAPS names** — some are intentional signals, some are typos or how a parent wrote it. Not a scriptable conversion.

### 3.3 Make-Up Credit Conversion Between Lesson Types
**Reported by ownership; ratios unverified.** Make-up credits appear to be **convertible between lesson types at an exchange rate** — e.g. some number of group credits equal one semi-private credit, and roughly four group credits equal one private credit.

**This changes the credit model materially.** Throughout the legacy system, the six counters (`MU_PR_Total`, `MU_SP_Total`, `MU_GR_Total`, `MU_PM_Total`, `MU_ST_Total`, plus `UK`) look like separate, non-fungible balances. If conversion is real, they are **denominated units in a single system**, and a balance in one type carries redeemable value in another.

It also changes the liability picture: a student holding 24 semi-private and 10 Parent & Me credits may be redeemable for a different — and larger — amount of higher-value lesson time than a raw count suggests.

**Requirements once the rules are confirmed:**
1. **A configurable conversion table** (group→semi-private, group→private, semi-private→private, and any others) rather than ratios hard-coded in logic.
2. **Matching and redemption honor conversions automatically** — a student with only group credits should still surface for an eligible semi-private make-up if the conversion permits it, without staff doing arithmetic.
3. **Conversions are recorded as events** — what was converted, at what rate, by whom — so a balance change is explicable later.
4. **Reporting values credits consistently** so outstanding liability is meaningful.

**Open — required before building:**
- The actual ratios, and which conversions are permitted
- Whether conversion is upgrade-only, or a private credit can be split into multiple group credits
- Whether it's automatic or requires staff approval each time
- What happens to existing private credits when a student moves to group lessons

### 3.4 Multi-Child / Multi-Lesson Pricing (the "sibling discount")
This is **not** a flat family discount — it's a progressive per-slot discount, directly carried over from the legacy `Rate_1`–`Rate_8` calculation logic:

- 1st lesson slot in a family/household: full rate, no discount.
- 2nd slot: full rate minus 1× the lesson type's discount amount.
- 3rd slot: full rate minus 2× the discount amount.
- 4th slot and beyond: full rate minus a **capped** 3× the discount amount (the discount does not continue growing past the 4th slot).

**Action required before build:** the legacy formula hard-codes this 3x cap with no documented rationale. Confirm with management whether this cap is still current business policy before encoding it as a permanent business rule — the risk of silently migrating a stale or unintended rule is real (see Section 4, migration risks).

**New finding, confirmed from a live student record — but flagged as a special case, not a standard rule:** that record ("CC Monthly 50% off PRIV" — 50% off private lessons) is a one-off arrangement for a specific student getting private lessons at semi-private pricing, not something the school normally offers. This isn't a second standard discount tier — it's evidence that **the system needs to support manually-applied, one-off pricing overrides** for special arrangements management approves on a case-by-case basis, distinct from the standard sibling-discount formula. Worth designing as an explicit "special pricing override" field/flag (visible on the family/student record, Management-only to set, with a required note explaining why) rather than folding it into the standard rate/discount tables — that keeps one-off exceptions from being mistaken for policy the next time someone reads the pricing logic.

### 3.5 Rate Changes, Annual Rollover, and Prepay Rate Locks
**Business cadence (confirmed with ownership):** the school runs year-round with a scheduled two-week closure from mid-December through New Year. **Price changes happen once a year, at the start of the new year** — mid-year changes are not part of normal operation. Before the increase takes effect, families are offered the chance to **prepay at the outgoing year's rates**, locking in the old price.

**How it works today (verified in the DDR):** each billing record stores its rate as stamped-in data via an auto-enter calculation, not a live lookup. The rate copies from `Billing_Rates` (one record per year) into `Billing_Months` when the lesson type is set, then freezes. Next year's billing records are generated in advance in bulk by `PRF_Create_Billing_Records_for_New_Year`.

- *Correct behavior worth preserving:* historical invoices don't retroactively change when prices go up.
- **The prepay rate lock does not exist as a feature — it is done by hand, every month.** When a family prepays at the outgoing rate, the annual rollover still stamps the **new** rate into all twelve of their upcoming billing records. Staff then manually enter a negative adjustment in each month (via `Adjustment_Credit`) to back out the difference — e.g. −$9/month for a year-long semi-private prepay at 15%. That is **12 manual corrections per prepaid family per year.** Consequences: it scales linearly with prepay uptake; missing one month silently overcharges a family with nothing to flag it; the adjustment records an amount but no reason, so the rationale is unrecoverable later; and reporting shows a phantom charge plus a correction rather than the actual agreed price. This is the clearest example in the system of a missing feature being absorbed as recurring manual labor.
- *Secondary issue:* the rate field allows manual editing over the calculated value, with no marker distinguishing an intentional override from a typo.

**Design for the new app:**
1. **Effective-dated rates.** A rate carries a start date rather than just a year. A price increase means inserting a new dated rate, never editing an existing one. This matches the annual cadence naturally while also handling an off-cycle change correctly if one is ever needed.
2. **Rate locks are first-class records — this is the highest-value fix in this document.** A prepaying family gets a durable *rate agreement*: this family/student, this locked rate, this discount tier, effective through this date. The billing engine honors it automatically when computing every affected month. **This eliminates the manual monthly adjustment entirely** — no negative adjustments, no missed months, no unexplained line items. The locked price simply *is* the price.
3. **Issued invoices snapshot their rate; unissued future periods resolve the applicable rate** (locked rate if one applies, otherwise current effective rate) — no batch re-stamp required.
4. **Adjustments are reserved for genuine one-offs** (a courtesy credit, a billing error) and require a reason. They should stop being the mechanism for something the system ought to compute on its own — which also makes the remaining adjustments meaningful and reviewable.
5. **Annual rollover as a guided, reviewable process**, not scripts run in a remembered order: set next year's rates → preview impact → generate next year's billing → confirm rate locks applied, with the system verifying each step.
6. **Manual rate overrides are explicit** — a distinct field requiring a reason, separate from the calculated rate and captured in the audit log.
7. **Impact preview before committing.** Show how many families are affected, how many hold rate locks, and the projected revenue delta before applying a change.

### 3.6 Prepay Plans, Rate Locks, and Refunds
**Confirmed with the billing team.** Prepay discounts are **duration-based** — the longer the prepaid term, the larger the discount. Known data points: **8-month prepay = 10%**, **4-month prepay = 5%**. (The full tier ladder — 0/5/10/15/20/25/50/100% exists in the system; confirm which are actually offered.)

**How prepay is recorded today:** when a family pays, staff **pre-post all the purchased months** with the discount applied, so anyone viewing the account can see how far ahead they're paid. Preserve this — visible paid-through status is genuinely useful.

**The early-termination refund rule (clean and implementable):** if a family stops before completing their prepaid term, the months they *actually took* are **recalculated at the discount tier they genuinely qualified for**, and the difference is refunded.

> Example: family buys an 8-month prepay at 10%. They stop after 4 months. Those 4 months are recalculated at the 4-month tier (5%), and the difference — the 5% they didn't earn — is refunded back. Stopping at months 5, 6, or 7 works the same way: since 8 months wasn't reached, the completed months recalculate at the 4-month tier.

**Design requirements:**
1. **Prepay term and tier are stored explicitly** — term length, discount rate, start month, paid-through month.
2. **The refund recalculation is automatic.** Given a stop date, the system determines the qualified tier, recomputes the completed months, and produces the refund figure — with the calculation shown, not just a number.
3. **Tier qualification is a lookup, not arithmetic in someone's head.** Months completed → tier earned.
4. **Rate locks remain explicit records** (see 3.4). A prepay purchase creates both a paid-through schedule and a locked rate.
5. **Held credit remains an option** — families may keep prepaid credit rather than refund (see 3.6 for the hold clock rules).

### 3.7 Enrollment Holds and Prepaid Credit
Families can pause enrollment and have their unused prepaid balance held as credit. **What that credit is worth depends on how long the pause lasts.** Rules confirmed with ownership:

- **Resumed within one year of the pause date:** the credit retains its *locked rate*. The family gets back the same **number** of prepaid months they purchased (not the same calendar months) at the price they paid. The rate lock survives the pause intact.
- **Pause exceeds one year:** the rate lock expires. The credit converts to a **dollar value** applied against the current year's rate.
- **The dollar credit never expires.** Once converted, it stays on the account indefinitely until used.

**What this means for the data model:** prepaid credit cannot be stored as a single dollar figure. It carries two denominations at once, with a clock deciding which applies:
- the monetary amount paid,
- the rate and discount tier it was purchased at,
- the **count** of months/lessons it covers, by lesson type,
- the hold start date — the clock runs from the pause, not from the original purchase.

The billing engine resolves which denomination applies at the moment the family resumes. This is the rate-agreement structure from 3.2 extended with a hold clock, not a separate mechanism.

**Design requirements:**
1. **Holds are explicit records** with a start date, not free text. (The legacy system stores holds as text notes — e.g. "WORK", "AUG PO" — which can't drive a calculation, so none of the above can be automated today.)
2. **The system computes the credit's current worth automatically** rather than making staff work out whether the lock still applies. On resumption it should state plainly: "resumed within the lock window — 4 prepaid months restored at locked rate," or "lock expired — $X credit applied at current rate."
3. **Warn before the one-year mark.** A family approaching lock expiry is about to lose value they paid for. Staff should see it coming — both a courtesy and a natural re-enrollment prompt.
4. **Credit conversion is an auditable event**, with a clear before/after, so it's explicable to a family who asks about it later.
5. **Outstanding credit liability report.** Because dollar credits never expire, unredeemed credit accumulates indefinitely on the books. Management should be able to see total outstanding credit at any time — both for financial visibility and to spot dormant accounts worth reaching out to. (Related in spirit to the unused make-up credit balances noted in 3.5.)

### 3.8 Closures: Two Distinct Types
The system currently treats these the same way, but they behave oppositely and the new app should model them separately:

- **Scheduled annual closure** (the two-week December/January closure): known in advance, absorbed into the annual flat rate, **generates no make-up credits**. Billing is unaffected — note that `Billing_Months` has no lesson-count field, so monthly tuition is flat regardless of how many lessons fall in a given month. This is a normal tuition model and worth preserving deliberately rather than by accident.
- **Incidental closures** (individual holidays like Memorial Day and Presidents Day, confirmed on live student records; weather; pool maintenance): these **do** generate Out Lessons and make-up credits for every affected student, via a bulk operation.

The new app needs a closure record with an explicit type that determines whether make-ups are issued — plus, for incidental closures, the "close this pool/date and issue make-ups to everyone affected" bulk action described in 3.4. Also worth noting: the legacy `Holiday_Dates` table holds only 6 records, so it appears to be a small working set rather than a durable multi-year closure calendar — the new system should keep a real, permanent closure calendar.

### 3.9 Cancellation Rules
- A cancelled lesson (marked absent, or cancelled in advance) generates a make-up credit by default, unless explicitly flagged not to (the legacy "do not issue" guard — this should map to an explicit reason code: e.g., late cancellation past a cutoff, no-call/no-show, vs. instructor-initiated cancellation).
- Cancelling a *booked make-up* (as opposed to the original lesson) should restore the credit rather than consuming it a second time.
- Business policy question to confirm before build: does a late cancellation (e.g., same-day) forfeit the make-up credit today? The legacy system supports this via the guard flag, but the specific cutoff rule isn't encoded in a calculation — it appears to be a manual staff judgment call. Decide whether to formalize this into an automatic rule or keep it as staff discretion.
- **New finding:** holiday closures (e.g., "HOLIDAY CLOSURE MEMORIAL DAY," "CLOSED PRES. DAY," seen directly on a real student's Out Lessons list) go through this exact same mechanism — a business-wide closure generates an Out Lesson (and presumably a make-up credit) for every affected student automatically, confirming the `STU_Schedule_Holiday_MU_Bulk` script found in the DDR is a real, actively-used bulk operation. The new app needs a "close the pool for a date, generate make-ups for everyone affected" action as a first-class admin tool, not just individual cancellation handling.
- **New open question, prompted by real data:** one student record we looked at had **28 accumulated, unused private-lesson make-up credits.** That's a lot sitting unused. Worth asking management: should make-up credits expire after some period? Right now nothing in the legacy system appears to enforce that, and unlimited accumulation could become a real liability (families expecting to redeem years of banked credits at once). Added to the open questions list below.

### 3.10 Student Profile Notes (Medical, Special Needs, History)
Students carry a special-needs flag (`flag_Special_Needs`, surfaced in the UI as "Special Abilities") alongside free-text notes (`Notes_General`, `Instructor_Notes`). Parents supply information at intake and over time that instructors need at every lesson: **allergies, special-needs details, and relevant history** (e.g. a child arriving fearful after a bad experience elsewhere). This is distinct from the operational and office-message note types in 2.1 — profile notes are persistent and apply to every lesson, not to a date.

**Interaction pattern to preserve (confirmed in use today):** the roster row shows an **indicator that a note exists** — not the note's content — and the instructor taps to expand and read it. The legacy system already does this, including a red alert badge on rows needing attention.

This should be treated as an intentional design decision, not merely a space-saving one: **an iPad on a pool deck is visible to passing parents.** Collapsing note content by default means an instructor can see that something needs knowing without a child's allergy or history being legible over their shoulder. Any redesign that "helpfully" displays notes inline would be a privacy regression.

**Design requirements:**
1. **Indicator + expand**, as above. Preserve it.
2. **Note severity/type is distinguishable.** A life-threatening allergy and "child is nervous in deep water" should not present identically. At minimum, separate safety-critical notes from general context, and consider whether critical medical information warrants stronger prominence than expand-to-read (see team question).
3. **Instructors see profile notes only for students on their own roster** — consistent with the access rules in Section 1.
4. **Parents are the source.** These notes come from families at intake and afterward, which connects directly to the digital intake form idea — captured once from the parent rather than transcribed by staff from paper.
5. **Instructors should be able to add observations** without editing the parent-supplied information — an instructor noting "very improved with floating this week" is different from the medical facts a parent provided, and the two shouldn't be able to overwrite each other.
6. **Health information stays minimal and purposeful.** Store what an instructor needs to teach safely, not a medical record. Anything beyond "needs awareness of X" belongs in a real health system, not the scheduling app.
7. **Photo consent — "NO PHOTOS" flag.** Families indicate on the waiver whether their child may be photographed, and **instructors need to know this**. Today it's conveyed as a note. Requirements:
   - A **structured consent field** captured at intake, not free text — so it can be reported on and can't be missed.
   - **Visible on the roster** as a clear badge, at the same prominence as the swim-diaper requirement. An instructor should see it without opening anything.
   - Default to **no consent** when unanswered. Consent must be affirmative; an unfilled field is not permission.
   - This is a legal/parental-rights matter, not a preference — it warrants stronger treatment than an ordinary note.
8. **Service requirements that aren't medical.** Confirmed from live records: some students carry requirements such as a **specific instructor gender** (in one case required by the funding agency). These are neither medical notes nor scheduling preferences — they're constraints the matching engine must honor when assigning or substituting instructors. Model them as structured requirements, not free text.
9. **Distinguish requirements from background context.** A note that a student *wore a life jacket at a previous swim school* is useful context about their prior experience — **not** an instruction to use one here (Blue Buoy does not use life jackets in lessons). Free-text notes currently conflate "you must do this" with "here's their history." Separating requirement from context prevents a new instructor misreading background as direction.

### 3.11 Free Trials
- Legacy tracks free trials via a text tag (`"free trial"`) inside a general hold-reason field, checked via pattern-matching. The new app should give this a first-class `is_free_trial` boolean plus a trial-count/expiration policy, rather than continuing the string-tag pattern — this was a workaround, not a design choice worth preserving.

---

## 4. Out of Scope (Deliberate Boundaries)

Recorded so future readers know these were excluded on purpose, not overlooked.

### Payroll and staff time tracking — **out of scope**
- **Humanity** handles staff shift scheduling and clock-in/out for *all* staff — lifeguards, office staff, and instructors, including guard shifts.
- **Paychex** handles payroll processing.
- Both work. Payroll also carries tax, wage-and-hour, and filing obligations that make building or replacing it a poor use of this project's effort.

**Considered and rejected:** using lesson attendance timestamps to help verify missed clock-ins (currently resolved by reviewing pool deck camera footage). This doesn't work: a teaching schedule shows when a lesson was *scheduled*, not when someone arrived; attendance can be backfilled, so its timestamp doesn't establish presence; and most staff being verified (lifeguards, office) don't take lesson attendance at all. Camera review is the appropriate tool.

**No duplicate data entry exists.** Humanity holds staff working hours including guard shifts; this app holds lesson assignments only. The two do not overlap.

### Known consequence: cross-role scheduling conflicts
Because the app has no knowledge of guard shifts, it **cannot detect** a lesson scheduled during an instructor's lifeguard shift. Today this is prevented by staff knowledge. Options if it proves to be a real problem: a read-only import of shift data from Humanity (if its API supports it), or accepting the limitation. **Confirm with staff whether this conflict actually occurs before building anything for it.**

### Also out of scope
- Accounting/bookkeeping systems (the app produces billing data; it is not a general ledger)
- Detailed health records — student profile notes carry only what an instructor needs to teach safely (see 3.8)
- Pool chemistry, maintenance, and facility management

---

## 5. Device & Interface Strategy

The legacy system solves this by building **separate files per form factor** — `Instructor_Entry` and `Launcher_Teacher` for iPads, `BlueBuoy_FM` for office computers. The web app uses one codebase adapting per device, but the underlying decision is the same and is easy to get wrong.

**The failure mode:** trying to make every screen work everywhere. The result is a billing screen that's unusable on a phone and a roster that's cluttered on a desktop — everyone dislikes all of it. Decide deliberately what belongs where.

| Device | Primary use | Design priorities |
|---|---|---|
| **Pool deck tablet** | Attendance, rosters | Touch-first, large tap targets, glanceable, usable wet and one-handed. Deliberately minimal — see 1.2 and 2.1. |
| **Office desktop / laptop** | Scheduling, billing, search, data entry | Information-dense, keyboard-driven, multi-column, many records visible at once. Where the substantive work happens. |
| **Phone** | Quick lookups on the move | Check a schedule, look up a student, respond to a notification. Not a data-entry surface. |

**Not every function needs to exist on every device.** Rate management, annual rollover, and charter-school invoicing are desktop work; it's correct to simply not offer them on a phone rather than build a cramped version nobody uses. Conversely, the roster genuinely needs to work well on all form factors — which is one reason it's a good first thing to build (see the phased plan): it forces the responsive foundation to be right on the lowest-stakes screen.

---

## 6. Data Protection, Backups & Recovery

**Key principle: for the most likely disaster, restoring a backup is the wrong response.** Two distinct scenarios need different tools:

- **Catastrophic loss** (server failure, database corruption) — rare; this is what backups exist for.
- **Human error** (the real incident where a family's record was deleted) — common. Restoring a full backup here would recover that family but *erase every payment, attendance mark, and schedule change every other user made since the backup*. It would fix one problem and create dozens.

Protection is therefore layered, with backups as the last resort rather than the first:

1. **Soft delete (Section 1.1).** Nothing staff remove is truly gone. Restoration is a single click, takes seconds, and affects nothing else. This handles the large majority of "oh no" moments without touching a backup.
2. **Audit log (Section 1).** Shows what changed, when, and by whom — enabling a targeted correction of one bad edit instead of rolling back time for everyone.
3. **Point-in-time recovery.** PostgreSQL continuously records changes, so recovery isn't limited to "last night's snapshot" — it can target any moment ("the state at 2:47pm, immediately before the bad import"). Standard on managed database platforms.
4. **Off-site copies.** Protection against losing the entire environment, not just data within it.

**Targets:**
- **Recovery granularity:** continuous. Worst-case data loss measured in seconds, not hours. Daily snapshots as anchor points.
- **Retention:** 30 days of point-in-time recovery minimum — some problems (a billing error) surface weeks after they occur.
- **Restore time:** minutes to a couple of hours for a full restore, depending on database size. A documented operation on managed platforms, not a heroic effort — but it means downtime, which is why layers 1–3 matter more day to day.

**Two commonly-skipped requirements:**
- **Test restores on a schedule.** A backup never restored is a hypothesis, not a backup. Perform a real restore into a test environment quarterly. This is the most frequently neglected step in backup strategy and the one most likely to matter.
- **Preserve the FileMaker data as a permanent frozen archive at cutover.** Not a live system — a preserved export of 20 years of history, kept indefinitely and untouched. Cheap insurance against a question in three years the new system can't answer.

**Immediate action on the legacy system:** confirm what backup and restore capability exists on FileMaker today, and whether a restore has ever actually been tested. That answer may be more urgent than anything in this section.

---

## 7. Key Technical Improvements Over Legacy FileMaker

| Legacy pattern | Problem | Web app replacement |
|---|---|---|
| Anchor-buoy relationship graph (341 table occurrences from 22 base tables) | Every new report/screen required new table occurrences; graph became unmanageable over 20 years | Normal relational schema with a real API layer — no table-occurrence explosion, since joins are written per-query, not pre-declared |
| Virtual_List scratch table (124 fields, 22 TOs, 4-script recalculation chain) | Manual workaround for FileMaker's lack of native ad hoc sortable/paginated reporting | Plain indexed SQL queries (`ORDER BY` / `LIMIT` / `OFFSET`) — the entire pattern becomes unnecessary |
| `Evaluate()`-based dynamic field-name resolution for sibling discounts | Effectively runtime `eval()` of business logic; not statically analyzable, fragile, undocumented | Explicit tier/discount lookup table with real foreign keys and a documented calculation function |
| Flattened matrix columns (`Students.c_1`…`c_52`, 52 paired week columns; letter-suffixed rate columns) | Column-per-repeating-unit anti-pattern instead of a child table | Proper child tables (e.g. `student_weekly_values`, `lesson_type` reference table) |
| Heavy global-field usage as pseudo-session-state (78 of 93 Preferences fields, 27 on Students) | No relational equivalent; conflates configuration with per-user session state | Session/request-scoped application state (React state, backend session), not database columns |
| Name-based instructor matching in some relationships (`Name_First = Instructor` text match) | Silently misjoins data if two instructors share a name or a name is edited | All joins keyed on `staff_id` exclusively — no text-based matching anywhere |
| Manual multi-step attendance recalculation (Virtual_List chain, PSOS-offloaded) | Built to keep the FileMaker Go UI from blocking during writes over pool-deck Wi-Fi | Optimistic, offline-tolerant writes with background sync — same goal, native web/mobile pattern |
| Raw credit card numbers stored on the Families table | Real PCI liability | Stripe tokenization — no card data touches our database at all |
| `OLD_*` legacy ID columns scattered across nearly every table | Evidence of at least one prior lossy migration; referential integrity on older records isn't guaranteed | Data audit and cleanup pass before migration; no `OLD_*` columns carried into the new schema |
| Dual billing keys on Billing_Months (both `id_student` and `id_family` populated) | Unclear which is authoritative; risk of duplicate/conflicting invoices | Single canonical foreign key (family-level billing, with student-level line items) decided explicitly before schema design |

**The headline technical goal:** instant pool-deck page loads on iPads. This means a single pre-joined API response per instructor per day (not a client-side walk across Student → Schedule → Attendance → Billing relationships), proper indexes on `(instructor_id, date)` and `(student_id, date)`, and offline-first attendance writes — none of which the legacy relationship-graph architecture was built to support.

---

## Open Questions for Stakeholder Sign-off
1. Is the 3x discount cap on the 4th+ lesson slot still intended policy, or should sibling discounts scale differently?
2. What is the actual late-cancellation cutoff policy for forfeiting a make-up credit (currently informal/staff discretion)?
3. Is family-level or student-level billing the canonical source of truth for invoicing?
4. Should families get self-service make-up booking, or does that stay a desk-staff-mediated process?
5. For waitlist matches: once staff trust the matching over a season, is auto-notifying the family directly (with a claim window) ever in scope, or does every match always route through desk staff first?
6. **Should make-up credits expire?** Large banked balances appear to be normal rather than exceptional — live records showed one student with 28 unused private credits, and others with 24 semi-private + 10 Parent & Me, and 24 semi-private + 6 Parent & Me. This is a meaningful outstanding service liability with no expiry, no reporting, and no proactive outreach. Decide whether an expiration policy is wanted, and build the unused-credit report either way.
7. How common are special-case, manually-approved pricing arrangements (like the semi-private-rate exception seen above)? If they happen often enough, the "special pricing override" feature is worth building well from day one rather than as an afterthought.

---

## Appendix: Legacy File Inventory (confirmed from FileMaker Server host)
The DDR analysis referenced several files that turned out to exist outside the original export. Confirmed live on the host:

| File | Status | Action needed |
|---|---|---|
| `BlueBuoy_FM` | Analyzed (this PRD is built from it) | Confirm this is the current live file — see next row |
| `BlueBuoy_FM_2024` | **Not yet analyzed** | Confirm with server admin which of these two is actually in daily use before treating `BlueBuoy_FM`'s schema as canonical |
| `Instructor_Entry` | **Analyzed** | Confirmed: the actual iPad-facing app. Holds no data of its own — pure UI layer over `BlueBuoy_FM` via external reference. Surfaced the Deck Manager role, PSOS attendance-write pattern, deck-level notes, and payments-due/free-trial reports — all now reflected in Sections 1 and 2.1 |
| `Launcher_Teacher` | **Confirmed live via screenshots, DDR not yet reviewed** | Confirmed: matches description exactly — Schedule and Student Levels only, no Deck Manager tools. The day-to-day Instructor experience: read-only view of any teacher's schedule, date navigation, and a dedicated catch-up button for backfilling missed attendance from a prior day. Now reflected in Sections 1 and 2.1. Export the DDR when convenient to confirm field-level details, but it's no longer a blocker |
| `fmSMS` | **Confirmed live — commercial Databuzz add-on, not custom code** | Identified as a "bring your own gateway" tool: connects to one of ~20 third-party SMS providers rather than sending messages itself. Still need to check its Accounts/Gateways tab to see which specific provider (Twilio, ClickSend, etc.) is configured — that resolves the keep-vendor-vs-migrate decision for Section 2.5 |
| `20 Time` | Analyzed (legacy roll-sheet system) | No further action — superseded by current system |
| `11-Wait`, `19`, `19 Time`, `20_BACKUP` | **Not yet analyzed** | Purpose unconfirmed — worth a quick check with whoever manages the server before assuming they're safe to leave out of the migration |


---

# PART B — Phased Rollout Plan

*Sequencing proposal. Likely to be superseded by the developer's own plan — the reasoning about why billing should not cut over in December is the part worth keeping.*


## Why not one big cutover at the December closure

The two-week closure is genuinely the best *window* — no lessons, staff available for training, low operational risk. But it's the wrong moment for a full switch, for two reasons:

1. **December is the most billing-intensive point of the year.** Annual rate changes, prepay-at-old-rate sales, next year's billing generation, and rate locks all happen then. Cutting over billing while billing performs its most complex annual operation is the highest-risk possible timing. Problems would surface in January, across every family at once.

2. **Scope.** The remaining work includes: resolving ~81 open business questions, schema design, migrating 20 years of data with known integrity issues, four device interfaces, the billing engine, scheduling and search, notifications, and a third-party payer invoicing subsystem that doesn't exist in any form today. That is a multi-quarter effort.

**Use the closure — for Phase 1 only.**

---

## Phase 0 — Foundations (before any user-facing work)

**Prerequisites, not features.** None of this is visible to staff, and all of it is required.

- Answers to the team questions — especially charter school / Regional Center billing, which is entirely undocumented
- Resolve open business decisions: sibling discount cap, cancellation cutoff, family vs. student billing authority
- Schema design in PostgreSQL
- **Data migration dry run** against real exported data, addressing the known landmines: name-based instructor matching, dual billing keys, ALL-CAPS name conventions (extract meaning *before* normalizing), `OLD_*` legacy ID columns
- Auth model: individual accounts, PIN for pool deck, session/device management
- Backup and point-in-time recovery configured **and a test restore performed**
- Hosting, domain, SSL

**Also during this period, independent of the project:** fix the unencrypted FileMaker connection and confirm current backups are restorable. Both are live issues on the existing system.

**Exit criteria:** migrated data reconciles against FileMaker — student counts, family balances, and make-up credit totals match.

---

## Phase 1 — Attendance & Rosters *(target: December closure)*

**Why first:** lowest risk, highest visibility, and it forces the responsive foundation to be correct on the simplest screen before complex interfaces are built on it.

**Scope:**
- Instructor roster view (all four form factors, tablet-first)
- Mark present/absent; backfill a prior day
- Free schedule switching between instructors; frictionless action from any device
- Student profile notes: indicator + expand-to-read
- Swim-diaper badge for under-4s
- Offline: full day's schedule for **all** instructors cached on every device
- PIN login

**Explicitly not in scope:** billing, make-up issuance, scheduling changes, waitlist.

**Fallback:** FileMaker remains fully operational. If anything goes wrong, instructors reopen `Launcher_Teacher` and lose nothing. Attendance is re-entered or exported.

**Parallel run:** 2–4 weeks with FileMaker as system of record; reconcile attendance nightly.

**Success:** instructors prefer it. If they don't, fix that before proceeding — the rest of the project depends on staff trusting the new system.

---

## Phase 2 — Scheduling, Search & Waitlist

**Why second:** builds on a proven foundation; still no money at risk.

**Scope:**
- Deck Manager search — **must match or exceed** current FileMaker Find capability (see PRD 2.4; this is the largest adoption risk in the project)
- Saved searches for common queries
- Schedule creation and editing
- Waitlist matching: opening→candidates and student→all openings
- Ad hoc availability search for phone-in make-up requests
- Make-up credit issuance and redemption
- Closure handling: scheduled vs. incidental, with bulk make-up generation
- Class eligibility validation with override

**Fallback:** FileMaker still holds billing; scheduling can revert if needed.

**Parallel run:** 4+ weeks, including at least one full make-up cycle.

---

## Phase 3 — Billing *(deliberately at a calm point in the year — not December)*

**Why last among migrations:** highest risk, hardest to reverse, and errors are visible to customers.

**Scope:**
- Rate tables with effective dating
- Sibling discount and prepay discount tiers
- **Explicit rate-lock records** — eliminating the manual monthly adjustment entirely (the single highest-value fix in the PRD)
- Enrollment holds and prepaid credit, with the one-year lock clock
- Full transaction ledger: all payment and adjustment types, unlimited payments per month
- Stripe integration for family payments
- Special-case pricing overrides with reasons

**Parallel run:** minimum one full billing cycle computed in both systems and reconciled line by line before switching. **Do not skip this.**

**Note:** the annual rollover happens in FileMaker one more time before this phase. That's intentional — observe a full cycle in the new system before trusting it with the year's most complex operation.

---

## Phase 4 — Third-Party Payers (Charter Schools & Regional Center)

**Why it can come last:** this is net-new capability. Nothing currently exists in software to break, so it can't regress anything. It's also potentially the largest operational win, since it's entirely manual today.

**Scope:**
- Payer entities separate from families
- Authorization / purchase-order tracking with exhaustion and expiry warnings
- Per-payer invoice generation with required documentation
- Accounts receivable aging
- Payment reconciliation across multi-student checks

---

## Phase 5 — New Capabilities

Only after the replacement is complete and stable:

- Broadcast notifications (rebuilt to replace fmSMS)
- Family self-service portal
- Digital intake forms
- Attrition warnings, level progression tracking, instructor utilization, revenue forecasting
- Unused credit and outstanding balance reporting

---

## Ongoing throughout

- FileMaker stays available read-only until Phase 4 completes
- **Permanent frozen archive** of FileMaker data preserved at final cutover
- Test restores quarterly
- Each phase gets its own training and its own fallback plan

---

## Honest note on timing

Phase 1 by the December closure is plausible if Phase 0 starts promptly and stays focused. The full replacement is realistically a multi-quarter effort — likely well into the following year, possibly beyond, depending on how much time you and your brother can commit.

That is not a failure of planning. Twenty years of accumulated business logic, three of which we only discovered in conversation because they existed nowhere in the software, does not get replaced in sixteen weeks. The phased approach means you get real value in January rather than waiting for everything.



---

# PART C — Staff Questionnaire

*Questions put to the scheduling and billing team. Many have been answered and folded into Part A; the unanswered ones remain open.*


## Part 1: The Big Open Questions

These came up during the analysis and genuinely can't be answered from the software alone.

### Pricing & Discounts
1. **The sibling discount** currently works like this: 1st lesson slot in a household is full price, 2nd gets one discount step, 3rd gets two steps, and the 4th and beyond all get three steps (the discount stops growing after the 4th). **Is that still the intended policy?** It's hard-coded with no explanation anywhere, so it may be stale.
2. **How often do you set up special one-off pricing** for a family (like the private-at-semi-private-rate arrangement we saw)? A few times a year, or regularly? That determines how much we invest in making that easy vs. just possible.
3. **When you raise prices**, what's the process today? What's annoying about it? (We know prices change once a year at the start of the new year, and that prepaid families need a manual adjustment every month afterward — what else is involved?)

### Charter Schools & Regional Center (biggest gap — most important section)
We found that the system lists 14 charter schools and 9 Regional Center agencies as billing options, but only as a text note telling staff how to bill. Everything after that appears to happen manually. These questions matter a lot, because this is probably the largest thing the new system could take off your plate.

4. **Walk us through billing a charter school**, start to finish. How do you know what to bill, what do you send them, in what format, and how do you know when they've paid?
5. **Where does that information live today?** A spreadsheet, a separate program, paper, email? (There's no trace of it in the FileMaker system.)
6. **Do charter schools authorize a set number of lessons or a dollar amount** up front — like a purchase order with limits and an expiration? If so, how do you currently track how much is left?
7. **Has a student ever kept taking lessons past what a school or agency authorized**, leaving you unpaid? How did you find out?
8. **How long do they typically take to pay**, and how do you track what's overdue?
9. **Is Regional Center billing different from charter school billing?** Different forms, different timing, different documentation?
10. **Do institutional payers always pay full price**, or are there negotiated rates per school/agency?
11. **Can one family have different payers for different kids** — e.g. one child through a charter school and a sibling paid by the family?
12. **What documentation do they require** to release payment — attendance sheets, signed service logs, progress notes?
13. **What's the most frustrating part of this whole process?**

### Payment Plans & Prepay
14. **What prepay options do you actually offer?** The system has discount tiers of 5%, 10%, 15%, 20%, 25%, 50%, and 100% — which are really in use, and what determines which one a family gets?
15. **The prepay-before-the-price-increase offer** — how long does that locked rate last? The whole next year? Until the prepaid lessons run out? Something else?
16. **The monthly adjustments for prepaid families** — roughly how many families are you doing this for, and how long does it take each month? (We now understand the system applies the new rate anyway and you manually back out the difference each month. This is near the top of the list to eliminate.)
17. **Has a month ever gotten missed**, or an adjustment entered wrong? How did you catch it?
18. **What happens if a family prepays at the old rate and then quits partway through?** Refund at which rate, and how is that figured today?
19. **Can a family prepay for part of a year** (say six months)? If so, what happens when it runs out — do they move to the new rate then?
20. **Besides prepay differences, what else do you use adjustments for?** (Courtesy credits, billing corrections, something else?) We want to keep adjustments available for real one-offs while removing the ones the system should just handle.
21. **What's the difference between the plan types** in practice — monthly auto-charge vs. prepay vs. card-on-file? Do families move between them?
22. **The system only allows two payments per month per family.** Is that ever a problem?
23. **How do you handle gift certificates, referral credits, and account credits** currently? Do they work well?

### The Monthly Billing Run (highest priority — this is where the most time goes)
Here's what we understand about the month-end process today. **Please correct anything wrong and fill in the gaps** — this is the area we most want to fix, and rough time estimates are genuinely useful.

Our current understanding of the steps:
- Manually post each family's lesson type for the month
- Manually work out prorated amounts for partial months
- Cross-reference a spreadsheet from the credit card company against what's being charged
- Manually reset families who had referral credits back to their normal fee the next month
- Void or refund families who cancel after billing has processed (roughly a one-week window)

24. **Is that right, and what did we miss?**
25. **Roughly how long does the whole month-end process take you?** Even a rough number ("most of a day," "two evenings") helps make the case for fixing it.
26. **Which step is the worst?** The one you dread, or that causes the most re-work.
27. **How many families typically need a prorated amount** in a given month?
28. **How many need a referral credit reset?**
29. **Has a referral credit reset ever been missed?** How did you find out? (This one worries us — a missed reset means a family keeps getting discounted with nothing flagging it.)
30. **How often does the credit card cross-reference turn up a mismatch**, and what do you do when it does?
31. **When a student changes lesson type mid-month**, how do you decide what to charge — the old rate, the new rate, or split between them? Is there a consistent rule?
32. **How often does the office forget to tell you about a mid-month change?** (You mentioned this happens — no blame intended, we want the system to carry that instead of a person.)
33. **What's the actual void/refund window**, and who decides whether to void versus refund?
34. **What else goes wrong during billing** that we haven't asked about?

### Payment Processing
We believe the setup is Affinity24 (Tustin) as the processor, Authorize.Net as the gateway, settling to Wells Fargo. A few things that affect a real decision about keeping it:

35. **Is that right?** Anything else in the mix?
36. **Roughly what's the monthly credit card volume?** (Not counting charter school / Regional Center payments, which come by check.)
37. **Do you know your effective processing rate?** It's usually on the monthly statement.
38. **Do you have a rep at Affinity24 you actually call**, and are they helpful?
39. **Do cards on file ever expire and cause a failed payment?** How do you handle it currently? (Authorize.Net has an automatic card-updating service that may not be turned on.)
40. **How do failed payments get noticed and followed up today?**

### Closures & the Holiday Break
41. **During the two-week December/January closure**, families still pay their normal monthly amount — no credit or reduced bill, correct?
42. **Do families ever push back on that**, and how do you handle it when they do?
43. **For one-off closures** (a holiday, weather, pool maintenance) — does everyone affected automatically get a make-up credit? Always, or are there exceptions?
44. **How do you close the pool for a day** and get make-ups issued to everyone today? How long does that take?
45. **Is there a master list of closure dates** for the year anywhere, or is it handled as each one comes up?

### Make-Ups & Cancellations
46. **Is there a cutoff for late cancellations** where a family loses their make-up credit — same-day, 24 hours, etc.? Or is it always a judgment call? Should it become an automatic rule, or do you want to keep discretion?
47. **Should make-up credits expire?** We found one student with 28 unused private-lesson credits banked. Is that normal? Is it a problem?
48. **When do you decide NOT to issue a make-up?** What situations?

### Billing
49. **Is the family or the individual student the "real" account** when it comes to who owes what? The current system tracks both at once and it's ambiguous which one wins.
50. **How do you handle a family with a past-due balance?** Is there a point where lessons stop? Who decides?
51. **What billing situations does the system NOT handle**, so you deal with them manually or outside the system?

### Waitlist & Scheduling
52. **How do you currently match waitlisted kids to open slots?** Walk through what you actually do — that helps us automate the right thing rather than a guess.
53. **How often do parents turn out to be more available than what they originally told you?** (We're planning to show all matching openings, not just their stated window — want to confirm that's useful.)
54. **What makes a match a bad idea even when it looks fine on paper?** (Teacher/student chemistry, sibling logistics, etc.) These stay human decisions — we just want to know what to surface so you can judge quickly.

### Searching (important — please don't skip)
We saw the Deck Manager search screen and it's genuinely powerful. The biggest way a project like this goes wrong is replacing a capable search with a prettier but weaker one, so we want to get this right.

55. **What searches do you run most often?** Even the boring everyday ones — those become one-click buttons in the new system.
56. **Do you use Saved Finds?** If so, which ones?
57. **What's the most complicated search you've ever needed to build?** (Multiple criteria, excluding certain students, etc.)
58. **Is there something you've wanted to search for and couldn't?**
59. **Do group lessons work differently** from private/semi-private in ways we should know about — scheduling, pricing, make-ups?

### Class Types & Eligibility
We have approximate requirements but need them confirmed exactly, since the system will enforce them.

60. **What are the exact requirements for each class type?** Our current understanding (likely imprecise): Parent & Me is age 3 and under; Group needs age 7+ and level 8+; Stroke Tech needs age 10+ and level 10+. Please correct.
61. **Are there requirements for the other types** — Private, Semi-Private, Adult — or can anyone take those?
62. **Is it always age AND level**, or does one sometimes substitute for the other? (E.g. a strong 6-year-old at level 9 — could they join Group?)
63. **How often do you make exceptions**, and who decides?
64. **What happens when a child ages out of Parent & Me?** Is that tracked, or do you catch it as it comes up?
65. **Would it help to see students who are one level away** from qualifying for Group or Stroke Tech? (Could be useful for parent conversations and keeping kids progressing.)
66. **Are there other class types** we haven't seen — seasonal programs, clinics, camps, private groups?
67. **Are there other color highlights or visual cues** on your screens that mean something important? (We found the under-4 age highlight signals the swim diaper requirement — there are likely others we'd otherwise miss, since they don't show up anywhere in the database itself.)
68. **Are there other ways you encode meaning by how you type something?** We know about ALL CAPS first names (special needs students, and difficult parents). Others might include: bold text, abbreviations in notes, a symbol or punctuation added to a name, putting something in a particular field that isn't quite what that field is for.
69. **What do the common note abbreviations mean?** We've seen things like "AUG PO," "WORK," "MU," "OUT" — a quick glossary of the shorthand your team uses would help a lot.
70. **Are there other pool rules or requirements** tied to age, level, or student status that staff just know — things a new instructor would have to be told?
71. **For the ALL-CAPS parent convention** — is that something you'd want carried into the new system, or handled differently? (Our suggestion: a proper account note with a reason and a date, visible only to office staff, rather than changing the person's name. Happy to do it either way — your call.)

### Communication
72. **What do you use the bulk texting for most often?** Sub notices, closures, reminders, something else?
73. **What do you wish you could send but currently can't** — or that's too tedious to bother with?
74. **Do families ever reply to those texts?** If so, where do the replies go and who handles them?

### Family Contacts & Pickup
75. **How many contacts can be on an account today?** Is it always two, or can there be more — grandparents, a nanny, a second household?
76. **Do you track who's allowed to pick a child up**, separately from who pays the bill? (An instructor might need that, and it's different information from the billing contact.)
77. **Do split households or custody arrangements come up?** How do you handle them now?
78. **Would instructors benefit from seeing more than just names** on that popup, or is names-only the right amount?

### Notes & Student Information
79. **What kinds of things end up in the instructor notes?** (We know: allergies, special needs, past experiences/fears. Anything else?)
80. **Should a serious allergy look different from a general note?** Right now everything is "there's a note, tap to read." For something potentially urgent, would you want it more prominent — or does the current approach work fine?
81. **Who enters these notes today** — office staff from what parents tell them, or do instructors add their own too?
82. **Should instructors be able to add their own observations** about a student's progress, separate from what parents provided?
83. **How does this information get collected initially** — a paper form at signup, a conversation, over time?

### Access & Permissions
84. **Who should be able to do what?** Specifically: should desk staff be able to change prices? Issue make-ups? See other families' billing?
85. **Has anything ever been deleted or changed by accident** that was hard to recover? (We already know about the record-deletion incident — wondering if there are others.)
86. **Right now the instructor iPads have no real login** — the password prompt can be cancelled and it opens anyway. Has that ever caused a problem, or is it just how it's always been? Any concern about an iPad walking off with student info on it?
87. **Would a short PIN at the start of a shift be acceptable**, if switching between teachers' schedules stayed instant and password-free? (We want to keep the grab-any-iPad convenience — just add a light barrier at the start.)
88. **Does it matter who marked attendance?** Right now if you take your roll on a colleague's iPad, there's no record of who actually entered it. Worth tracking quietly in the background, or genuinely doesn't matter? (Either way, it won't add a step to your workflow.)
89. **How often does the dead-battery handoff happen** — grabbing another iPad late in the day to take your roll? Daily, occasionally? (It affects how much we cache on each device for offline use.)
90. **Do you ever need to take roll somewhere with no WiFi**, or is coverage solid across the whole pool deck?

### Remote Access & Staff Turnover
91. **When someone leaves, what happens to their access today?** Does anyone change passwords, or does it generally stay as-is?
92. **How many people share the same login?** (We noticed a saved "deck manager" password — wondering how widely shared logins are used.)
93. **Who needs access from off-site**, and for what? (You, your wife, scheduling office staff — do instructors ever need it from home?)
94. **Would a log of who accessed what be useful to you**, or is that more than you'd ever look at?
95. **Has there ever been a concern about a former employee** still having access, or taking family/student information with them?
96. **Who currently manages your FileMaker server** — someone in-house, or an outside consultant? (Relevant for the unencrypted-connection issue, which is worth fixing now regardless of this project.)

### Backups & Recovery
97. **What backups exist on the current system**, and has anyone ever actually restored from one? (Worth confirming — an untested backup isn't really a backup.)
98. **When that family record got deleted, what did you do?** Was anything recoverable, or was it re-entered from scratch?
99. **How long could you operate if the system were down** — an hour, a day? That tells us how fast recovery needs to be.

### Devices
100. **What does each person actually work on?** (Desk staff — desktop or laptop? Do you or your wife work from a phone often, or mostly laptop?)
101. **Is there anything you'd want to do from your phone** that you currently can't?
102. **Do the scheduling office computers have any constraints** — old machines, small screens, a specific browser?

---

## Part 2: The Most Important Question

**What takes way longer than it should?**

And its companion: **what do you do outside the system entirely** — on paper, in a spreadsheet, in your head, in a text thread — because the software can't handle it?

Please be specific and don't self-edit. "I have to check three different screens to answer one parent's question" is exactly the kind of thing worth fixing, and exactly the kind of thing that never shows up in a software analysis.

Also worth knowing: **what do you actually like about the current system?** We don't want to accidentally throw away something that works well just because it's old.

---

## Part 3: Ideas We Haven't Built Yet — What Sounds Useful?

These are all *possible* with the data you already have, but the current system was never built to do them. We're not committing to any of these — just want to know which sound genuinely useful versus which would be noise.

Rate them however you like: "yes please," "nice but not important," or "we'd never use that."

| Idea | What it would do |
|---|---|
| **Attrition warnings** | Flag families who look like they're drifting away — attendance dropping off, end date approaching with no renewal — *before* they quietly disappear |
| **Level progression tracking** | Show which students have been stuck at the same level for a long time (e.g. "14 students at Level 5 for 6+ months") — useful for teaching quality and for parent conversations |
| **Instructor utilization reports** | Who's consistently full, who has open capacity, trends over time — helps with hiring and scheduling decisions |
| **Revenue forecasting** | Project next month's expected revenue from current enrollment, and flag the gap between expected and actually collected |
| **Family self-service portal** | Parents could view their own schedule, balance, and make-up credits online — without booking anything themselves unless you want that |
| **Unused credit report** | "These students have large unused make-up balances" — so you can reach out proactively rather than being surprised later |
| **Digital intake forms** | Parents fill out enrollment/medical info digitally with a signature, instead of staff transcribing paper forms |
| **Automated waitlist alerts** | When a spot opens, staff see ranked matching candidates immediately instead of scanning manually |

**Anything missing from this list?** If there's something you've wanted for years that isn't here, that's probably the most valuable thing on this page.

---

## Part 4: Screenshots That Would Help

If it's easy to grab these while you're working, they'd help a lot. No need to stage anything — normal working screens are ideal.

- The **Family tab** on a student record (we've only seen the Lessons tab)
- The **billing/payment entry screen** — where payments actually get recorded
- Any **reports** you run regularly (payments due, monthly summaries, etc.)
- The **waitlist screen** as you actually use it
- The **fmSMS bulk texting screen** — particularly the **Accounts** or **Gateways** tab, which tells us which texting service is connected
- **Anything you use for charter school or Regional Center billing** — even if it's a spreadsheet, a Word invoice template, or a folder of PDFs outside FileMaker entirely. Especially that, actually: if it lives outside the system, we have no visibility into it at all.
- Anything that's a daily annoyance — a screenshot of the thing you wish worked better

---

*Thanks — every answer here directly shapes what gets built. Nothing is too small or too obvious to mention.*

---

## Round 2 Questions (issued after the first set was answered)

**Thank you for the last round.** Those answers changed a lot — several things we had wrong are now right, and the month-end billing process is now the top priority to fix.

**This round is much shorter.** These are new gaps that came up since, plus a screenshot request at the end.

Same as before: answer what's easy, skip what doesn't apply, rough answers are fine.

---

## Group Classes
We now know there are three group types — Parent & Me, Group (Stroke Prep), and Stroke Technique — all capped at 6 students. A few things that affect how scheduling gets built:

1. **What's the minimum for a group class to run?** If only one or two students are enrolled, does it still happen, get cancelled, or merge with another class?
2. **Does the price change based on how full the class is?** Does a student in a class of 2 pay the same as one in a class of 6?
3. **How does a group student fit into the sibling discount?** Do they take up a "slot" the same way a private student does?
4. **How do group make-ups work?** They'd need a class with both an open seat and the right level — is that harder to arrange? Can they take it as a semi-private or private instead?
5. **How do families join a group?** Do they join an existing class, or do you form a class once enough students want it?
6. **What is the Adult class?** Is it a group or individual, what's the capacity, and are there requirements?

---

## Make-Up Credit Conversions
We heard there's a formula for trading make-up credits between lesson types — something like a few group credits equaling one semi-private, or about four group equaling one private.

7. **Is that right, and what are the actual ratios?**
8. **Which conversions are allowed?** Group → semi-private? Group → private? Semi-private → private?
9. **Does it work in reverse?** Can a private credit be split into several group credits?
10. **Who decides?** Is it automatic, or does someone approve each conversion?
11. **What happens to a student's existing private credits if they switch to group lessons?**

---

## Reports
This is a real gap — we know almost nothing about what you actually run.

12. **What reports do you run regularly?** Weekly, monthly, whenever. Even the boring ones.
13. **Does anything get printed or exported** — to your accountant, to charter schools, to Regional Center?
14. **Is there a report you rely on that would be painful to lose?**
15. **Is there a report you wish existed** but doesn't?

---

## A Few Loose Ends
16. **The military discount** — how much is it, and does it stack with the sibling and prepay discounts?
17. **Monthly credit card volume** — last time the answer was "550–700." Is that the number of transactions, or dollars? (This decides whether we stay with our current card processor or switch.)
18. **Which file is the real one** — `BlueBuoy_FM` or `BlueBuoy_FM_2024`?
19. **How is a substitute found today** when a teacher calls out? Walk us through it.
20. **Has a lesson ever been scheduled during someone's lifeguard shift** by mistake? (Our system won't know about guard shifts — those only live in Humanity.)

---

## Screenshots That Would Help

No need to stage anything — normal working screens are ideal. **Please avoid or blur real family names and contact info where you can**, since these get shared with the developer.

**Most useful:**
- **Every report you run** over a normal month — just screenshot each one as you go. This is the single most valuable thing on this list.
- A **group class** on the schedule, so we can see how multiple students in one slot are displayed
- The **charter school / Regional Center billing process** — the spreadsheet, QuickBooks, an invoice template, a charter school portal. Anything outside FileMaker.
- The **waitlist screen** as you actually use it

**Also helpful if easy:**
- The **fmSMS Accounts or Gateways tab** (tells us which texting service we're on)
- Anything that's a daily annoyance — a screenshot of the thing you wish worked better

---

*Thanks — the last round genuinely changed the plan. Nothing here is too small to mention.*


---

# PART D — What We Still Don't Know

Listed explicitly so gaps aren't mistaken for completeness.

## Business decisions requiring an owner
- Is the sibling discount cap at the 4th slot still intended policy?
- Should make-up credits expire? (Balances of 24–28 unused credits appear normal.)
- Is family or student the authoritative billing entity?
- What is the military discount, and how does it stack with sibling and prepay discounts?
- How long should a make-up offer be held before cascading to the next family?
- Should the ALL-CAPS "difficult parent" convention be carried forward, or replaced with structured notes?


## Newly identified, values unconfirmed
- **Make-up credit conversion ratios** between lesson types (reported: some number of group credits = one semi-private; ~4 group = one private). Actual ratios, permitted directions, and approval process all unknown. See PRD 3.3.
- **Group class minimums** — whether a class runs, cancels, or merges below a threshold.
- **Whether group pricing varies with class fill.**
- **Whether a group student occupies a sibling-discount tier slot.**
- **Adult class** — group or individual, capacity, eligibility.
- **Military discount** — amount and how it stacks with other discounts.

## Facts still to gather
- **Monthly card volume** — staff answered "550–700," almost certainly transaction count rather than dollars. This determines whether keeping Affinity24/Authorize.Net beats moving to Stripe.
- **Effective card processing rate**, and whether Authorize.Net Account Updater is enabled.
- **Which of `BlueBuoy_FM` and `BlueBuoy_FM_2024` is the live file.**
- **Purpose of legacy files** `11-Wait`, `19`, `19 Time`, `20_BACKUP`.
- **Whether Humanity offers an API** (would allow read-only availability import).
- **Whether current FileMaker backups have ever been restore-tested.**
- All data profiling listed in the technical appendix.

## Areas barely explored
- **Group lessons** — a Group/Non-Group toggle appears throughout the scheduling UI, but group-specific scheduling, pricing, and make-up rules were never discussed.
- **Reporting** — what reports staff actually run and rely on.
- **The QuickBooks/Excel institutional billing process** — described but never seen.
- **Seasonal programs, clinics, or camps**, if any exist.
- **Charter school portals** — two different submission workflows exist; neither has been examined.

## Immediate actions independent of this project
1. **The FileMaker server reports "Connection is not encrypted."** Student names, ages, and medical notes travel unprotected. Fix now — a trusted SSL certificate plus "Require Secure Connections."
2. **Verify backups are restorable.**
3. **Credit card numbers are stored in plain text fields** in FileMaker. This is a live PCI exposure that ends when card storage moves to a tokenized processor.

---

*Compiled from DDR analysis, live system screenshots, and interviews with Blue Buoy ownership and staff. Treat findings as verified where marked, and everything else as a starting point for verification.*
