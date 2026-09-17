
# Data profile of live FileMaker export: 2026-09-13/14 (BlueBuoy_FM, via .xlsx)

Generated 2026-09-16 by `scripts/profile_exports.py`. Aggregates only; source files are not committed.
Sections: row counts, date ranges, active vs historical, instructor collisions, dual keys and orphans, ALL-CAPS names, unknown values, payment volume, pre-2020 billing rows, placeholder rows, the make-up ledger replay (FileMaker's formula and the ADR-0003 rule), and a free-text scan for card-number-shaped digit runs and truncated cells. Paste the numbers the ticket asks for into its resolution.

## Row counts

| Table | Rows | flag_active = 1 | flag_trashcan = 1 |
| --- | --- | --- | --- |
| Staff | 39 | 17 | n/a |
| Families | 13780 | 856 | 0 |
| Students | 9443 | 1163 | 0 |
| Billing_Months | 493652 | n/a | n/a |
| Billing_Years | 33495 | n/a | n/a |
| Lesson_Schedules | 127697 | n/a | n/a |
| Lesson_Attendance | 339624 | n/a | n/a |
| Lessons | 975 | n/a | n/a |
| Lesson_Out | 82573 | n/a | n/a |
| Waitlist | 10614 | 517 | n/a |
| Billing_Rates | 7 | n/a | n/a |
| Holiday_Dates | file missing |  |  |


## Date ranges

| Table | Column | Earliest | Latest | Blank / unparsed |
| --- | --- | --- | --- | --- |
| Staff | CreationTimestamp | 2020-05-29 | 2026-05-04 | 0 |
| Families | CreationTimestamp | 2020-08-29 | 2026-09-11 | 0 |
| Students | CreationTimestamp | 1999-06-25 | 2026-09-11 | 0 |
| Billing_Months | CreationTimestamp | 2020-12-15 | 2026-09-14 | 0 |
| Billing_Years | CreationTimestamp | 2021-08-16 | 2026-09-14 | 0 |
| Lesson_Schedules | CreationTimestamp | 2020-08-29 | 2026-09-12 | 0 |
| Lesson_Attendance | CreationTimestamp | 2020-08-31 | 2026-09-12 | 0 |
| Lessons | CreationTimestamp | 2020-08-29 | 2026-08-29 | 0 |
| Lesson_Out | CreationTimestamp | 2020-08-31 | 2026-09-12 | 0 |
| Waitlist | CreationTimestamp | 2020-08-29 | 2026-09-12 | 0 |
| Billing_Rates | CreationTimestamp | 2020-12-08 | 2025-11-20 | 0 |
| Lesson_Attendance | Date_Attendance | 2020-08-31 | 2026-09-12 | 0 |
| Lesson_Schedules | Date_Start | 0202-04-23 | 2026-11-11 | 125 |
| Lesson_Schedules | Date_End | 0202-09-01 | 2026-12-31 | 132 |
| Lesson_Out | Date_Out | 2020-08-07 | 2026-11-30 | 9 |
| Billing_Months | Date_Amt_Received_1 | 2002-02-20 | 2030-06-29 | 426082 |
| Students | Last_Lesson_Date_End | 2018-12-31 | 2026-12-31 | 296 |
| Waitlist | Date_Requested | 1998-01-01 | 2051-08-25 | 1063 |
| Students | Date_of_Birth | 1942-10-03 | 2049-06-29 | 34 |


### Lesson_Attendance.Date_Attendance rows per year

| Year | Rows |
| --- | --- |
| 2020 | 7218 |
| 2021 | 40584 |
| 2022 | 54369 |
| 2023 | 56854 |
| 2024 | 64475 |
| 2025 | 65846 |
| 2026 | 50278 |


### Students.CreationTimestamp rows per year

| Year | Rows |
| --- | --- |
| 1999 | 1 |
| 2001 | 1 |
| 2009 | 1 |
| 2010 | 6 |
| 2011 | 25 |
| 2012 | 27 |
| 2013 | 60 |
| 2014 | 81 |
| 2015 | 143 |
| 2016 | 216 |
| 2017 | 322 |
| 2018 | 712 |
| 2019 | 1348 |
| 2020 | 444 |
| 2021 | 954 |
| 2022 | 1194 |
| 2023 | 1166 |
| 2024 | 1030 |
| 2025 | 950 |
| 2026 | 762 |


### Families.CreationTimestamp rows per year

| Year | Rows |
| --- | --- |
| 2020 | 9267 |
| 2021 | 770 |
| 2022 | 1008 |
| 2023 | 845 |
| 2024 | 736 |
| 2025 | 641 |
| 2026 | 513 |


### Lesson_Schedules.Date_Start rows per year

| Year | Rows |
| --- | --- |
| 202 | 1 |
| 2002 | 3 |
| 2008 | 12 |
| 2009 | 136 |
| 2010 | 7 |
| 2011 | 42 |
| 2012 | 46 |
| 2013 | 77 |
| 2014 | 41 |
| 2015 | 72 |
| 2016 | 152 |
| 2017 | 187 |
| 2018 | 1099 |
| 2019 | 19507 |
| 2020 | 8517 |
| 2021 | 11793 |
| 2022 | 16502 |
| 2023 | 17904 |
| 2024 | 18321 |
| 2025 | 18486 |
| 2026 | 14667 |


### Billing_Months rows per Year

| Year | Rows |
| --- | --- |
| 2016 | 12 |
| 2017 | 36 |
| 2018 | 60 |
| 2019 | 156 |
| 2020 | 10764 |
| 2021 | 97220 |
| 2022 | 107592 |
| 2023 | 109176 |
| 2024 | 85116 |
| 2025 | 46068 |
| 2026 | 37368 |
| 2027 | 84 |


## Genuinely active vs historical

| Measure | Count |
| --- | --- |
| Students with flag_active = 1 and not trashed | 1163 |
| Students whose Last_Lesson_Date_End is within 90 days (since 2026-06-18) | 1660 |
| Students with at least one Lesson_Schedules row with Status = Open | 1089 |
| Students in all three sets | 1088 |
| Students flagged active but with no open schedule | 75 |
| Families with flag_active = 1 and not trashed | 856 |
| Families with at least one flag_active student | 856 |
| Families with at least one student in an Open schedule | 811 |


### Students.Status distribution

| Status | Rows |
| --- | --- |
| (blank) | 7853 |
| Closed | 1242 |
| Open | 313 |
| Future | 35 |


## Instructor first-name collisions

| Measure | Count |
| --- | --- |
| Staff rows | 39 |
| Staff with flag_instructor = 1 | 35 |
| Distinct first names (case-insensitive) | 35 |
| First names shared by more than one staff row | 3 |
| Staff rows involved in a collision | 6 |
| Collisions where more than one is flag_active | 0 |


### Colliding first names

| First name | Staff rows | Active | Instructors |
| --- | --- | --- | --- |
| Chloe | 2 | 1 | 2 |
| Emma | 2 | 0 | 2 |
| Pricilla | 2 | 0 | 2 |


### Lesson_Schedules.Instructor resolved against Staff

| Outcome | Rows |
| --- | --- |
| id_staff blank | 2224 |
| id_staff disagrees with name | 6099 |
| id_staff not in Staff | 52 |
| name blank | 59 |
| name matches exactly one staff row | 113856 |
| name matches more than one staff row (ambiguous) | 5485 |
| name matches no staff row | 8297 |


### Lesson_Attendance.Instructor_Name resolved against Staff

| Outcome | Rows |
| --- | --- |
| id_staff blank | 1 |
| id_staff disagrees with name | 20757 |
| id_staff not in Staff | 6 |
| name blank | 7 |
| name matches exactly one staff row | 306235 |
| name matches more than one staff row (ambiguous) | 12625 |
| name matches no staff row | 20757 |


### Lessons.Instructor resolved against Staff

| Outcome | Rows |
| --- | --- |
| id_staff blank | 3 |
| id_staff disagrees with name | 64 |
| name blank | 3 |
| name matches exactly one staff row | 896 |
| name matches more than one staff row (ambiguous) | 12 |
| name matches no staff row | 64 |


### Lesson_Out.Instructor resolved against Staff

| Outcome | Rows |
| --- | --- |
| id_staff blank | 10 |
| id_staff disagrees with name | 5044 |
| id_staff not in Staff | 5 |
| name blank | 10 |
| name matches exactly one staff row | 73827 |
| name matches more than one staff row (ambiguous) | 3692 |
| name matches no staff row | 5044 |


## Dual-key disagreements (id_student vs id_family)


### Billing_Months

| Outcome | Rows |
| --- | --- |
| agree | 277641 |
| id_family blank | 1333 |
| id_family not in Families (orphan) | 12 |
| id_student not in Students (orphan) | 214642 |
| student's family differs from row's id_family | 36 |

Orphan id_student values: 5654 distinct; 1444 orphan rows carry a payment, 25 carry a Monthly_Fee.

| Year (orphan rows) | Rows |
| --- | --- |
| 2017 | 12 |
| 2018 | 12 |
| 2019 | 24 |
| 2020 | 6776 |
| 2021 | 59210 |
| 2022 | 61236 |
| 2023 | 60408 |
| 2024 | 16512 |
| 2025 | 10572 |
| 2026 | 60 |

Disagreements by year (Year column, else creation year):

| Year | Rows |
| --- | --- |
| 2021 | 12 |
| 2023 | 12 |
| 2025 | 12 |


### Billing_Years

| Outcome | Rows |
| --- | --- |
| agree | 21010 |
| id_family blank | 3 |
| id_family not in Families (orphan) | 1 |
| id_student not in Students (orphan) | 12478 |
| student's family differs from row's id_family | 4 |

Orphan id_student values: 5639 distinct; 0 orphan rows carry a payment, 0 carry a Monthly_Fee.

| Year (orphan rows) | Rows |
| --- | --- |
| 2016 | 1 |
| 2017 | 1 |
| 2018 | 2 |
| 2019 | 2 |
| 2020 | 4 |
| 2021 | 79 |
| 2022 | 5102 |
| 2023 | 5032 |
| 2024 | 1375 |
| 2025 | 879 |
| 2026 | 4 |

Disagreements by year (Year column, else creation year):

| Year | Rows |
| --- | --- |
| 2021 | 1 |
| 2023 | 1 |
| 2024 | 1 |
| 2025 | 1 |


### Lesson_Schedules

| Outcome | Rows |
| --- | --- |
| agree | 113076 |
| both blank | 9734 |
| id_family blank | 4887 |

Orphan id_student values: 588 distinct; 0 orphan rows carry a payment, 0 carry a Monthly_Fee.

| Year (orphan rows) | Rows |
| --- | --- |
| ? | 4887 |


### Waitlist

| Outcome | Rows |
| --- | --- |
| agree | 9095 |
| both blank | 837 |
| id_family blank | 2 |
| id_student not in Students (orphan) | 679 |
| student's family differs from row's id_family | 1 |

Orphan id_student values: 619 distinct; 0 orphan rows carry a payment, 0 carry a Monthly_Fee.

| Year (orphan rows) | Rows |
| --- | --- |
| ? | 680 |

Disagreements by year (Year column, else creation year):

| Year | Rows |
| --- | --- |
| 2021 | 1 |


### Students

| Outcome | Rows |
| --- | --- |
| id_family blank | 17 |
| id_family not in Families (orphan) | 0 |


## ALL-CAPS names vs flag_Special_Needs

| Combination | Students |
| --- | --- |
| Stored Name_First ALL CAPS, flag_Special_Needs = 1 | 13 |
| Stored Name_First ALL CAPS, flag_Special_Needs = 0 | 49 |
| Stored Name_First not caps, flag_Special_Needs = 1 | 337 |
| Stored Name_First not caps, flag_Special_Needs = 0 | 9044 |

Stored Name_Last ALL CAPS: 52
Families.Family_Name ALL CAPS: 158
Families.Primary_Name_First ALL CAPS (the hand-typed 'handle with care' convention): 138 of 13441 populated
Families.Secondary_Name_First ALL CAPS (the hand-typed 'handle with care' convention): 113 of 10464 populated
Students.Primary_Name_First ALL CAPS (the hand-typed 'handle with care' convention): 55 of 9389 populated

Reading: the on-screen caps come from `Name_First_calc`, which upper-cases *because of* the flag. Rows on the second line are the ones where caps carry meaning the flag does not, and are what the decode pass must catch.

## Unknown values (do not default these)

| Measure | Rows |
| --- | --- |
| Students.Level blank | 1863 |
| Students.Age blank | 33 |
| Students.Date_of_Birth blank | 33 |
| Students.Payment_Plan blank | 6325 |
| Students.Status blank | 7853 |
| Students.id_family blank | 17 |
| Students.Lesson_Type_1 blank | 8134 |
| Students.OLD_ID populated (prior migration) | 0 |
| Students.OLD_STUD_ID populated (prior migration) | 3349 |
| Students.OLD_FAMILY_ID populated (prior migration) | 3348 |
| Families.OLD_FAMILY_ID populated | 9228 |


## Payment volume (last 24 months)


### Payment_Type values seen (Payment_Type_1 + Payment_Type_2, last 24 months)

| Payment_Type | Payments |
| --- | --- |
| Auto CC | 19096 |
| Credit Card | 3221 |
| Direct Dpst. | 1079 |
| Check | 785 |
| Referral Credit | 313 |
| Xfer Credit | 188 |
| BB Credit | 53 |
| (blank) | 22 |
| GC Online | 15 |
| Cash | 12 |
| Reversal | 4 |
| Refund | 3 |
| xXfer Credit | 2 |
| Gift Cert. | 2 |
| TRADE | 1 |
| xfXfer Credit | 1 |


### Payment_Plan_CC_DD on Billing_Months rows (last 24 months)

| Plan | Rows |
| --- | --- |
| CC | 22025 |
| DD | 189 |


### Per month

| Month | Rows | Fee > 0 | Rows paid | Payments | Dollars paid | plan:CC | plan:DD | Auto CC | Credit Card | Direct Dpst. | Check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2024-09 | 7093 | 1094 | 942 | 981 | 191,159 | 1031 | 13 | 781 | 150 | 28 | 4 |
| 2024-10 | 7093 | 1093 | 931 | 967 | 178,032 | 1091 | 13 | 783 | 112 | 34 | 9 |
| 2024-11 | 7093 | 1036 | 879 | 904 | 178,378 | 1132 | 14 | 775 | 66 | 33 | 11 |
| 2024-12 | 7093 | 960 | 863 | 920 | 257,236 | 1196 | 14 | 720 | 143 | 31 | 13 |
| 2025-01 | 3839 | 954 | 789 | 820 | 154,008 | 692 | 7 | 640 | 116 | 34 | 12 |
| 2025-02 | 3839 | 992 | 830 | 866 | 171,204 | 728 | 7 | 682 | 95 | 45 | 17 |
| 2025-03 | 3839 | 1037 | 859 | 879 | 171,036 | 759 | 7 | 672 | 107 | 63 | 18 |
| 2025-04 | 3839 | 1097 | 913 | 935 | 177,754 | 773 | 8 | 715 | 109 | 72 | 26 |
| 2025-05 | 3839 | 1177 | 1015 | 1049 | 217,997 | 777 | 8 | 762 | 174 | 64 | 31 |
| 2025-06 | 3839 | 1248 | 1092 | 1147 | 222,005 | 798 | 8 | 814 | 249 | 19 | 32 |
| 2025-07 | 3839 | 1245 | 1083 | 1132 | 225,892 | 813 | 8 | 890 | 171 | 16 | 20 |
| 2025-08 | 3839 | 1203 | 1032 | 1088 | 205,636 | 802 | 8 | 896 | 104 | 22 | 26 |
| 2025-09 | 3839 | 1120 | 1004 | 1084 | 216,059 | 840 | 9 | 801 | 147 | 48 | 31 |
| 2025-10 | 3839 | 1108 | 974 | 1004 | 203,424 | 826 | 9 | 780 | 106 | 53 | 40 |
| 2025-11 | 3839 | 1040 | 905 | 926 | 206,116 | 809 | 10 | 742 | 71 | 58 | 37 |
| 2025-12 | 3839 | 998 | 899 | 949 | 278,206 | 802 | 10 | 685 | 153 | 52 | 40 |
| 2026-01 | 3114 | 1007 | 845 | 891 | 176,639 | 916 | 4 | 676 | 97 | 51 | 56 |
| 2026-02 | 3114 | 1037 | 881 | 922 | 187,232 | 931 | 4 | 694 | 86 | 65 | 60 |
| 2026-03 | 3114 | 1105 | 944 | 996 | 200,095 | 944 | 4 | 709 | 137 | 77 | 52 |
| 2026-04 | 3114 | 1176 | 998 | 1035 | 213,477 | 925 | 4 | 764 | 111 | 88 | 49 |
| 2026-05 | 3114 | 1202 | 1054 | 1100 | 237,314 | 925 | 4 | 788 | 153 | 80 | 51 |
| 2026-06 | 3114 | 1212 | 1056 | 1093 | 222,103 | 910 | 4 | 807 | 203 | 13 | 41 |
| 2026-07 | 3114 | 1192 | 1042 | 1105 | 233,649 | 886 | 4 | 881 | 123 | 12 | 40 |
| 2026-08 | 3114 | 1191 | 1017 | 1067 | 215,771 | 864 | 4 | 854 | 134 | 17 | 38 |
| 2026-09 | 3114 | 1112 | 916 | 937 | 211,093 | 855 | 4 | 785 | 104 | 4 | 31 |

Card volume per month = payments whose Payment_Type is the card value (see the type columns), or rows on a CC plan. Compare with staff's reported 550-700.

## Pre-2020 Billing_Months: are amounts stamped on the row?

| Year band | rows | Monthly_Fee populated | Rate_1 populated | Amount_Paid_1 populated | Cumulative_Balance populated |
| --- | --- | --- | --- | --- | --- |
| < 2020 | 264 | 0 | 0 | 0 | 264 |
| >= 2020 | 493388 | 68576 | 52547 | 70896 | 493388 |

Billing_Rates has rows for 2020-2026 only; rows before 2020 must carry their own amounts or the history is unpriced.

## Placeholder and pseudo rows (every real search excludes these)

| Measure | Rows |
| --- | --- |
| Lesson_Schedules with ID_Lesson_Schedule = DUMMY | 46 |
| Lesson_Schedules with flag_dummy = 1 | 46 |
| Lesson_Schedules whose Student text starts with 'Inst' | 0 |
| Lesson_Schedules with flag_hold = 1 | 42680 |
| Lesson_Schedules with flag_break = 1 | 9582 |
| Students with Name_First = Inst | 0 |
| Lessons whose Student text starts with 'Inst' | 0 |
| Lessons with flag_has_break = 1 | 105 |


## Make-up ledger replay vs stored counters (ADR-0003 rehearsal)


### Lesson_Out.Makeup_Type (upper-cased)

| Denomination | Rows |
| --- | --- |
| SP | 55345 |
| PR | 13489 |
| PM | 10008 |
| GR | 2600 |
| ST | 905 |
| AD | 207 |
| (blank) | 19 |


### Lesson_Schedules.Lesson_MU_to_use (upper-cased) and Lesson_MU_Amount

| Denomination | Rows |
| --- | --- |
| SP | 34311 |
| PR | 6412 |
| PM | 4391 |
| GR | 2221 |
| ST | 786 |
| UNKNOWN | 5 |
| BRK | 1 |
| SP MU | 1 |
| - | 1 |
| P | 1 |

| Amount | Rows |
| --- | --- |
| 0.25 | 2 |
| 0.5 | 137 |
| 1.0 | 46062 |
| 2.0 | 1674 |
| 4.0 | 255 |

Amounts other than 1 are the conversions: 2 SP for a PR lesson, 4 group for a PR, 0.5 PR for an SP lesson.


### Replay 1 — FileMaker's stored formula (flagged out rows minus flagged schedule rows)

| Denomination | Students with activity | Stored = formula | Stored > formula | Stored < formula | Match rate |
| --- | --- | --- | --- | --- | --- |
| SP | 3551 | 860 | 1816 | 875 | 24% |
| PR | 980 | 299 | 389 | 292 | 31% |
| PM | 1025 | 251 | 317 | 457 | 24% |
| GR | 426 | 61 | 286 | 79 | 14% |
| ST | 151 | 21 | 102 | 28 | 14% |

A miss here is a counter FileMaker never re-evaluated (or a script that wrote it directly): the stored value is stale, not the ledger. This is the list the Scheduling & search gate classifies.


### Replay 2 — the ADR-0003 business rule (do-not-issue excluded, conversion amounts honoured)

| Denomination | Students with stored counter != 0 | Stored = issued - redeemed | Stored = issued only | Neither | of which stored > balance | of which stored < balance |
| --- | --- | --- | --- | --- | --- | --- |
| SP | 2853 | 6914 | 180 | 2349 | 1874 | 475 |
| PR | 757 | 8792 | 100 | 551 | 324 | 227 |
| PM | 722 | 8811 | 91 | 541 | 328 | 213 |
| GR | 280 | 9093 | 106 | 244 | 193 | 51 |
| ST | 96 | 9321 | 44 | 78 | 65 | 13 |

Same comparison restricted to students with any activity in that denomination (stored != 0, or an issue, or a redemption):

| Denomination | Students with activity | Replay matches stored | Differs | Match rate |
| --- | --- | --- | --- | --- |
| SP | 3857 | 1328 | 2529 | 34% |
| PR | 1101 | 450 | 651 | 41% |
| PM | 1084 | 452 | 632 | 42% |
| GR | 450 | 100 | 350 | 22% |
| ST | 157 | 35 | 122 | 22% |

Lesson_Out rows of type AD (adults issue no credit per ADR-0003): {'counted': 20, 'not counted': 187}

| Measure | Students |
| --- | --- |
| MU_Unknown_Total != 0 | 651 |
| OLD_MU_REMAINING populated (balance carried from the previous migration) | 0 |
| Any stored MU_*_Total negative | 14 |
| Students with at least one counted Lesson_Out row | 4537 |
| Students with at least one redemption row | 9451 |

Reading: 'Stored = issued - redeemed' means the six counters are balances the ledger can replay; 'Stored = issued only' means they count issues and redemptions live elsewhere; 'Neither' is the reconciliation list the import must produce per student. This is the rehearsal, not the import's rule.

### Lesson_Schedules.Adult_Credit (ADR-0004 opening packs)

| Measure | Rows |
| --- | --- |
| Rows with a non-blank Adult_Credit | 0 |
| Distinct values | 0 |


## Free-text scan: card-number-shaped digit runs and truncated cells

Counts only. A 'digit run' is 13-16 digits with optional spaces or dashes; Luhn-valid runs are the ones that look like real card numbers. Truncated = cell length exactly 32,767, the .xlsx limit.

| Table | Columns scanned | Populated cells | Digit runs | Luhn-valid | Rows with a run | Truncated cells |
| --- | --- | --- | --- | --- | --- | --- |
| Families | Notes_General, Referral_Notes, Credit_Card_1_Exp_Date, Credit_Card_2_Exp_Date | 15288 | 2 | 0 | 2 | 38 |
| Students | Notes_General, Instructor_Notes, Notes_Attendance, Notes_Deck_Manager, Notes_MU, Referral_Notes, FoundSetIDs_SMS, sum_id_family | 28144 | 0 | 0 | 0 | 18895 |
| Billing_Months | Payment_Notes | 20454 | 7 | 1 | 7 | 0 |
| Billing_Years | Notes | 106 | 0 | 0 | 0 | 0 |
| Lesson_Attendance | Intructor_Notes_to_Office | 2981 | 0 | 0 | 0 | 0 |
| Lesson_Out | Notes | 32053 | 0 | 0 | 0 | 0 |
| Lesson_Schedules | Student_Notes, import_Pool_Notes | 208 | 0 | 0 | 0 | 0 |
| Waitlist | Notes, Time_Notes | 17652 | 0 | 0 | 0 | 0 |
| Notes | Note | 818 | 0 | 0 | 0 | 0 |
| Audits | Log | 5958 | 4 | 0 | 1 | 0 |
| Staff | Notes | 16 | 0 | 0 | 0 | 0 |


## Missing files or columns (facts skipped)

| Table | Column |
| --- | --- |
| Holiday_Dates | *file* |

