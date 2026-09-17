#!/usr/bin/env python3
"""Profile live FileMaker exports into the facts the DDR cannot yield.

Usage:  python scripts/profile_exports.py <export folder> [label] > docs/discovery/data-profile-YYYY-MM-DD.md

Files may be named <Table>.csv or <Table>_All.csv (the 2026-09-14 live export used the latter).

Reads the Merge/CSV files listed in docs/discovery/data-profiling-export.md
(one file per table, header row = FileMaker field names) and prints a Markdown
report of aggregates only: counts, date ranges, distributions. No student or
family names are printed; instructor first names appear only where they collide.

Standard library only. A missing table or column skips that fact and says so.
"""
import csv
import glob
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

TODAY = date.today()
MISSING = []  # (table, column) pairs we could not find


# ---------- loading ----------

def find_file(folder, table):
    for cand in glob.glob(os.path.join(folder, "*")):
        base, ext = os.path.splitext(os.path.basename(cand))
        if base.lower() in (table.lower(), table.lower() + "_all") and ext.lower() in (".csv", ".mer", ".tab", ".txt"):
            return cand
    return None


# Columns kept per table when loading. None = keep everything (small tables).
# The live export carries every field (Students alone has 285, three of them
# 32 KB free text), so projecting on load keeps the big tables in memory.
KEEP = {
    "Staff": None,
    "Billing_Rates": None,
    "Holiday_Dates": None,
    "Families": {"PrimaryKey", "ID_Family", "OLD_FAMILY_ID", "Family_Name", "Primary_Name_First",
                 "Primary_Name_Last", "Secondary_Name_First", "Secondary_Name_Last", "Preferred_Billing",
                 "Primary_Relation", "Secondary_Relation", "flag_active", "flag_trashcan",
                 "CreationTimestamp", "ModificationTimestamp"},
    "Students": {"PrimaryKey", "ID_Students", "id_family", "OLD_ID", "OLD_STUD_ID", "OLD_FAMILY_ID",
                 "Name_First", "Name_Last", "Name_Mid", "Name_First_calc", "Primary_Name_First",
                 "Secondary_Name_First", "Date_of_Birth", "Age", "Level", "Status", "Status_Recent",
                 "flag_active", "flag_trashcan", "flag_Special_Needs", "flag_AD", "flag_has_free_trial",
                 "flag_owes", "Payment_Plan", "Payment_Plan_CC_DD", "Lesson_Type_1", "Lesson_Type_2",
                 "Lesson_Type_3", "Lesson_Type_4", "Last_Lesson_Date_Start", "Last_Lesson_Date_End",
                 "CreationTimestamp", "ModificationTimestamp", "MU_SP_Total", "MU_PR_Total", "MU_PM_Total",
                 "MU_ST_Total", "MU_GR_Total", "MU_Unknown_Total", "Makeups_Left", "OLD_MU_REMAINING",
                 "OLD_MU_PREV_YEAR"},
    "Billing_Months": {"PrimaryKey", "ID_Billing_Months", "id_student", "id_family", "id_billing_year", "Year",
                       "Month_Num", "Month", "Payment_Plan", "Payment_Plan_CC_DD", "Payment_Type_1",
                       "Payment_Type_2", "Amount_Paid_1", "Amount_Paid_2", "Date_Amt_Received_1",
                       "Date_Amt_Received_2", "Monthly_Fee", "Monthly_Balance", "Cumulative_Balance",
                       "Adjustment_Credit", "Prepay_Discount", "Rate_LessonType_1", "Rate_1",
                       "flag_paid_in_full", "flag_create", "flag_new", "CreationTimestamp", "ModificationTimestamp"},
    "Billing_Years": {"PrimaryKey", "ID_Billing_Years", "id_student", "id_family", "id_current_student", "Year",
                      "Cumulative_Total", "Cumulative_Total_Prev_Year", "CreationTimestamp", "ModificationTimestamp"},
    "Lesson_Schedules": {"PrimaryKey", "ID_Lesson_Schedule", "id_student", "id_family", "id_staff", "id_lesson",
                         "Instructor", "Instructor_Nickname", "Lesson_Type", "Day", "Time_Start", "Time_End",
                         "Date_Start", "Date_End", "Pool_Used", "Status", "CreationTimestamp",
                         "ModificationTimestamp", "Lesson_MU", "Lesson_MU_to_use", "Lesson_MU_Amount",
                         "flag_MU_Count", "Adult_Credit", "flag_dummy", "flag_hold", "flag_break", "Student",
                         "flag_MU_SP", "flag_MU_PR", "flag_MU_PM", "flag_MU_GR", "flag_MU_ST", "flag_MU_AD"},
    "Lesson_Attendance": {"PrimaryKey", "ID_Lesson_Attendance", "id_student", "id_staff", "id_lesson",
                          "id_lesson_sched", "Instructor_Name", "Lesson_Type", "Date_Attendance", "Day", "Time",
                          "flag_complete", "flag_ignore", "flag_Makeup", "flag_free_trial", "flag_Special_Needs",
                          "flag_unpaid", "CreationTimestamp", "ModificationTimestamp"},
    "Lessons": {"PrimaryKey", "ID_Lessons", "id_staff", "Instructor", "Instructor_Name_First", "Instructor_Nickname",
                "OLD_INST_ID", "Type", "Day", "Time_Start", "Time_End", "Date_Start", "Date_End", "Slots_Total",
                "Slots_Available", "Status", "flag_drop", "flag_has_break", "CreationTimestamp",
                "ModificationTimestamp", "Student"},
    "Lesson_Out": {"PrimaryKey", "ID_Lesson_Out", "id_student", "id_staff", "id_lesson", "id_lesson_sched",
                   "Instructor", "Makeup_Type", "Date_Out", "flag_do_not_issue", "flag_count", "flag_missing_stud",
                   "CreationTimestamp", "flag_MU_SP", "flag_MU_PR", "flag_MU_PM", "flag_MU_GR", "flag_MU_ST"},
    "Waitlist": {"PrimaryKey", "ID_Waitlist", "id_student", "id_family", "id_lesson", "id_instructor_primary",
                 "id_instructor_secondary", "Instructor_primary", "Instructor_secondary", "Lesson_Type", "Status",
                 "Priority", "Date_Requested", "Date_Start", "Date_Drop", "Last_Checked", "flag_active", "flag_open",
                 "flag_dropped", "CreationTimestamp"},
}


