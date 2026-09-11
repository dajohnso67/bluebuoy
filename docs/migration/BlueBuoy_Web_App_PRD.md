# Product Requirements Document
## BlueBuoy Swim School — Web Application (React + PostgreSQL)

**Source:** Derived from architectural analysis of the legacy FileMaker system (BlueBuoy_FM.fmp12, 22 base tables / 341 table occurrences / 340 scripts / 70 layouts, plus the legacy companion file 20 Time.fmp12).

---

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

### 2.9 Payment Processing — Stay With Affinity24
**Confirmed with staff; this decision can now be made on real numbers.**

| Figure | Value |
|---|---|
| Monthly card volume | **$156,000 – $207,000** |
| Families/students processed monthly | 550 – 700 |
| Charter / Regional Center (check or direct deposit) | ~15% of income |
| Estimated 2026 gross income | **~$2,650,000** |

**Current stack:** Affinity24 (Tustin) as merchant processor → Authorize.Net as gateway → Wells Fargo settlement.

**Recommendation: keep the existing stack.** At roughly $180,000/month in card volume, each 1% of processing rate is about **$1,800/month — $21,600/year**. Interchange-plus pricing through a regional processor is very likely to beat flat-rate pricing at this volume, and the cost of switching (re-collecting or migrating stored payment methods across hundreds of families) is significant and customer-facing.

**Integration approach:**
1. **Accept.js for card capture** — card data goes from the browser directly to Authorize.Net and never touches the application server. This ends the current practice of storing card numbers in plain text (see Sections 6 and 7).
2. **Customer Information Manager (CIM) for stored payment profiles**, charged monthly with a computed amount. **Do not use Authorize.Net's ARB (Automated Recurring Billing)** — ARB expects a fixed recurring amount, and monthly totals vary with prorations, credits, lesson-type changes and rate locks.
3. **Enable Account Updater** on the Authorize.Net account. It refreshes expired or reissued card details on stored CIM profiles automatically, priced per card actually updated. Confirm whether it's currently switched on — it likely isn't.
4. **Abstract the processor behind an internal interface** from day one. The application should ask "charge this family $X"; a swappable adapter handles the provider. Without this, a future move to Stripe means rewriting billing logic rather than replacing one module.
5. **Webhook/callback handling** so charge outcomes (succeeded, declined, refunded) post back into the ledger automatically — this is what removes the manual spreadsheet reconciliation described in 2.8.

**Still worth asking Affinity24:** the current effective rate, whether Account Updater is enabled, and whether their API documentation supports the above. If integration proves painful in development, the abstraction in point 4 keeps a later move to Stripe cheap.

### 2.10 Third-Party Payers (Charter Schools & Regional Center)
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

### 2.11 Broadcast Notifications
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

### 2.12 Instructor Availability, Qualifications & Coverage

**Nothing exists today.** The Staff table has no hours, days, or availability fields — only name, contact, role, CPR certification, and active status. Availability is *implied* by which lesson slots happen to exist. Consequences: nothing knows an instructor doesn't work Mondays; nothing prevents creating a 6am slot; and matching can only find **existing empty slots**, never "times this instructor could teach but nothing is scheduled yet." That last point limits the waitlist and make-up features directly.

**Boundary with Humanity:** staff shift scheduling, on-call availability, and guard shifts live in **Humanity** and stay there. The new app should not attempt to own staff availability it cannot be authoritative about.

**What the app should own:**

1. **Regular teaching hours** — each instructor's normal teaching window per weekday, with date-effective changes (availability shifts seasonally). This enables "could a lesson go here?" rather than only "is this slot empty?" It's about lesson scheduling capacity, not staff employment hours, so it doesn't duplicate Humanity.
2. **Teaching qualifications** — which lesson types and levels each instructor can teach. Humanity has no idea about this and neither does the current system; it lives in staff knowledge. It's the missing input for both routine scheduling and finding substitutes.
3. **Breaks within a schedule** — the legacy `flag_has_break` / `Create Break` mechanism carries over.

