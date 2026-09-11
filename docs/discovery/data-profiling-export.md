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

`PrimaryKey`, `ID_Students`, `id_family`, `OLD_ID`, `OLD_STUD_ID`, `OLD_FAMILY_ID`, `Name_First`, `Name_Last`, `Name_Mid`, `Name_First_calc`, `Date_of_Birth`, `Age`, `Level`, `Status`, `Status_Recent`, `flag_active`, `flag_trashcan`, `flag_Special_Needs`, `flag_AD`, `flag_has_free_trial`, `flag_owes`, `Payment_Plan`, `Payment_Plan_CC_DD`, `Lesson_Type_1`, `Lesson_Type_2`, `Lesson_Type_3`, `Lesson_Type_4`, `Last_Lesson_Date_Start`, `Last_Lesson_Date_End`, `CreationTimestamp`, `ModificationTimestamp`

`Name_First_calc` is `If(flag_Special_Needs; Upper(Name_First); Titlecase(Name_First))`, so the screen shows caps *because of* the flag. What we need is whether the **stored** `Name_First` is also typed in caps, and how often that happens without the flag. Both columns are required.

### `Billing_Months` (492,824)

`PrimaryKey`, `ID_Billing_Months`, `id_student`, `id_family`, `id_billing_year`, `Year`, `Month_Num`, `Month`, `Payment_Plan`, `Payment_Plan_CC_DD`, `Payment_Type_1`, `Payment_Type_2`, `Amount_Paid_1`, `Amount_Paid_2`, `Date_Amt_Received_1`, `Date_Amt_Received_2`, `Monthly_Fee`, `Monthly_Balance`, `Cumulative_Balance`, `Adjustment_Credit`, `Prepay_Discount`, `Rate_LessonType_1`, `Rate_1`, `flag_paid_in_full`, `flag_create`, `flag_new`, `CreationTimestamp`, `ModificationTimestamp`

Largest table; the export takes a few minutes. Half a million rows at ~30 columns is roughly 60 MB.

### `Billing_Years` (33,426)

`PrimaryKey`, `ID_Billing_Years`, `id_student`, `id_family`, `id_current_student`, `Year`, `Cumulative_Total`, `Cumulative_Total_Prev_Year`, `CreationTimestamp`, `ModificationTimestamp`

### `Lesson_Schedules` (126,251)

`PrimaryKey`, `ID_Lesson_Schedule`, `id_student`, `id_family`, `id_staff`, `id_lesson`, `Instructor`, `Instructor_Nickname`, `Lesson_Type`, `Day`, `Time_Start`, `Time_End`, `Date_Start`, `Date_End`, `Pool_Used`, `Status`, `CreationTimestamp`, `ModificationTimestamp`

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

```
python scripts/profile_exports.py resources/exports/YYYY-MM-DD > docs/discovery/data-profile-YYYY-MM-DD.md
```

The report holds counts, ranges, and distributions only, plus instructor first names where they collide. It is safe to commit; the exports are not. Paste the report's headline block into the ticket as the resolution.
