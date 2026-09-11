# Search parity enumeration

The set of searches the Scheduling & search phase must reproduce. Rule 5 of `migration-prompt.md`: acceptance is **set-equality against these searches on the same data**, not a feature checklist.

**Wayfinder ticket:** [Search-parity daily-search enumeration](https://github.com/dajohnso67/bluebuoy/issues/7).
**Status:** the system half (everything the DDR encodes) is complete below. The staff half (ad-hoc finds and Saved Finds, qa.md Q55–Q58, riding [staff question batch 1](./staff-batch-1.md) Section C) is pending and goes in Part 5 when it returns. The parity set is the union.

Every search carries an id (`SP-nn`) so the gate, tests, and later tickets can cite one line. Source: `resources/DDR/BlueBuoy_FM_fmp12.xml` (office file) and `Instructor_Entry_fmp12.xml` (iPad app), DDR of 2026-08-17. Field and script names are FileMaker's; the domain terms are in `CONTEXT.md` (slot = `Lessons`, enrollment = `Lesson_Schedules`, lesson = `Lesson_Attendance`, make-up = `Lesson_Out`).

## Part 1 — Where staff type their own finds

Native Find mode is exposed by button (a "Re-find Ctrl+R" bar with **Enter Find Mode** and **Open Edit Saved Finds**) on exactly these layouts. Ad-hoc finds and Saved Finds can only be typed here; every other screen searches by script or by global criteria fields.

| Layout | File | Table searched | Note |
| --- | --- | --- | --- |
| `Lesson_Availibility_NEW` (+ `_Group`, `_5_8_25`, legacy `Lesson_Availibility`) | office | slots (`Lessons`), one variant on enrollments | the office availability grid |
| `L008_Deck_Manager_Search_Lesson_NonGroup` / `L008b_..._Group` | iPad | slots (`Lessons`) | the screen in the package's 2.6 screenshot |
| `L009_Deck_Manager_Search_Student` | iPad | students | Find mode only, no Saved Finds button |

**Saved Finds are not in the DDR.** FileMaker stores them per account, outside the design report. The only source is staff (Q56, the screenshot request). Whatever Q56 returns is the seed list for `saved_search`.

Fields staff can find on from these layouts (the union of what the layouts place, matching package 2.6's observed list): student name, age, level, pool, lesson type, make-up flag (`Lesson_MU`), hold status and hold notes (`Lesson_Hold`), start and end date, instructor, instructor nickname and gender, time, day, lesson notes and scheduling-office notes, `Slots_Total` / `Slots_Available`, `flag_drop`, group vs non-group (`Type_Assignment`), free-trial flag, and on the student screen every enrollment, make-up, waitlist, and family-note field in its portals.

## Part 2 — Structured search forms (criteria fields, not Find mode)

These are the searches with a form: global fields on `Preferences` feed a relationship whose predicates *are* the query. Blank criteria match everything via a `"*"` key. The predicate list is the spec.

### SP-01 Office lesson finder (`Search_Lessons`, office file)

Finds slots for a student being scheduled. Fourteen predicates against `Lessons`:

| Criterion | Match | Notes |
| --- | --- | --- |
| Instructor | equal on `id_staff` | by id, not name |
| Instructor gender | equal | |
| Lesson type | equal on `Type` | |
| Pool | equal on `Pool_List` | |
| Complete openings only | equal on `flag_complete_opening` | slot has **all** its capacity free (`Slots_Total = Slots_Available`) |
| Day range | start ≤ `Day_Number` ≤ end | |
| Time range | start ≤ `Time_Start` ≤ end | |
| Age range | start and end each match `Approximate_Age_Range` | for Semi-Private slots only: the range is the current student's age **±2**; otherwise wildcard |
| Level range | same shape against `Approximate_Level_Range` | Semi-Private: current student's level **±2** |
| Family member | equal on `id_student_key` | "slots where a sibling already is" (`g_Search_flag_by_family`) |

Result columns: instructor, time, slots total / available, day. Selecting a slot opens `Search_Lessons_Selected`, which shows the slot's open-or-future enrollments and the chosen student's make-up balances by type.

### SP-02 Deck Manager schedule filter (`L003_Deck_Manager_Search`, iPad)

Filters enrollments (`Lesson_Schedules`) by up to six typed keys plus a date window, each key defaulting to `"*"`:

| Criterion | Match |
| --- | --- |
| Date window | `Date_Start` between `g_Date_Start` (default 1900-01-01) and `g_Date_End` (default 2200-01-01) |
| Instructor, lesson type, day, pool, student, time | equal on a `Char_*` key field each |
| Always | `Status ≠ "Closed"` and `ID_Lesson_Schedule ≠ "DUMMY"` |

Result columns include instructor, student, day, type, time, make-up flag, phone, pool, hold, payment plan, balance due, and the registration / liability form flags.

### SP-03 Out-lesson date range (`L008` "out search", iPad and office)

Two-step: `Lesson_Out` rows with `Date_Out` between `g_DateSearchStart` and `g_DateSearchEnd` (defaults 1950 / 2150), collected to a list of slot ids, then a find on `Lessons.ID_Lessons` for each. Answers "which slots have someone out in this window". A toggle variant (`LES_Toggle_Out_Search`) finds slots whose `Out_Date_List` contains today.

### SP-04 Student lookup (`Search_Student`, `Search_Student_Add_to_Family`, office; Master Details finds, both files)

A single text box (`g_Search`). The office scheduling screen runs **Perform Quick Find** on the typed text; the student-picker card and the iPad find on `Name_Full_Reversed` (`Last, First`). Columns: first, last, level, id, email, initials, age, make-ups left.

## Part 3 — Scripted searches (canned finds behind buttons and screens)

Each row is one find request set. `omit` means a FileMaker omit request (set difference).

### Schedule and availability

| Id | Script | File | Returns |
| --- | --- | --- | --- |
| SP-10 | `Find_Initialize_Availibility` (0076 / 0076.1) | office | slots for today's weekday, omitting `flag_drop`; the `.1` variant runs on enrollments with `flag_open_or_future` |
| SP-11 | `Find_for_Set_Date_Finish` (0075 / 1602) | both | slots for a chosen day **and** instructor, then constrain to omit `flag_drop` |
| SP-12 | `Find_Lessons_Current` (0100, iPad, on layout enter) | iPad | the signed-in instructor's enrollments for today: `Date_Start ≤ today`, `flag_open`, day = today's two-letter day code, `id_staff` = me |
| SP-13 | `Search_Staff_and_Date` (1200) | iPad | an instructor's roster for a date: three requests (open with end ≥ date; open with no end; open with no start and end ≥ date), omit `flag_omit_from_sched` (end before start); run twice, once by the slot's `Day` and once by the enrollment's own `Day` |
| SP-14 | `LES_Search_flag_ongoing_break` (4011 / 1608) | both | slots with an ongoing instructor break |
| SP-15 | `RPT_View_Lesson_Schedules` (8005) | office | all enrollments omitting trials and end-before-start rows |
| SP-16 | `RPT_Lesson_Attendance` (8020) | office | enrollments covering a date on a weekday, omitting breaks (the printed roll sheet) |
| SP-17 | `LES_Show_Year` / `LES_Show_All` (4008 / 4009) | office | one student's enrollments, optionally one `Date_Year` |
| SP-18 | `LES_Omit_Empty_Lesson_Type` (4014) | office | constrain: drop enrollments with blank lesson type |

### Students

| Id | Script | File | Returns |
| --- | --- | --- | --- |
| SP-20 | `STU_Constrain_Active` (1002 / 1710) | both | constrain current set to `flag_active` |
| SP-21 | `Search_Students_Today` (1502) | iPad | students with an open enrollment starting on the chosen date (sorted last name) |
| SP-22 | `Search_Students_Out_Instructor` / `_Out_Time` (1503 / 1504) | iPad | enrollments whose `Lesson_Out_Date_Key` list contains the date, sorted by instructor or by time |
| SP-23 | `STU_Check_for_Duplicates` (1049) | office | students matching first name + last name + date of birth (the duplicate guard on create) |
| SP-24 | `OUT_Show_Year` / `OUT_Show_All` (3004 / 3005) | office | one student's make-ups, optionally one year |
| SP-25 | `STF_Show_Active_Staff` (2004) | office | staff with `flag_active` |

### Reports (a report is a find plus a sort)

| Id | Script | File | Returns |
| --- | --- | --- | --- |
| SP-30 | `RPT_Payments_Due` (8100 office; 8012 iPad) | both | students with an open-or-future enrollment (`Status > "d"`), **omitting**: rows already paid this month (`Amount_Paid_1 = "*"` on the month's billing record), instructor placeholders (`Name_First = "Inst"`), `Payment_Plan` Charter School, Don't Bill, or (iPad) Billing, free-trial enrollments, and blank lesson type. `_OMIT_MUS` (8101) also omits make-up enrollments. Sorted by day, time. |
| SP-31 | `RPT_Free_Trials` (8010 office; `Search_Free_Trials` 1501 iPad) | both | enrollments flagged trial and not yet checked, on a date (office); students with a chosen free-trial date (iPad) |
| SP-32 | `RPT_Waitlist` (8015) | office | waitlist rows requested on or before a date |
| SP-33 | `RPT_Lesson_Absentees` (8035) | office | attendance rows for a month/year with `Student_Level = "A"` (absent) |
| SP-34 | `RPT_Notes_to_Scheduling_Office` (8000) / `RPT_DM_Notes_to_Scheduling_Office` (8030) | office | attendance rows with unread instructor notes within three days of a date; Deck Manager notes sent on a date and not yet checked |
| SP-35 | `RPT_Families_CC_Monthly` / `_DD_Monthly` / `_Prepay` (8025–8027) | office | active students whose `Payment_Plan` contains `CC`, `DD`, or `Pre-` |
| SP-36 | `STU_Create_Email_List` (1045) | office | families by id list (mailing list) |
| SP-37 | `PRF_Create_Billing_Records_PSOS` (9005b) | office | families with `flag_active` (the set the month generator bills) |

Not searches, but present and worth knowing: the `Attendance_Viewer` (student's attendance by day/week/year via relationship) and `Lesson_MU_Select` (make-up balances by type) are lookups on one record, not finds.

## Part 4 — Derived dimensions the new search must compute

These are stored or calculated in FileMaker and searched as if they were plain columns. Parity fails if any is missing from the criteria builder.

| Dimension | FileMaker | Meaning |
| --- | --- | --- |
| Available capacity | `Lessons.Slots_Available` | `Slots_Total` minus open-or-future non-trial enrollments plus outs, zero when the slot has a break |
| Complete opening | `Lessons.flag_complete_opening` | nothing enrolled at all |
| Semi-private age / level fit | `Approximate_Age_Range`, `Approximate_Level_Range` | current occupant's age or level ±2, wildcard for other types |
| Enrollment status | `Lesson_Schedules.Status` → `flag_open`, `flag_future`, `flag_closed` | Open when today is inside start..end; Closed when ended or unbounded; Future when not yet started |
| Out dates on an enrollment / slot | `Lesson_Out_Date_Key`, `Out_Date_List` | the list of make-up dates, searched by containment |
| Hold | `Lesson_Hold` (free text) | a held enrollment and why; searched by text |
| Make-up enrollment | `Lesson_MU` | the enrollment is itself a make-up |
| Trial | `flag_trial` = free trial or make-up trial | |
| Group vs non-group | `Type_Assignment` (`GR`, `ST`, `PM`, `AD`, else private/semi) | the L008 / L008b split |
| Placeholder rows | `ID_Lesson_Schedule = "DUMMY"`, `Name_First = "Inst"` | per-staff placeholder enrollments and instructor pseudo-students that every real search must exclude; the import must drop or mark them |

## Part 5 — Staff-reported searches (pending Q55–Q58)

**Received out of band — Round 2 (2026-09-10), before batch 1 Section C returned.** Staff named these unprompted while answering the reports questions (qa.md Q103–Q105); each is cross-referenced to the DDR row it runs:

| Id | In the staff's words | Runs | Same as |
| --- | --- | --- | --- |
| SP-50 | "a button on top of our Schedule board that allows us to find students that have reported an absence" — used all day; "really a scheduling feature instead of a report" | the schedule board's `Search Out` button, for the day shown | SP-22 / SP-03 |
| SP-51 | "a wait list report of open requests" checked weekly or monthly against the board for spots that opened — staff want it automated away | `RPT_Waitlist` | SP-32 |
| SP-52 | "Notes from pool deck or teachers" (the `Teacher Notes to Scheduling Office` button) | `RPT_Notes_to_Scheduling_Office` | SP-34 |
| SP-53 | the `Deck Mgr Notes to Scheduling Office` button | `RPT_DM_Notes_to_Scheduling_Office` | SP-34 |
| SP-54 | "Free Trials or Make up trials that came in the day before" (the `Trials` button) | `RPT_Free_Trials` for yesterday | SP-31 |
| SP-55 | the `Lesson Attendance` button | `RPT_Lesson_Attendance` | SP-16 |
| SP-56 | monthly: "enrolled student's Pre Pays that will be ending for the current month and still have open enrollment going into next month" | a hand-built find over billing months — no scripted equivalent in the DDR | new; Part 6 computes it from the exports |
| SP-57 | monthly: "currently enrolled students to check that their monthly tuition payment matches … the Authorize.net batch that will process on the first" | a hand-built find plus a spreadsheet cross-reference | new; becomes a billing-run exception view |
| SP-58 | "Attendance sheet on each student's account" — a layout, not a find, but named as painful to lose | the student Attendance layout (year grid per type, Out Lessons, totals) | not a search; a screen the Attendance phase must carry |

Screenshots of SP-50, SP-52–SP-55 and SP-58 came back with Round 2 and live only in the gitignored original of that document. **Still pending from Section C:** the rest of Q55, every Saved Find (Q56), the most complex search (Q57), and the wished-for searches (Q58).

*Expected shape for the remainder:*

- **SP-5x Daily ad-hoc finds (Q55):** one line each, in the staff's words, then the criteria in Part 1's vocabulary.
- **SP-6x Saved Finds (Q56):** name as saved, the layout it belongs to, the criteria from the screenshot.
- **Q57 most complex search ever built:** recorded as a worked example the criteria builder must express.
- **Q58 searches wanted but impossible today:** listed separately, not in the parity set (parity is against what runs, not what is wished for), but carried into the criteria builder's backlog.

## Part 6 — How the gate reads this

The Scheduling & search gate passes when, on the same imported data, each `SP-nn` row returns the same set of ids in the new system as in FileMaker. Parts 2 and 3 are executable now against the exports from [Live CSV export for data profiling](https://github.com/dajohnso67/bluebuoy/issues/6): each row is a filter over the exported tables, so the expected sets can be computed before any UI exists. Part 5 joins the set when the batch returns.