**Known limitation — confirmed as low risk.** Because guard shifts live only in Humanity, the app cannot detect a lesson scheduled during an instructor's lifeguard shift. Staff report this only arises when someone is deliberately switched from guarding to subbing for the day, which is an intentional act rather than an error. **No engineering effort is warranted here.** If it ever becomes a real problem, a read-only import of Humanity shift data (if its API allows) is the fallback.

### 2.13 Emergency Coverage (Teacher Call-Out)
**The current process, described by staff step by step:**
1. Open the absent teacher's schedule for that day.
2. Cross-reference every other teacher working during those hours.
3. Look for an opening in their schedule — a genuinely empty slot, a student already marked out, or a student whose start date is the following week (making the current day available).
4. Check the student's constraints before placing: **required instructor gender**, whether they should be paired higher or lower, and **whether a sibling is enrolled around that time** (aim for the same slot or immediately after).
5. If nothing fits exactly, widen to nearby times, or check the family's **previously stated availability** from earlier requests to see if they can flex for the day.
6. **Last resort: the on-call teacher** takes whatever couldn't be placed.

This is the matching engine (2.4/2.5) applied under time pressure, with three constraints the system must respect — instructor gender requirements, level pairing tolerance, and sibling proximity — plus an explicit fallback to on-call staff.
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

### 2.14 Level & Pool Assessment
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

### 2.15 Parent Portal
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

### 2.16 Documents & Forms (Per Student)
**Confirmed from live screens.** Each student record has a Forms tab with document slots. Four exist — Registration & Liability, Payment, Other, Withdrawal — but **only Registration & Liability and Withdrawal are used**. Documents arrive either from website registration or on paper at the pool and are uploaded per child, with a submission date.

**Requirements:**
1. **Per-student document storage** with type, submission date, and preview — carrying forward the two types actually in use.
2. **Don't rebuild unused slots.** Payment and Other are dead; replace with a general attachment capability rather than fixed empty categories.
3. **Military ID upload — a requested addition.** Families with a military discount need somewhere to attach proof. This implies a **military discount** exists that isn't yet captured elsewhere in this document; confirm the discount amount and how it interacts with sibling and prepay discounts.
4. **Digital intake ties in directly** (see 2.14) — registration and liability captured through the portal lands here automatically instead of being uploaded by staff.

### 2.17 Notes History (Instructor & Deck Manager)
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

### 2.18 Student List Conventions (Confirmed)
The student list panel encodes information visually:
- **Green dot** = actively enrolled. **No dot** = not currently enrolled.
- **Blue name beneath the student** = the parent's first name — how staff disambiguate similar student names at a glance.
- Search by last name surfaces similar-beginning matches, not exact matches only.
- **ALL-CAPS student names** appear here too (see 3.2).

**Requirements:** carry all of these forward as explicit, labeled UI (enrollment status badge, parent name line, fuzzy last-name search) rather than color/typography alone — same reasoning as 3.2.

### 2.19 Reporting
**Confirmed with staff.** Previously the largest unexplored area; now documented.

**Run daily:**
- **Weekly enrollment by lesson type, compared to the same period in prior years.** Counts per type (`SP`/`PR`/`PM`/`ST`/`GR`/`AD`), a weekly total, the prior-year total, and the year-over-year change. **This is currently compiled by hand and typed into Excel.** Representative volume: ~1,100 enrollments per week, of which roughly 800 semi-private, 150 private, 130 Parent & Me, 34 group, 8 stroke tech, 3 adult. Make-ups and sub-covered lessons are excluded from the count.
- **Free trials and make-up trials from the previous day** — staff call these families to follow up: convert them, find a different time if the slot didn't work, or reassign if the teacher felt the match was wrong.
- **Notes from the pool deck and instructors** — lesson changes, requests, and impromptu make-ups arranged after the scheduling office closed.

**Run weekly/monthly:**
- **Waitlist report of open requests**, checked against the schedule board for newly opened spots. Staff explicitly want this eliminated and automated — it is exactly the matching engine in 2.4.

**Run monthly:**
- **Prepays ending this month** where the student remains enrolled into next month. Triggers a reminder text/email: re-prepay, or the account converts to auto-billing on the 1st.
- **Tuition verification against the Authorize.Net batch** that processes on the 1st — confirming each enrolled student's charge matches.