def load(folder, table):
    """Return list[dict] or None when the file is absent."""
    path = find_file(folder, table)
    if not path:
        MISSING.append((table, "*file*"))
        return None
    for enc in ("utf-8-sig", "cp1252", "mac_roman"):
        try:
            with open(path, newline="", encoding=enc) as fh:
                sample = fh.read(65536)
                fh.seek(0)
                delim = "\t" if sample.count("\t") > sample.count(",") else ","
                reader = csv.DictReader(fh, delimiter=delim)
                keep = KEEP.get(table)
                rows = []
                for r in reader:
                    # FileMaker exports embedded returns as \v; normalise.
                    rows.append({(k or "").strip(): (v or "").replace("\x0b", "\n").strip()
                                 for k, v in r.items() if keep is None or (k or "").strip() in keep})
                return rows
        except UnicodeDecodeError:
            continue
    sys.stderr.write(f"could not decode {path}\n")
    return None


def col(rows, table, name):
    """True if column exists; otherwise record and return False."""
    if rows and name in rows[0]:
        return True
    MISSING.append((table, name))
    return False


# ---------- parsing ----------

_DATE_FORMATS = ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y", "%d.%m.%Y")
_TS_FORMATS = ("%m/%d/%Y %I:%M:%S %p", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S",
               "%m/%d/%Y %I:%M %p", "%m/%d/%Y %H:%M", "%Y-%m-%dT%H:%M:%S")


def to_date(s):
    s = (s or "").strip()
    if not s:
        return None
    head = s.split(" ")[0]
    for f in _TS_FORMATS:
        try:
            return datetime.strptime(s, f).date()
        except ValueError:
            pass
    for f in _DATE_FORMATS:
        try:
            return datetime.strptime(head, f).date()
        except ValueError:
            pass
    return None


