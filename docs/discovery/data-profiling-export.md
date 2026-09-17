# Data profiling export — what to pull from the live FileMaker file

**Wayfinder ticket:** [Live CSV export for data profiling](https://github.com/dajohnso67/bluebuoy/issues/6).
**Why:** five facts the DDR cannot yield (record date ranges, instructor first-name collisions, dual-key disagreements, ALL-CAPS name counts, active-family count and card volume) gate the dual-key strategy, the decode pass, and the Authorize.Net-vs-Stripe question. This page is the exact export list; `scripts/profile_exports.py` turns the exports into those facts.

Record counts below are from the DDR generated **2026-08-17** from `BlueBuoy_FM.fmp12` on `s842624.fmphost.com`; the live export will differ slightly.

## Before exporting

1. **Export from `BlueBuoy_FM`.** Round 2 (qa.md Q99, answered 2026-09-10) confirmed it is the live file, so the DDR and the field list below are canonical. `BlueBuoy_FM_2024` is an archive of families idle for ten years; add a **second, smaller export from it** — `Families` and `Students` only, the same fields — into `resources/exports/YYYY-MM-DD/archive/`, so the archive decision (what the import does with those families) has row counts and date ranges to stand on.
2. Log in with a **Full Access** account. Export needs the *Allow exporting* privilege.
3. Work in FileMaker Pro (desktop), not WebDirect.

## Export settings (same for every table)

1. Go to a layout based on the table (Layout menu, or Manage Layouts; any layout whose table occurrence is the base table works).
2. **Records → Show All Records.** Confirm the record count in the toolbar matches the table (not a found set).
3. **File → Export Records…**
4. Type: **Merge Files (`*.mer`)**. Merge writes the field names as the first row; plain *Comma-Separated Text* does not, and the profiling script needs the header.
5. Filename: the table name, e.g. `Students.mer`.
6. In the *Specify Field Order* dialog: source = **Current Table** (never a related table occurrence), add exactly the fields listed below, in any order.
7. Character set: **UTF-8**. Uncheck **Apply current layout's data formatting**.
8. Save every file into a single folder named by the export date: `resources/exports/YYYY-MM-DD/`. That folder is gitignored; nothing under it is ever committed.
9. Rename `.mer` to `.csv` (the content is CSV with a header). The script accepts either.

## Never export

- `Families.Credit_Card_1`, `Credit_Card_2`, `Credit_Card_1_Exp_Date`, `Credit_Card_2_Exp_Date`, `Additional_CC_Notes`
- `Students.Credit_Card_Num_1`, `Credit_Card_Num_2`, `Credit_Card_Exp_Date_1`, `Credit_Card_Exp_Date_2`
- Any container (`Binary`) field: `Staff.Image`, `Staff.CPR_Certification`, `Students.Form_*`, everything in `Documents`
- Free-text notes for this pass: `Students.Instructor_Notes`, `Billing_Months.Payment_Notes`, `Families.Notes_General`, `Waitlist.Notes`, `Lesson_Attendance.Intructor_Notes_to_Office`. Free text is a known landmine and gets its own decode ticket; it may also carry card numbers.

These are stored as plain text in FileMaker today. Leaving them out of the export is the whole of the PCI story for this ticket.

## Tables and fields

Tables not listed (`Documents`, `Notes`, `Audits`, `Virtual_List`, `Navigation Menu`, `Preferences`, `Recovered Library*`, `Lesson_Rates`, `Lesson_Out_Requests`) are not needed for profiling.

### `Staff` (39 records)

`PrimaryKey`, `ID_Staff`, `Name_First`, `Name_Last`, `Name_Mid`, `Nickname`, `Role`, `flag_instructor`, `flag_active`, `CreationTimestamp`, `ModificationTimestamp`

### `Families` (13,729)

`PrimaryKey`, `ID_Family`, `OLD_FAMILY_ID`, `Family_Name`, `Primary_Name_First`, `Primary_Name_Last`, `Secondary_Name_First`, `Secondary_Name_Last`, `Preferred_Billing`, `flag_active`, `flag_trashcan`, `CreationTimestamp`, `ModificationTimestamp`

### `Students` (9,367)

`PrimaryKey`, `ID_Students`, `id_family`, `OLD_ID`, `OLD_STUD_ID`, `OLD_FAMILY_ID`, `Name_First`, `Name_Last`, `Name_Mid`, `Name_First_calc`, `Date_of_Birth`, `Age`, `Level`, `Status`, `Status_Recent`, `flag_active`, `flag_trashcan`, `flag_Special_Needs`, `flag_AD`, `flag_has_free_trial`, `flag_owes`, `Payment_Plan`, `Payment_Plan_CC_DD`, `Lesson_Type_1`, `Lesson_Type_2`, `Lesson_Type_3`, `Lesson_Type_4`, `Last_Lesson_Date_Start`, `Last_Lesson_Date_End`, `CreationTimestamp`, `ModificationTimestamp`, `MU_SP_Total`, `MU_PR_Total`, `MU_PM_Total`, `MU_ST_Total`, `MU_GR_Total`, `MU_Unknown_Total`

`Name_First_calc` is `If(flag_Special_Needs; Upper(Name_First); Titlecase(Name_First))`, so the screen shows caps *because of* the flag. What we need is whether the **stored** `Name_First` is also typed in caps, and how often that happens without the flag. Both columns are required.

### `Billing_Months` (492,824)

`PrimaryKey`, `ID_Billing_Months`, `id_student`, `id_family`, `id_billing_year`, `Year`, `Month_Num`, `Month`, `Payment_Plan`, `Payment_Plan_CC_DD`, `Payment_Type_1`, `Payment_Type_2`, `Amount_Paid_1`, `Amount_Paid_2`, `Date_Amt_Received_1`, `Date_Amt_Received_2`, `Monthly_Fee`, `Monthly_Balance`, `Cumulative_Balance`, `Adjustment_Credit`, `Prepay_Discount`, `Rate_LessonType_1`, `Rate_1`, `flag_paid_in_full`, `flag_create`, `flag_new`, `CreationTimestamp`, `ModificationTimestamp`

Largest table; the export takes a few minutes. Half a million rows at ~30 columns is roughly 60 MB.

### `Billing_Years` (33,426)

`PrimaryKey`, `ID_Billing_Years`, `id_student`, `id_family`, `id_current_student`, `Year`, `Cumulative_Total`, `Cumulative_Total_Prev_Year`, `CreationTimestamp`, `ModificationTimestamp`

### `Lesson_Schedules` (126,251)

`PrimaryKey`, `ID_Lesson_Schedule`, `id_student`, `id_family`, `id_staff`, `id_lesson`, `Instructor`, `Instructor_Nickname`, `Lesson_Type`, `Day`, `Time_Start`, `Time_End`, `Date_Start`, `Date_End`, `Pool_Used`, `Status`, `CreationTimestamp`, `ModificationTimestamp`, `Lesson_MU`, `Lesson_MU_to_use`, `Lesson_MU_Amount`, `Adult_Credit`

### `Lesson_Attendance` (334,399)

`PrimaryKey`, `ID_Lesson_Attendance`, `id_student`, `id_staff`, `id_lesson`, `id_lesson_sched`, `Instructor_Name`, `Lesson_Type`, `Date_Attendance`, `Day`, `Time`, `flag_complete`, `flag_ignore`, `flag_Makeup`, `flag_free_trial`, `flag_Special_Needs`, `flag_unpaid`, `CreationTimestamp`, `ModificationTimestamp`

### `Lessons` (983)

`PrimaryKey`, `ID_Lessons`, `id_staff`, `Instructor`, `Instructor_Name_First`, `Instructor_Nickname`, `OLD_INST_ID`, `Type`, `Day`, `Time_Start`, `Time_End`, `Date_Start`, `Date_End`, `Slots_Total`, `Slots_Available`, `Status`, `flag_drop`, `CreationTimestamp`, `ModificationTimestamp`

### `Lesson_Out` (81,386)

`PrimaryKey`, `ID_Lesson_Out`, `id_student`, `id_staff`, `id_lesson`, `id_lesson_sched`, `Instructor`, `Makeup_Type`, `Date_Out`, `flag_do_not_issue`, `flag_missing_stud`, `CreationTimestamp`

### `Waitlist` (10,531)

`PrimaryKey`, `ID_Waitlist`, `id_student`, `id_family`, `id_lesson`, `id_instructor_primary`, `id_instructor_secondary`, `Instructor_primary`, `Instructor_secondary`, `Lesson_Type`, `Status`, `Priority`, `Date_Requested`, `Date_Start`, `Date_Drop`, `Last_Checked`, `flag_active`, `flag_open`, `flag_dropped`, `CreationTimestamp`

### `Billing_Rates` (7) and `Holiday_Dates` (6)

Export **all** fields. Both are tiny and are the rate table and closure calendar in the raw.

## After exporting

**Added 2026-09-10 (ADR-0003):** the six `MU_*_Total` counters on `Students` and the three `Lesson_MU*` fields on `Lesson_Schedules` are exported so the make-up ledger replay can be rehearsed against this export before Foundations: replayed balance (out-lessons issued minus make-ups redeemed, per denomination) versus the stored counter, per student. The profiler does not compute this yet; the import's own reconciliation step does, and the count of students whose replayed and stored balances differ is a Scheduling & search gate input.

```
python scripts/profile_exports.py resources/exports/YYYY-MM-DD > docs/discovery/data-profile-YYYY-MM-DD.md
```

The report holds counts, ranges, and distributions only, plus instructor first names where they collide. It is safe to commit; the exports are not. Paste the report's headline block into the ticket as the resolution.

**Added 2026-09-10 (ADR-0004):** `Lesson_Schedules.Adult_Credit` is the only trace of Adult class-pack balances (hand-typed on the iPad, maintained by nothing). Its non-blank values become opening packs at import; the export lets us count how many adults carry one and what the values look like. *Outcome 2026-09-16:* blank on every row (ADR-0004 addendum).

## What actually arrived (2026-09-13/14)

The export was done differently from the recipe above, and the differences matter for the cutover pull.

- **Method:** one `Maintenance › T##_` layout per table, Show All, **File › Export Records › Excel Workbooks (.xlsx)** with field names as the first row, source *Current Table*, layout formatting off; then converted to CSV as `<Table>_All.csv` (UTF-8 with BOM, embedded newlines quoted — the conversion is lossless, every row has the header's field count). Fifteen tables landed in `resources/application-data/` (gitignored). The session's own account is `BlueBuoy_Export_Session_Findings.md` in the same drop.
- **Every field came, not the lists above:** the card-number columns were removed after export and `Families.Credit_Card_1/2` and `Additional_CC_Notes` were excluded at export, but the card **expiry** columns, every free-text note field, and the working fields (`FoundSetIDs_SMS`, `sum_id_family`, `_kz_*`) are all present. That is why `Students_All.csv` is 645 MB for 9,443 rows. The profiler projects the columns it needs on load and scans the note fields for card-number-shaped digit runs without printing them: one Luhn-valid 13–16 digit run in `Billing_Months.Payment_Notes`, none anywhere else.
- **`.xlsx` truncates at 32,767 characters per cell.** `Families.Notes_General` hit the limit on 38 records and `Students.Notes_General` on 9; the two working fields hit it on every student row. The cutover export must use Merge (`.mer`) or a direct driver for the note fields, never `.xlsx`.
- **Row counts** parsed: Students 9,443 · Families 13,780 · Billing_Months 493,652 · Billing_Years 33,495 · Lesson_Schedules 127,697 · Lesson_Attendance 339,624 · Lesson_Out 82,573 · Waitlist 10,614 · Lessons 975 · Staff 39 · Notes 830 · Audits 5,958 · Documents 15,374 · Billing_Rates 7. Families, Lesson_Schedules and Lesson_Out are 2, 41 and 26 rows short of the counts noted during the export session; the CSVs parse cleanly, so the gap is records that moved between the count and the export or rows the `.xlsx` writer dropped — small enough to ignore for profiling, worth a recount at cutover.
- **Not yet exported:** `Holiday_Dates` (6 rows, no layout of its own) and the **archive** sub-export from `BlueBuoy_FM_2024` (`Families` and `Students`). Both are owed by the residual-exports ticket; the archive one gates the archive decision, and matters more than it looked — 5,654 student ids referenced by the live file's billing rows are absent from the live `Students` table.
- **Report:** [`data-profile-2026-09-14.md`](./data-profile-2026-09-14.md), generated by `python scripts/profile_exports.py resources/application-data "2026-09-13/14 (BlueBuoy_FM, via .xlsx)"`.