**Exported annually:**
- **QuickBooks General Ledger, P&L, and Balance Sheet** to the accountant in January/February for tax preparation.
- **A separate Excel spreadsheet tracking Regional Center payments** — what's outstanding and what's been paid.

**Named as painful to lose:**
- **The absence lookup** — a button on the schedule board listing students who have reported an absence. Used all day, every day. Note this is a *scheduling feature*, not a report, and should be treated as such.
- Free trial / make-up trial reports.
- Notes from deck and instructors.
- The per-student attendance sheet.

**Requested but doesn't exist:**
1. **A quick summary of monthly tuition for auto-pay students** — the current absence of this is part of why month-end verification is manual.
2. **Students who haven't attended for 2+ weeks without notice.** This is the attrition-warning idea, requested independently by staff, and it also overlaps the unpaid-lesson exception view in 2.3.
3. **Lesson type changes on ongoing enrollment** — e.g. Parent & Me to Semi-Private — flagged so billing can adjust the prepay or monthly rate. This is precisely the 1–2 times per month communication gap described in 2.8, and a report that surfaces it automatically would close that loop.

**Design requirements:**
1. **The weekly enrollment comparison becomes a live report**, not a hand-built spreadsheet. The system holds enrollment, lesson type, and history — a year-over-year comparison is a query. This alone removes a daily manual task.
2. **Keep an export path to QuickBooks and Excel.** QuickBooks remains the accounting system; the new app should produce clean exports rather than attempt to replace it.
3. **Exception-driven reports rather than lists to scan** — the three requested reports above are all "show me what needs attention," consistent with the billing run (2.8) and daily review (2.3).
4. **Preserve the absence lookup as an instant, always-available action**, not something buried in a reports menu.

---

## 3. Business Rules

### 3.1 Lesson Types, Class Structure and Eligibility
**Lesson type codes** (decoded — these appear throughout the legacy schema in rate tables, make-up counters, and discount tiers):

| Code | Class | Group? | Eligibility | Capacity |
|---|---|---|---|---|
| `PR` | Private | No | — | 1 |
| `SP` | Semi-Private | No | — | 2 |
| `PM` | Parent & Me | **Yes** | Ages **0–3**, **no level requirement** | 6 |
| `GR` | Group / Stroke Prep | **Yes** | Age **7+** and Level **9–12** | 6 |
| `ST` | Stroke Technique | **Yes** | Age **10+** and Level **10–12** | 6 |
| `AD` | Adult | **Yes** | Age **16+** | 6 |

**Also seen in scheduling:** `M SP` and `M PR` — make-up semi-private and make-up private. These appear when an open group slot is repurposed (see below), so the schedule distinguishes a regular lesson from a make-up occupying the same slot.

**Group classes run on a fixed annual timetable.** Set times for each group type, largely unchanged year over year. Families join an existing class rather than a class forming around demand — which means group availability is a *seat* question, never a scheduling question.

**Group classes run regardless of enrollment** — a class with one student, or none, still happens. The one exception: if a group slot is completely empty and a teacher calls out, the slot gets repurposed for `SP`, `PR`, `M SP`, `M PR`, or `PM`. Worth modeling as a deliberate action ("repurpose this empty group slot") rather than an ad hoc override.

**Pricing does not vary with class fill.** A student in a class of two pays the same as one in a class of six.

**Three distinct group class types**, all capped at **6 students**. Confirmed with ownership.

**Schema implication — no special handling needed.** The legacy `Lessons` table already carries `Slots_Total` and `Slots_Available`, with `Lesson_Schedules` linking students to a lesson. A group class is one lesson record with 6 seats and up to 6 student rows attached — structurally identical to a private (1 seat) or semi-private (2 seats). **Capacity is simply a per-type number.** This is what the "Total/Avail" figures on the Deck Manager search display.

**Matching implication — this does change the search logic.** For group and semi-private types, "is there an opening?" means *is there a free seat in an existing class*, not *is this time slot empty*. Every matching feature (2.4, 2.5, 2.12) must evaluate **remaining capacity**, not emptiness — and for groups, must also check that the student's level fits the class.