def to_num(s):
    s = (s or "").strip().replace(",", "").replace("$", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def truthy(s):
    return (s or "").strip() not in ("", "0", "0.0", "No", "no", "false", "False")


def is_all_caps(s):
    s = (s or "").strip()
    letters = [c for c in s if c.isalpha()]
    return len(letters) >= 2 and all(c.isupper() for c in letters)


# ---------- output helpers ----------

OUT = []


def h(level, text):
    OUT.append("")
    OUT.append("#" * level + " " + text)
    OUT.append("")


def line(text=""):
    OUT.append(text)


def table(headers, rows):
    OUT.append("| " + " | ".join(headers) + " |")
    OUT.append("|" + "|".join(" --- " for _ in headers) + "|")
    for r in rows:
        OUT.append("| " + " | ".join(str(x) for x in r) + " |")
    OUT.append("")


def date_range(rows, table_name, column):
    if not rows or not col(rows, table_name, column):
        return None, None, 0
    ds = [d for d in (to_date(r[column]) for r in rows) if d]
    if not ds:
        return None, None, 0
    return min(ds), max(ds), len(rows) - len(ds)


def per_year(rows, column):
    c = Counter()
    for r in rows:
        d = to_date(r.get(column, ""))
        if d:
            c[d.year] += 1
    return c


# ---------- sections ----------

def section_counts(data):
    h(2, "Row counts")
    rows = []
    for name, rs in data.items():
        if rs is None:
            rows.append((name, "file missing", "", ""))
            continue
        trash = sum(1 for r in rs if truthy(r.get("flag_trashcan", ""))) if rs and "flag_trashcan" in rs[0] else "n/a"
        active = sum(1 for r in rs if truthy(r.get("flag_active", ""))) if rs and "flag_active" in rs[0] else "n/a"
        rows.append((name, len(rs), active, trash))
    table(["Table", "Rows", "flag_active = 1", "flag_trashcan = 1"], rows)


def section_date_ranges(data):
    h(2, "Date ranges")
    rows = []
    for name, rs in data.items():
        if not rs:
            continue
        lo, hi, blank = date_range(rs, name, "CreationTimestamp")
        if lo:
            rows.append((name, "CreationTimestamp", lo, hi, blank))
    for name, column in (("Lesson_Attendance", "Date_Attendance"), ("Lesson_Schedules", "Date_Start"),
                         ("Lesson_Schedules", "Date_End"), ("Lesson_Out", "Date_Out"),
                         ("Billing_Months", "Date_Amt_Received_1"), ("Students", "Last_Lesson_Date_End"),
                         ("Waitlist", "Date_Requested"), ("Students", "Date_of_Birth")):
        rs = data.get(name)
        if not rs:
            continue
        lo, hi, blank = date_range(rs, name, column)
        if lo:
            rows.append((name, column, lo, hi, blank))
    table(["Table", "Column", "Earliest", "Latest", "Blank / unparsed"], rows)

    for name, column in (("Lesson_Attendance", "Date_Attendance"), ("Students", "CreationTimestamp"),
                         ("Families", "CreationTimestamp"), ("Lesson_Schedules", "Date_Start")):
        rs = data.get(name)
        if rs and column in rs[0]:
            c = per_year(rs, column)
            h(3, f"{name}.{column} rows per year")
            table(["Year", "Rows"], sorted(c.items()))

    bm = data.get("Billing_Months")
    if bm and "Year" in bm[0]:
        c = Counter(r["Year"] for r in bm)
        h(3, "Billing_Months rows per Year")
        table(["Year", "Rows"], sorted(c.items()))


def section_activity(data):
    h(2, "Genuinely active vs historical")
    st = data.get("Students")
    fam = data.get("Families")
    ls = data.get("Lesson_Schedules")
    if not st:
        line("Students export missing.")
        return
    recent = date.fromordinal(TODAY.toordinal() - 90)
    active_flag = {r.get("ID_Students") for r in st
                   if truthy(r.get("flag_active", "")) and not truthy(r.get("flag_trashcan", ""))}
    recent_lesson = set()
    if col(st, "Students", "Last_Lesson_Date_End"):
        for r in st:
            d = to_date(r["Last_Lesson_Date_End"])
            if d and d >= recent:
                recent_lesson.add(r.get("ID_Students"))
    open_sched = set()
    if ls and col(ls, "Lesson_Schedules", "Status"):
        open_sched = {r.get("id_student") for r in ls if r.get("Status") == "Open"}
    status = Counter((r.get("Status") or "(blank)") for r in st) if "Status" in st[0] else Counter()
    rows = [
        ("Students with flag_active = 1 and not trashed", len(active_flag)),
        (f"Students whose Last_Lesson_Date_End is within 90 days (since {recent})", len(recent_lesson)),
        ("Students with at least one Lesson_Schedules row with Status = Open", len(open_sched)),
        ("Students in all three sets", len(active_flag & recent_lesson & open_sched) if open_sched else "n/a"),
        ("Students flagged active but with no open schedule", len(active_flag - open_sched) if open_sched else "n/a"),
    ]
    if fam and col(st, "Students", "id_family"):
        fam_ids = {r.get("ID_Family") for r in fam}
        fam_active_flag = {r.get("ID_Family") for r in fam
                           if truthy(r.get("flag_active", "")) and not truthy(r.get("flag_trashcan", ""))}
        fam_with_active_student = {r.get("id_family") for r in st if r.get("ID_Students") in active_flag}
        fam_with_open = {r.get("id_family") for r in st if r.get("ID_Students") in open_sched}
        rows += [
            ("Families with flag_active = 1 and not trashed", len(fam_active_flag)),
            ("Families with at least one flag_active student", len(fam_with_active_student & fam_ids)),
            ("Families with at least one student in an Open schedule",
             len(fam_with_open & fam_ids) if open_sched else "n/a"),
        ]
    table(["Measure", "Count"], rows)
    if status:
        h(3, "Students.Status distribution")
        table(["Status", "Rows"], status.most_common())


def section_instructors(data):
    h(2, "Instructor first-name collisions")
    staff = data.get("Staff")
    if not staff:
        line("Staff export missing.")
        return
    col(staff, "Staff", "Name_First")
    instr = [r for r in staff if truthy(r.get("flag_instructor", "1"))]
    by_first = defaultdict(list)
    for r in staff:
        by_first[(r.get("Name_First") or "").strip().lower()].append(r)
    collisions = {k: v for k, v in by_first.items() if k and len(v) > 1}
    rows = [
        ("Staff rows", len(staff)),
        ("Staff with flag_instructor = 1", len(instr)),
        ("Distinct first names (case-insensitive)", len([k for k in by_first if k])),
        ("First names shared by more than one staff row", len(collisions)),
        ("Staff rows involved in a collision", sum(len(v) for v in collisions.values())),
        ("Collisions where more than one is flag_active",
         sum(1 for v in collisions.values() if sum(truthy(r.get("flag_active", "")) for r in v) > 1)),
    ]
    table(["Measure", "Count"], rows)
    if collisions:
        h(3, "Colliding first names")
        table(["First name", "Staff rows", "Active", "Instructors"],
              [(k.title(), len(v),
                sum(truthy(r.get("flag_active", "")) for r in v),
                sum(truthy(r.get("flag_instructor", "")) for r in v))
               for k, v in sorted(collisions.items())])

    # How the text join actually resolves in the big tables.
    first_to_ids = {k: {r.get("ID_Staff") for r in v} for k, v in by_first.items()}
    id_to_first = {r.get("ID_Staff"): (r.get("Name_First") or "").strip().lower() for r in staff}
    for tname, namecol in (("Lesson_Schedules", "Instructor"), ("Lesson_Attendance", "Instructor_Name"),
                           ("Lessons", "Instructor"), ("Lesson_Out", "Instructor")):
        rs = data.get(tname)
        if not rs or not col(rs, tname, namecol):
            continue
        has_id = "id_staff" in rs[0]
        c = Counter()
        for r in rs:
            first = (r.get(namecol) or "").strip().split(" ")[0].lower()
            ids = first_to_ids.get(first, set())
            sid = r.get("id_staff", "") if has_id else ""
            if not first:
                c["name blank"] += 1
            elif not ids:
                c["name matches no staff row"] += 1
            elif len(ids) > 1:
                c["name matches more than one staff row (ambiguous)"] += 1
            else:
                c["name matches exactly one staff row"] += 1
            if has_id:
                if not sid:
                    c["id_staff blank"] += 1
                elif sid not in id_to_first:
                    c["id_staff not in Staff"] += 1
                elif first and id_to_first[sid] != first:
                    c["id_staff disagrees with name"] += 1
        h(3, f"{tname}.{namecol} resolved against Staff")
        table(["Outcome", "Rows"], sorted(c.items()))


def section_dual_keys(data):
    h(2, "Dual-key disagreements (id_student vs id_family)")
    st = data.get("Students")
    fam = data.get("Families")
    if not st or not col(st, "Students", "id_family"):
        line("Students export (with id_family) missing.")
        return
    stu_fam = {r.get("ID_Students"): r.get("id_family") for r in st}
    fam_ids = {r.get("ID_Family") for r in fam} if fam else None
    for tname in ("Billing_Months", "Billing_Years", "Lesson_Schedules", "Waitlist"):
        rs = data.get(tname)
        if not rs or not col(rs, tname, "id_student") or not col(rs, tname, "id_family"):
            continue
        c = Counter()
        years = Counter()
        for r in rs:
            s, f = r.get("id_student", ""), r.get("id_family", "")
            if not s and not f:
                c["both blank"] += 1
            elif not s:
                c["id_student blank"] += 1
            elif not f:
                c["id_family blank"] += 1
            elif s not in stu_fam:
                c["id_student not in Students (orphan)"] += 1
            elif stu_fam[s] != f:
                c["student's family differs from row's id_family"] += 1
                created = to_date(r.get("CreationTimestamp", ""))
                years[r.get("Year") or (created.year if created else "?")] += 1
            else:
                c["agree"] += 1
            if fam_ids is not None and f and f not in fam_ids:
                c["id_family not in Families (orphan)"] += 1
        h(3, tname)
        table(["Outcome", "Rows"], sorted(c.items()))
        orphan_ids = {r.get("id_student") for r in rs if r.get("id_student") and r.get("id_student") not in stu_fam}
        if orphan_ids:
            orphan_rows = [r for r in rs if r.get("id_student") in orphan_ids]
            paid = sum(1 for r in orphan_rows if to_num(r.get("Amount_Paid_1", "")) or to_num(r.get("Amount_Paid_2", "")))
            fee = sum(1 for r in orphan_rows if to_num(r.get("Monthly_Fee", "")))
            oy = Counter(r.get("Year") or "?" for r in orphan_rows)
            line(f"Orphan id_student values: {len(orphan_ids)} distinct; {paid} orphan rows carry a payment, "
                 f"{fee} carry a Monthly_Fee.")
            line()
            table(["Year (orphan rows)", "Rows"], sorted(oy.items(), key=lambda kv: str(kv[0])))
        if years:
            line("Disagreements by year (Year column, else creation year):")
            line()
            table(["Year", "Rows"], sorted(years.items(), key=lambda kv: str(kv[0])))

    st_orph = sum(1 for r in st if fam_ids is not None and r.get("id_family") and r.get("id_family") not in fam_ids)
    st_nofam = sum(1 for r in st if not r.get("id_family"))
    h(3, "Students")
    table(["Outcome", "Rows"], [("id_family blank", st_nofam),
                                ("id_family not in Families (orphan)", st_orph if fam_ids is not None else "n/a")])


def section_caps(data):
    h(2, "ALL-CAPS names vs flag_Special_Needs")
    st = data.get("Students")
    if not st or not col(st, "Students", "Name_First"):
        line("Students export missing.")
        return
    has_flag = col(st, "Students", "flag_Special_Needs")
    c = Counter()
    for r in st:
        caps = is_all_caps(r.get("Name_First"))
        flag = truthy(r.get("flag_Special_Needs", "")) if has_flag else None
        c[(caps, flag)] += 1
    rows = [
        ("Stored Name_First ALL CAPS, flag_Special_Needs = 1", c[(True, True)]),
        ("Stored Name_First ALL CAPS, flag_Special_Needs = 0", c[(True, False)]),
        ("Stored Name_First not caps, flag_Special_Needs = 1", c[(False, True)]),
        ("Stored Name_First not caps, flag_Special_Needs = 0", c[(False, False)]),
    ]
    table(["Combination", "Students"], rows)
    if "Name_Last" in st[0]:
        line(f"Stored Name_Last ALL CAPS: {sum(1 for r in st if is_all_caps(r.get('Name_Last')))}")
    fam = data.get("Families")
    if fam and "Family_Name" in fam[0]:
        line(f"Families.Family_Name ALL CAPS: {sum(1 for r in fam if is_all_caps(r.get('Family_Name')))}")
    for tname, column in (("Families", "Primary_Name_First"), ("Families", "Secondary_Name_First"),
                          ("Students", "Primary_Name_First")):
        rs = data.get(tname)
        if rs and column in rs[0]:
            line(f"{tname}.{column} ALL CAPS (the hand-typed 'handle with care' convention): "
                 f"{sum(1 for r in rs if is_all_caps(r.get(column)))} of {sum(1 for r in rs if r.get(column))} populated")
    line()
    line("Reading: the on-screen caps come from `Name_First_calc`, which upper-cases *because of* the flag. "
         "Rows on the second line are the ones where caps carry meaning the flag does not, "
         "and are what the decode pass must catch.")


def section_nulls(data):
    h(2, "Unknown values (do not default these)")
    st = data.get("Students")
    if not st:
        return
    rows = []
    for column in ("Level", "Age", "Date_of_Birth", "Payment_Plan", "Status", "id_family", "Lesson_Type_1"):
        if column in st[0]:
            rows.append((f"Students.{column} blank", sum(1 for r in st if not r.get(column))))
    for column in ("OLD_ID", "OLD_STUD_ID", "OLD_FAMILY_ID"):
        if column in st[0]:
            rows.append((f"Students.{column} populated (prior migration)", sum(1 for r in st if r.get(column))))
    fam = data.get("Families")
    if fam and "OLD_FAMILY_ID" in fam[0]:
        rows.append(("Families.OLD_FAMILY_ID populated", sum(1 for r in fam if r.get("OLD_FAMILY_ID"))))
    table(["Measure", "Rows"], rows)


def section_money(data):
    h(2, "Payment volume (last 24 months)")
    bm = data.get("Billing_Months")
    if not bm or not col(bm, "Billing_Months", "Year") or not col(bm, "Billing_Months", "Month_Num"):
        line("Billing_Months export missing.")
        return
    for c in ("Amount_Paid_1", "Amount_Paid_2", "Payment_Type_1", "Payment_Type_2", "Payment_Plan_CC_DD", "Monthly_Fee"):
        col(bm, "Billing_Months", c)
    start = (TODAY.year - 2, TODAY.month)
    months = defaultdict(Counter)
    dollars = defaultdict(float)
    ptypes = Counter()
    plans = Counter()
    for r in bm:
        try:
            y, m = int(float(r["Year"])), int(float(r["Month_Num"]))
        except (ValueError, KeyError):
            continue
        if (y, m) < start or (y, m) > (TODAY.year, TODAY.month):
            continue
        key = f"{y}-{m:02d}"
        months[key]["rows"] += 1
        paid = 0.0
        for amt, typ in (("Amount_Paid_1", "Payment_Type_1"), ("Amount_Paid_2", "Payment_Type_2")):
            a = to_num(r.get(amt, ""))
            if a:
                months[key]["payments"] += 1
                paid += a
                t = (r.get(typ) or "(blank)").strip()
                ptypes[t] += 1
                months[key][f"type:{t}"] += 1
        if paid:
            months[key]["rows with a payment"] += 1
            dollars[key] += paid
        cc = (r.get("Payment_Plan_CC_DD") or "").strip()
        if cc:
            months[key][f"plan:{cc}"] += 1
            plans[cc] += 1
        fee = to_num(r.get("Monthly_Fee", ""))
        if fee:
            months[key]["rows with Monthly_Fee > 0"] += 1
    h(3, "Payment_Type values seen (Payment_Type_1 + Payment_Type_2, last 24 months)")
    table(["Payment_Type", "Payments"], ptypes.most_common())
    h(3, "Payment_Plan_CC_DD on Billing_Months rows (last 24 months)")
    table(["Plan", "Rows"], plans.most_common())
    h(3, "Per month")
    type_keys = [f"type:{t}" for t, _ in ptypes.most_common(4)]
    headers = (["Month", "Rows", "Fee > 0", "Rows paid", "Payments", "Dollars paid", "plan:CC", "plan:DD"]
               + [k[5:] for k in type_keys])
    rows = []
    for key in sorted(months):
        c = months[key]
        rows.append((key, c["rows"], c["rows with Monthly_Fee > 0"], c["rows with a payment"], c["payments"],
                     f"{dollars[key]:,.0f}", c["plan:CC"], c["plan:DD"]) + tuple(c[k] for k in type_keys))
    table(headers, rows)
    line("Card volume per month = payments whose Payment_Type is the card value (see the type columns), "
         "or rows on a CC plan. Compare with staff's reported 550-700.")


def section_placeholders(data):
    h(2, "Placeholder and pseudo rows (every real search excludes these)")
    rows = []
    ls = data.get("Lesson_Schedules")
    if ls:
        rows.append(("Lesson_Schedules with ID_Lesson_Schedule = DUMMY", sum(1 for r in ls if r.get("ID_Lesson_Schedule") == "DUMMY")))
        if "flag_dummy" in ls[0]:
            rows.append(("Lesson_Schedules with flag_dummy = 1", sum(1 for r in ls if truthy(r.get("flag_dummy")))))
        if "Student" in ls[0]:
            rows.append(("Lesson_Schedules whose Student text starts with 'Inst'",
                         sum(1 for r in ls if (r.get("Student") or "").strip().lower().startswith("inst"))))
        if "flag_hold" in ls[0]:
            rows.append(("Lesson_Schedules with flag_hold = 1", sum(1 for r in ls if truthy(r.get("flag_hold")))))
        if "flag_break" in ls[0]:
            rows.append(("Lesson_Schedules with flag_break = 1", sum(1 for r in ls if truthy(r.get("flag_break")))))
    st = data.get("Students")
    if st:
        rows.append(("Students with Name_First = Inst", sum(1 for r in st if (r.get("Name_First") or "").strip().lower() == "inst")))
    lessons = data.get("Lessons")
    if lessons:
        if "Student" in lessons[0]:
            rows.append(("Lessons whose Student text starts with 'Inst'",
                         sum(1 for r in lessons if (r.get("Student") or "").strip().lower().startswith("inst"))))
        if "flag_has_break" in lessons[0]:
            rows.append(("Lessons with flag_has_break = 1", sum(1 for r in lessons if truthy(r.get("flag_has_break")))))
    table(["Measure", "Rows"], rows)


def section_makeup_replay(data):
    h(2, "Make-up ledger replay vs stored counters (ADR-0003 rehearsal)")
    st, out, ls = data.get("Students"), data.get("Lesson_Out"), data.get("Lesson_Schedules")
    if not (st and out and ls):
        line("Needs Students, Lesson_Out and Lesson_Schedules.")
        return
    for t, c in (("Lesson_Out", "Makeup_Type"), ("Lesson_Out", "flag_count"), ("Lesson_Schedules", "Lesson_MU_to_use"),
                 ("Lesson_Schedules", "Lesson_MU_Amount")):
        col(data[t], t, c)
    # Issued: one credit per Lesson_Out row that counts (flag_count = 1, i.e. not flag_do_not_issue).
    issued = defaultdict(Counter)
    mt = Counter()
    for r in out:
        d = (r.get("Makeup_Type") or "").strip().upper()
        mt[d or "(blank)"] += 1
        if truthy(r.get("flag_count", "1")) and not truthy(r.get("flag_do_not_issue", "")):
            issued[r.get("id_student")][d] += 1
    # Redeemed: Lesson_Schedules rows with Lesson_MU_to_use set consume Lesson_MU_Amount (default 1) of that denomination.
    redeemed = defaultdict(Counter)
    use, amt = Counter(), Counter()
    for r in ls:
        d = (r.get("Lesson_MU_to_use") or "").strip().upper()
        if not d:
            continue
        use[d] += 1
        a = to_num(r.get("Lesson_MU_Amount", "")) or 1.0
        amt[str(a)] += 1
        redeemed[r.get("id_student")][d] += a
    h(3, "Lesson_Out.Makeup_Type (upper-cased)")
    table(["Denomination", "Rows"], mt.most_common())
    h(3, "Lesson_Schedules.Lesson_MU_to_use (upper-cased) and Lesson_MU_Amount")
    table(["Denomination", "Rows"], use.most_common())
    table(["Amount", "Rows"], sorted(amt.items(), key=lambda kv: float(kv[0])))
    line("Amounts other than 1 are the conversions: 2 SP for a PR lesson, 4 group for a PR, 0.5 PR for an SP lesson.")
    line()
    stored_cols = {"SP": "MU_SP_Total", "PR": "MU_PR_Total", "PM": "MU_PM_Total", "GR": "MU_GR_Total", "ST": "MU_ST_Total"}
    # 1. FileMaker's own formula (DDR): MU_X_Total = Sum(Lesson_Out.flag_MU_X) - Sum(Lesson_Schedules.flag_MU_X),
    #    a stored number re-evaluated only when Students.flag_update fires. Every flag is 0/1, so do-not-issue
    #    rows still count as issued and a 2-for-1 conversion still counts as one redemption.
    fm_issued, fm_redeemed = defaultdict(Counter), defaultdict(Counter)
    for r in out:
        for d in stored_cols:
            if truthy(r.get(f"flag_MU_{d}", "")):
                fm_issued[r.get("id_student")][d] += 1
    for r in ls:
        for d in stored_cols:
            if truthy(r.get(f"flag_MU_{d}", "")):
                fm_redeemed[r.get("id_student")][d] += 1
    h(3, "Replay 1 — FileMaker's stored formula (flagged out rows minus flagged schedule rows)")
    rows = []
    for d, sc in stored_cols.items():
        if sc not in st[0]:
            continue
        n = m = over = under = 0
        for r in st:
            sid = r.get("ID_Students")
            stored = to_num(r.get(sc, "")) or 0.0
            bal = float(fm_issued[sid][d] - fm_redeemed[sid][d])
            if not (stored or bal):
                continue
            n += 1
            if abs(stored - bal) < 1e-9:
                m += 1
            elif stored > bal:
                over += 1
            else:
                under += 1
        rows.append((d, n, m, over, under, f"{(100.0 * m / n):.0f}%" if n else "n/a"))
    table(["Denomination", "Students with activity", "Stored = formula", "Stored > formula", "Stored < formula", "Match rate"], rows)
    line("A miss here is a counter FileMaker never re-evaluated (or a script that wrote it directly): the stored value "
         "is stale, not the ledger. This is the list the Scheduling & search gate classifies.")
    line()
    h(3, "Replay 2 — the ADR-0003 business rule (do-not-issue excluded, conversion amounts honoured)")
    # Compare with stored counters, denomination by denomination.
    rows = []
    for d, sc in stored_cols.items():
        if sc not in st[0]:
            MISSING.append(("Students", sc))
            continue
        match_bal = match_issued = differ = stored_nonzero = 0
        diffs = Counter()
        for r in st:
            sid = r.get("ID_Students")
            stored = to_num(r.get(sc, "")) or 0.0
            iss = float(issued[sid][d])
            red = float(redeemed[sid][d])
            bal = iss - red
            if stored:
                stored_nonzero += 1
            if abs(stored - bal) < 1e-9:
                match_bal += 1
            elif abs(stored - iss) < 1e-9:
                match_issued += 1
            else:
                differ += 1
                diffs["stored > replayed balance" if stored > bal else "stored < replayed balance"] += 1
        rows.append((d, stored_nonzero, match_bal, match_issued, differ,
                     diffs["stored > replayed balance"], diffs["stored < replayed balance"]))
    table(["Denomination", "Students with stored counter != 0", "Stored = issued - redeemed", "Stored = issued only",
           "Neither", "of which stored > balance", "of which stored < balance"], rows)
    line("Same comparison restricted to students with any activity in that denomination "
         "(stored != 0, or an issue, or a redemption):")
    line()
    rows = []
    for d, sc in stored_cols.items():
        if sc not in st[0]:
            continue
        n = m = 0
        for r in st:
            sid = r.get("ID_Students")
            stored = to_num(r.get(sc, "")) or 0.0
            iss, red = float(issued[sid][d]), float(redeemed[sid][d])
            if not (stored or iss or red):
                continue
            n += 1
            if abs(stored - (iss - red)) < 1e-9:
                m += 1
        rows.append((d, n, m, n - m, f"{(100.0 * m / n):.0f}%" if n else "n/a"))
    table(["Denomination", "Students with activity", "Replay matches stored", "Differs", "Match rate"], rows)
    ad_out = Counter()
    for r in out:
        if (r.get("Makeup_Type") or "").strip().upper() == "AD":
            ad_out["counted" if truthy(r.get("flag_count", "1")) and not truthy(r.get("flag_do_not_issue", "")) else "not counted"] += 1
    if ad_out:
        line(f"Lesson_Out rows of type AD (adults issue no credit per ADR-0003): {dict(ad_out)}")
        line()
    unk = sum(1 for r in st if to_num(r.get("MU_Unknown_Total", ""))) if "MU_Unknown_Total" in st[0] else "n/a"
    old_mu = sum(1 for r in st if to_num(r.get("OLD_MU_REMAINING", ""))) if "OLD_MU_REMAINING" in st[0] else "n/a"
    neg = sum(1 for r in st for sc in stored_cols.values() if sc in r and (to_num(r.get(sc, "")) or 0) < 0)
    table(["Measure", "Students"], [
        ("MU_Unknown_Total != 0", unk),
        ("OLD_MU_REMAINING populated (balance carried from the previous migration)", old_mu),
        ("Any stored MU_*_Total negative", neg),
        ("Students with at least one counted Lesson_Out row", len([s for s in issued if sum(issued[s].values())])),
        ("Students with at least one redemption row", len(redeemed)),
    ])
    line("Reading: 'Stored = issued - redeemed' means the six counters are balances the ledger can replay; "
         "'Stored = issued only' means they count issues and redemptions live elsewhere; 'Neither' is the "
         "reconciliation list the import must produce per student. This is the rehearsal, not the import's rule.")
    if "Adult_Credit" in ls[0]:
        nonblank = Counter((r.get("Adult_Credit") or "").strip() for r in ls if (r.get("Adult_Credit") or "").strip())
        h(3, "Lesson_Schedules.Adult_Credit (ADR-0004 opening packs)")
        table(["Measure", "Rows"], [("Rows with a non-blank Adult_Credit", sum(nonblank.values())),
                                    ("Distinct values", len(nonblank))])
        if nonblank:
            table(["Value", "Rows"], nonblank.most_common(20))


def section_pre2020(data):
    h(2, "Pre-2020 Billing_Months: are amounts stamped on the row?")
    bm = data.get("Billing_Months")
    if not bm or not col(bm, "Billing_Months", "Year"):
        return
    by = defaultdict(Counter)
    for r in bm:
        try:
            y = int(float(r["Year"]))
        except ValueError:
            continue
        band = "< 2020" if y < 2020 else ">= 2020"
        by[band]["rows"] += 1
        for c in ("Monthly_Fee", "Rate_1", "Amount_Paid_1", "Cumulative_Balance"):
            if c in r and to_num(r.get(c)) is not None:
                by[band][f"{c} populated"] += 1
    keys = ["rows", "Monthly_Fee populated", "Rate_1 populated", "Amount_Paid_1 populated", "Cumulative_Balance populated"]
    table(["Year band"] + keys, [(b,) + tuple(by[b][k] for k in keys) for b in sorted(by)])
    line("Billing_Rates has rows for 2020-2026 only; rows before 2020 must carry their own amounts or the history is unpriced.")


# Free-text columns scanned (streaming, never loaded) for card-number-shaped digit runs
# and for cells at Excel's 32,767-character limit (the export passed through .xlsx).
TEXT_SCAN = {
    "Families": ["Notes_General", "Referral_Notes", "Credit_Card_1_Exp_Date", "Credit_Card_2_Exp_Date"],
    "Students": ["Notes_General", "Instructor_Notes", "Notes_Attendance", "Notes_Deck_Manager", "Notes_MU",
                 "Referral_Notes", "FoundSetIDs_SMS", "sum_id_family"],
    "Billing_Months": ["Payment_Notes"],
    "Billing_Years": ["Notes"],
    "Lesson_Attendance": ["Intructor_Notes_to_Office"],
    "Lesson_Out": ["Notes"],
    "Lesson_Schedules": ["Student_Notes", "import_Pool_Notes"],
    "Waitlist": ["Notes", "Time_Notes"],
    "Notes": ["Note"],
    "Audits": ["Log"],
    "Staff": ["Notes"],
}
_DIGIT_RUN = re.compile(r"(?<!\d)(?:\d[ -]?){12}\d{1,4}(?!\d)")


def _luhn(digits):
    total, alt = 0, False
    for ch in reversed(digits):
        n = int(ch)
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        alt = not alt
    return total % 10 == 0


def section_text_scan(folder):
    h(2, "Free-text scan: card-number-shaped digit runs and truncated cells")
    line("Counts only. A 'digit run' is 13-16 digits with optional spaces or dashes; Luhn-valid runs are the ones "
         "that look like real card numbers. Truncated = cell length exactly 32,767, the .xlsx limit.")
    line()
    rows = []
    for tname, columns in TEXT_SCAN.items():
        path = find_file(folder, tname)
        if not path:
            rows.append((tname, ", ".join(columns), "file missing", "", "", "", ""))
            continue
        runs = luhn = trunc = cells = rows_hit = 0
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            present = [c for c in columns if c in (reader.fieldnames or [])]
            for r in reader:
                hit = False
                for c in present:
                    v = r.get(c) or ""
                    if not v:
                        continue
                    cells += 1
                    if len(v) >= 32767:
                        trunc += 1
                    for m in _DIGIT_RUN.finditer(v):
                        runs += 1
                        hit = True
                        if _luhn(re.sub(r"\D", "", m.group(0))):
                            luhn += 1
                if hit:
                    rows_hit += 1
        rows.append((tname, ", ".join(present) or "(none of the listed columns present)", cells, runs, luhn, rows_hit, trunc))
    table(["Table", "Columns scanned", "Populated cells", "Digit runs", "Luhn-valid", "Rows with a run", "Truncated cells"], rows)


# ---------- main ----------

TABLES = ["Staff", "Families", "Students", "Billing_Months", "Billing_Years", "Lesson_Schedules",
          "Lesson_Attendance", "Lessons", "Lesson_Out", "Waitlist", "Billing_Rates", "Holiday_Dates"]


def main():
    if len(sys.argv) not in (2, 3) or not os.path.isdir(sys.argv[1]):
        sys.stderr.write(__doc__)
        sys.exit(2)
    folder = sys.argv[1]
    label = sys.argv[2] if len(sys.argv) == 3 else os.path.basename(os.path.normpath(folder))
    data = {t: load(folder, t) for t in TABLES}
    h(1, f"Data profile of live FileMaker export: {label}")
    line(f"Generated {TODAY} by `scripts/profile_exports.py`. Aggregates only; source files are not committed.")
    line("Sections: row counts, date ranges, active vs historical, instructor collisions, dual keys and orphans, "
         "ALL-CAPS names, unknown values, payment volume, pre-2020 billing rows, placeholder rows, the make-up "
         "ledger replay (FileMaker's formula and the ADR-0003 rule), and a free-text scan for card-number-shaped "
         "digit runs and truncated cells. Paste the numbers the ticket asks for into its resolution.")
    section_counts(data)
    section_date_ranges(data)
    section_activity(data)
    section_instructors(data)
    section_dual_keys(data)
    section_caps(data)
    section_nulls(data)
    section_money(data)
    section_pre2020(data)
    section_placeholders(data)
    section_makeup_replay(data)
    section_text_scan(folder)
    if MISSING:
        h(2, "Missing files or columns (facts skipped)")
        table(["Table", "Column"], sorted(set(MISSING)))
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(OUT))


if __name__ == "__main__":
    main()
