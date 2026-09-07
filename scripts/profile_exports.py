#!/usr/bin/env python3
"""Profile live FileMaker exports into the facts the DDR cannot yield.

Usage:  python scripts/profile_exports.py resources/exports/YYYY-MM-DD > docs/discovery/data-profile-YYYY-MM-DD.md

Reads the Merge/CSV files listed in docs/discovery/data-profiling-export.md
(one file per table, header row = FileMaker field names) and prints a Markdown
report of aggregates only: counts, date ranges, distributions. No student or
family names are printed; instructor first names appear only where they collide.

Standard library only. A missing table or column skips that fact and says so.
"""
import csv
import glob
import os
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
        if base.lower() == table.lower() and ext.lower() in (".csv", ".mer", ".tab", ".txt"):
            return cand
    return None


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
                rows = []
                for r in reader:
                    # FileMaker exports embedded returns as \v; normalise.
                    rows.append({(k or "").strip(): (v or "").replace("\x0b", "\n").strip()
                                 for k, v in r.items()})
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


# ---------- main ----------

TABLES = ["Staff", "Families", "Students", "Billing_Months", "Billing_Years", "Lesson_Schedules",
          "Lesson_Attendance", "Lessons", "Lesson_Out", "Waitlist", "Billing_Rates", "Holiday_Dates"]


def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        sys.stderr.write(__doc__)
        sys.exit(2)
    folder = sys.argv[1]
    data = {t: load(folder, t) for t in TABLES}
    h(1, f"Data profile of live FileMaker export: {os.path.basename(os.path.normpath(folder))}")
    line(f"Generated {TODAY} by `scripts/profile_exports.py`. Aggregates only; source files are not committed.")
    line("Sections: row counts, date ranges, active vs historical, instructor collisions, dual keys, "
         "ALL-CAPS names, unknown values, payment volume. Paste the numbers the ticket asks for into its resolution.")
    section_counts(data)
    section_date_ranges(data)
    section_activity(data)
    section_instructors(data)
    section_dual_keys(data)
    section_caps(data)
    section_nulls(data)
    section_money(data)
    if MISSING:
        h(2, "Missing files or columns (facts skipped)")
        table(["Table", "Column"], sorted(set(MISSING)))
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(OUT))


if __name__ == "__main__":
    main()