**Deliberate tier-ordering strategy — confirmed.** Where a family has both group and non-group lessons, staff place the **group lesson in the first (undiscounted) tier**, so the more expensive private or semi-private lessons receive the tiered discount and the family's total cost is lower. This is the same intentional ordering used for charter-funded siblings (2.8). The system must let staff control tier assignment order rather than assigning it automatically.

### 3.2 The Adult Class — A Separate Billing Model
**Confirmed with staff.** Adult (`AD`) is a group class, capacity 6, ages 16+. **It does not use monthly tuition at all.**

- Adults purchase either a **single class**, a **package of 4**, or a **package of 8**.
- A lesson is **deducted from their balance only when they actually attend**, based on the teacher's roll for that day.
- **The known problem:** adults frequently don't notify the school when they'll be absent. Since nothing is deducted for a no-show, the seat is simply lost. Staff explicitly flagged this as something they want addressed.

**Requirements:**
1. **Class-pack balances are a distinct payment type** — purchased quantity, remaining balance, purchase date. Not a monthly ledger entry.
2. **Attendance drives deduction.** A lesson is consumed when marked present, not when scheduled.
3. **No-show handling needs a deliberate policy decision.** Options include a cancellation window (notify by X hours and the lesson isn't deducted; don't notify and it is), or simply reporting on repeat no-shows so staff can have the conversation. This is a business decision, not a technical one — but the current behaviour of silently absorbing the loss is what staff want changed.
4. **Balance visibility for the adult** — a portal view showing lessons remaining would likely reduce both no-shows and phone calls (ties to 2.14).

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

### 3.3 Information Encoded in Formatting & Color (Migration-Critical)
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

### 3.4 Make-Up Credit Conversion Between Lesson Types
**Confirmed with staff — ratios verified.** Make-up credits are convertible between lesson types at fixed rates, and conversion works **in both directions**.

For conversion purposes, `GR`, `ST`, and `PM` are all treated as a single **"group" denomination**.

| From | To |
|---|---|
| 2 Semi-Private | 1 Private |
| 1 Private | 2 Semi-Private |
| 2 Group (`GR`/`ST`/`PM`) | 1 Semi-Private |
| 4 Group (`GR`/`ST`/`PM`) | 1 Private |
| 1 Private | 4 Group |

**All listed conversions are permitted, in both directions.** A student who switches from private to group lessons keeps their existing private credits as private — they aren't forcibly converted, but can be exchanged when redeemed.

**This confirms the credit model is a single denominated system**, not six independent balances. The legacy counters (`MU_PR_Total`, `MU_SP_Total`, etc.) are units in one currency, and a balance in one type carries redeemable value in another. Outstanding liability must be valued accordingly: 24 semi-private credits are also 12 private lessons.

**Conversion is a staff decision at redemption time**, not automatic — the option is chosen when the make-up is being scheduled.

**Credits transfer between siblings.** Staff move make-ups from one child to another within a family, recording the quantity and type moved as a manual note. This is a real workflow with no system support today.

**Requirements:**
1. **A configurable conversion table** holding the ratios above, editable without code changes.
2. **Matching and redemption honour conversions automatically** — a student holding only group credits should surface as eligible for a semi-private make-up, with the conversion shown, so staff never do the arithmetic.
3. **Sibling transfer as a first-class action** — move N credits of type X from student A to student B, recorded as a dated event with both balances updated. Replaces the current manual note.
4. **Conversions and transfers are recorded as events** — what moved, at what rate, by whom, when — so any balance change is explicable later.
5. **Reporting values credits in a consistent denomination** so total outstanding liability is meaningful.

### 3.5 Multi-Child / Multi-Lesson Pricing (the "sibling discount")

**A third discount exists — first responders.** Confirmed with staff: a **10% discount for military, police and fire department** families. It **stacks with both the sibling discount and the prepay discount**. Proof of eligibility (ID) is requested at signup.

**Requirements:** model it as a distinct percentage discount on the family record, applied after the sibling tier calculation and alongside prepay. Staff have specifically asked for **a flag recording whether ID has been provided**, tied to the document upload in 2.16 — so an unverified discount can be reported on rather than quietly persisting.
This is **not** a flat family discount — it's a progressive per-slot discount, directly carried over from the legacy `Rate_1`–`Rate_8` calculation logic:

- 1st lesson slot in a family/household: full rate, no discount.
- 2nd slot: full rate minus 1× the lesson type's discount amount.
- 3rd slot: full rate minus 2× the discount amount.
- 4th slot and beyond: full rate minus a **capped** 3× the discount amount (the discount does not continue growing past the 4th slot).

**Action required before build:** the legacy formula hard-codes this 3x cap with no documented rationale. Confirm with management whether this cap is still current business policy before encoding it as a permanent business rule — the risk of silently migrating a stale or unintended rule is real (see Section 4, migration risks).

**New finding, confirmed from a live student record — but flagged as a special case, not a standard rule:** that record ("CC Monthly 50% off PRIV" — 50% off private lessons) is a one-off arrangement for a specific student getting private lessons at semi-private pricing, not something the school normally offers. This isn't a second standard discount tier — it's evidence that **the system needs to support manually-applied, one-off pricing overrides** for special arrangements management approves on a case-by-case basis, distinct from the standard sibling-discount formula. Worth designing as an explicit "special pricing override" field/flag (visible on the family/student record, Management-only to set, with a required note explaining why) rather than folding it into the standard rate/discount tables — that keeps one-off exceptions from being mistaken for policy the next time someone reads the pricing logic.

### 3.6 Rate Changes, Annual Rollover, and Prepay Rate Locks
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

### 3.7 Prepay Plans, Rate Locks, and Refunds
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

### 3.8 Enrollment Holds and Prepaid Credit
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

### 3.9 Closures: Two Distinct Types
The system currently treats these the same way, but they behave oppositely and the new app should model them separately:

- **Scheduled annual closure** (the two-week December/January closure): known in advance, absorbed into the annual flat rate, **generates no make-up credits**. Billing is unaffected — note that `Billing_Months` has no lesson-count field, so monthly tuition is flat regardless of how many lessons fall in a given month. This is a normal tuition model and worth preserving deliberately rather than by accident.
- **Incidental closures** (individual holidays like Memorial Day and Presidents Day, confirmed on live student records; weather; pool maintenance): these **do** generate Out Lessons and make-up credits for every affected student, via a bulk operation.

The new app needs a closure record with an explicit type that determines whether make-ups are issued — plus, for incidental closures, the "close this pool/date and issue make-ups to everyone affected" bulk action described in 3.4. Also worth noting: the legacy `Holiday_Dates` table holds only 6 records, so it appears to be a small working set rather than a durable multi-year closure calendar — the new system should keep a real, permanent closure calendar.

### 3.10 Cancellation Rules
- A cancelled lesson (marked absent, or cancelled in advance) generates a make-up credit by default, unless explicitly flagged not to (the legacy "do not issue" guard — this should map to an explicit reason code: e.g., late cancellation past a cutoff, no-call/no-show, vs. instructor-initiated cancellation).
- Cancelling a *booked make-up* (as opposed to the original lesson) should restore the credit rather than consuming it a second time.
- Business policy question to confirm before build: does a late cancellation (e.g., same-day) forfeit the make-up credit today? The legacy system supports this via the guard flag, but the specific cutoff rule isn't encoded in a calculation — it appears to be a manual staff judgment call. Decide whether to formalize this into an automatic rule or keep it as staff discretion.
- **New finding:** holiday closures (e.g., "HOLIDAY CLOSURE MEMORIAL DAY," "CLOSED PRES. DAY," seen directly on a real student's Out Lessons list) go through this exact same mechanism — a business-wide closure generates an Out Lesson (and presumably a make-up credit) for every affected student automatically, confirming the `STU_Schedule_Holiday_MU_Bulk` script found in the DDR is a real, actively-used bulk operation. The new app needs a "close the pool for a date, generate make-ups for everyone affected" action as a first-class admin tool, not just individual cancellation handling.
- **New open question, prompted by real data:** one student record we looked at had **28 accumulated, unused private-lesson make-up credits.** That's a lot sitting unused. Worth asking management: should make-up credits expire after some period? Right now nothing in the legacy system appears to enforce that, and unlimited accumulation could become a real liability (families expecting to redeem years of banked credits at once). Added to the open questions list below.

### 3.11 Student Profile Notes (Medical, Special Needs, History)
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

### 3.12 Free Trials
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

**Resolved since the last revision:** make-up credit conversion ratios, group class minimums and pricing, Adult class structure, the military/first-responder discount, monthly card volume, which FileMaker file is live, how substitutes are found, and what reports staff actually run. Those are now folded into the sections above.

**Still open:**
1. Is the 3x sibling discount cap at the 4th+ lesson slot still intended policy, or should it scale differently? (Hard-coded in the legacy calculation with no documented rationale.)
2. What is the late-cancellation cutoff for forfeiting a make-up credit — and should it become an automatic rule, or stay staff discretion?
3. Is family-level or student-level billing the canonical source of truth for invoicing? (`Billing_Months` populates both keys today.)
4. **Should make-up credits expire?** Balances of 24–28 unused credits appear normal, and with confirmed conversion ratios the true liability is larger than a raw count suggests. Decide the policy; build the unused-credit report either way.
5. **How should Adult class no-shows be handled?** Staff have flagged the current behaviour (seat lost, nothing deducted) as a problem. Options include a notification window or simply reporting repeat no-shows — a business decision, not a technical one.
6. How long should a make-up offer be held before cascading to the next family in the queue?
7. Should the ALL-CAPS "difficult parent" convention be carried forward, or replaced with a structured, access-controlled account note?
8. Should families ever get self-service make-up booking, or does it stay desk-mediated?
9. For waitlist matches: once staff trust the matching over a season, is auto-notifying the family (with a claim window) ever in scope, or does every match always route through desk staff?
10. How common are one-off pricing arrangements (like the private-at-semi-private-rate case)? If frequent, the special pricing override deserves proper design rather than a workaround.

## Appendix: Legacy File Inventory (confirmed from FileMaker Server host)
The DDR analysis referenced several files that turned out to exist outside the original export. Confirmed live on the host:

| File | Status | Action needed |
|---|---|---|
| `BlueBuoy_FM` | Analyzed (this PRD is built from it) | **Confirmed as the live production file.** |
| `BlueBuoy_FM_2024` | **Resolved — this is an archive, not a live file** | `BlueBuoy_FM` is the live system. Families with no enrollment for 10+ years are moved into `FM_2024` because the system slows as record count grows. Rarely accessed, but must stay reachable in case a family returns. **Migration implication:** the new system needs an archive/restore concept rather than deletion, and the archived file should be preserved as part of the frozen historical archive (Section 6). Performance-driven archiving should not be necessary in PostgreSQL — proper indexing handles this volume — so this practice can end at cutover. |
| `Instructor_Entry` | **Analyzed** | Confirmed: the actual iPad-facing app. Holds no data of its own — pure UI layer over `BlueBuoy_FM` via external reference. Surfaced the Deck Manager role, PSOS attendance-write pattern, deck-level notes, and payments-due/free-trial reports — all now reflected in Sections 1 and 2.1 |
| `Launcher_Teacher` | **Confirmed live via screenshots, DDR not yet reviewed** | Confirmed: matches description exactly — Schedule and Student Levels only, no Deck Manager tools. The day-to-day Instructor experience: read-only view of any teacher's schedule, date navigation, and a dedicated catch-up button for backfilling missed attendance from a prior day. Now reflected in Sections 1 and 2.1. Export the DDR when convenient to confirm field-level details, but it's no longer a blocker |
| `fmSMS` | **Confirmed live — commercial Databuzz add-on, not custom code** | Identified as a "bring your own gateway" tool: connects to one of ~20 third-party SMS providers rather than sending messages itself. Still need to check its Accounts/Gateways tab to see which specific provider (Twilio, ClickSend, etc.) is configured — that resolves the keep-vendor-vs-migrate decision for Section 2.5 |
| `20 Time` | Analyzed (legacy roll-sheet system) | No further action — superseded by current system |
| `11-Wait`, `19`, `19 Time`, `20_BACKUP` | **Not yet analyzed** | Purpose unconfirmed — worth a quick check with whoever manages the server before assuming they're safe to leave out of the migration |
