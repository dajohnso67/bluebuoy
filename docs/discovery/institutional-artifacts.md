# Institutional billing artifacts — collection checklist

**Wayfinder ticket:** [Institutional billing artifacts](https://github.com/dajohnso67/bluebuoy/issues/9).
**Why:** charter-school and Regional Center billing has no trace in FileMaker (package 2.9, Confirmed). [ADR-0002](../adr/0002-no-authorization-balance-tracking.md) decided the payer model; three details of it, and the Institutional payers gate in `PLAN.md` §5, wait on seeing the real paperwork. This page lists exactly what to collect, what each artifact settles, and where it goes. Nothing here asks staff a question; it asks for things that already exist.

## Where artifacts go

- Raw files (PDFs, screenshots, spreadsheet exports) go in `resources/artifacts/institutional/`, which is **gitignored**. They carry student names, school financials, and possibly disability-related information (Regional Center involvement), so they never enter the repo.
- Name each file `<artifact-id>-<source>-<YYYY-MM>.<ext>`, for example `A1-charter-invoice-2026-06.pdf`.
- The committed record is the **Inventory** and **Facts settled** sections at the bottom of this page: filename, source, date, and the answer each artifact gave. Quote invoice layouts by structure, never by student name.

## What to collect

Minimum set is A1, B1, B2, C1 and C2, D1. The rest sharpen the same decisions and are worth grabbing while in the systems.

### A — Charter school invoices (the emailed / paper workflow)

| Id | Artifact | Where it lives | Redact |
| --- | --- | --- | --- |
| **A1** | One real charter invoice as actually sent, for a recent closed month. If the emailed and paper formats differ, one of each. | The sent-items folder of whoever sends them, or the QuickBooks invoice PDF | student names → initials; leave PO number, school, period, rates, counts, invoice number, terms |
| A2 | The email or cover letter it went out with, if there is one | same mailbox | recipient personal names |
| A3 | A second invoice from a different school, if formats vary by school | same | same |

**Settles:**
1. Whether one invoice covers one student or batches every student the school funds for the month. `PLAN.md` §2 assumes batching per payer; if it is per student, `invoice` needs a student dimension.
2. Whether the PO number is cited per invoice, per line, or not at all, and whether it changes month to month or holds for a school year. This is the **validity granularity of `funding_reference`** that ADR-0002 left open.
3. Whether the invoice lists lesson dates or a lesson count. If it does, invoicing depends on attendance and the Institutional payers phase inherits an attendance dependency; if it bills a flat monthly rate, it does not.
4. Where the invoice number comes from (`11237`, `11257`, `11309` in the notes look like one sequence). If QuickBooks assigns it, the app must either import numbers from QuickBooks or hand invoices to it unnumbered.
5. Payment terms printed on the invoice, if any: the terms clock that `invoice.issued` starts.

### B — The receivables trail (QuickBooks and Excel)

| Id | Artifact | Where it lives | Redact |
| --- | --- | --- | --- |
| **B1** | A screenshot or export of the **open invoices / A/R aging** view for institutional customers | QuickBooks: Reports → A/R Aging Summary or Open Invoices, filtered to charter and RC customers | nothing beyond student names if they appear |
| **B2** | The **customer list** as QuickBooks holds it: are the 14 schools and 9 agencies customers, are students sub-customers or jobs, or is each family the customer with the school as a note? | QuickBooks: Customers list, or Customer Contact List report | family names → initials |
| B3 | The Excel tracking sheet, if one exists alongside QuickBooks, with one month of rows | wherever it is kept | student names |
| B4 | One example of a **check that paid several invoices** and how it was applied | QuickBooks: Receive Payment screen for that deposit, or the deposit slip | account numbers on the check image |
| B5 | Which QuickBooks it is: **Desktop or Online**, and the version or subscription level | Help → About, or the browser URL | nothing |

**Settles:**
1. The reconciliation boundary. ADR-0002 keeps QuickBooks as the accounting system; B2 and B5 decide whether the app pushes invoices and payments into it (Online has an API; Desktop takes IIF or CSV imports, or nothing) or only mirrors what staff enter there.
2. Whether `payment_application` matches reality: one check settling several students' invoices is the assumed normal case; B4 confirms it and shows what a partial application looks like.
3. Whether receivables aging can be seeded from history at cutover, and how far back. B1 shows what is open today; if the aging report is the only place that trail exists, the cutover import needs it.
4. Whether the free-text notes in FileMaker (`JAN 11237 $368 (sent 1/15)`, `CK 7499`) are a copy of QuickBooks or the only record. If QuickBooks holds the same facts structured, the notes need no parsing at import.

### C — The two portal submission workflows

| Id | Artifact | Where it lives | Redact |
| --- | --- | --- | --- |
| **C1** | A walkthrough of the **first** portal workflow: screenshots of each screen from login to confirmation, or a narrated description if screenshots are impractical | the school's portal, with whoever holds the login | student names, login credentials, any URL token |
| **C2** | The same for the **second** portal workflow | same | same |
| C3 | The list of **which schools use which method**: emailed invoice, paper invoice, or portal, and for portal schools the portal's name or vendor | the person who does month-end billing; likely the same note as D1 | nothing |
| C4 | Whatever the portal gives back as **proof of submission**: a confirmation number, an email, a status page | same | tokens |

**Settles:**
1. What the app has to produce for a portal school. If the portal wants per-lesson dates, the app needs an attendance export in that shape; if it wants a monthly total, a figure is enough. This decides whether `submission method = portal` is a workflow the app supports or one it only records.
2. Whether the portal **replaces** the invoice or accompanies it. If a portal school also wants an invoice, `submitted_at` means two things.
3. What counts as `submitted` for a portal school, for the invoice status machine and the receivables clock.
4. Whether one login serves all portal schools or each school has its own, which decides whether credentials belong in the payer configuration.

### D — Payer configuration as it exists today

| Id | Artifact | Where it lives | Redact |
| --- | --- | --- | --- |
| **D1** | The **text note listing the 14 charter schools and 9 Regional Center agencies** with how to bill each | FileMaker: the note staff read when billing; the DDR shows no value list for it, so it is typed text somewhere on a Preferences or family screen | nothing |
| D2 | One charter school's **rate sheet or contract** for the current school year (July negotiation) | the billing team's files | signatures, personal contact details |
| D3 | One Regional Center **contract or authorization letter** the family arranged, if Blue Buoy holds a copy | the family's file, or the billing team | family name, UCI number → last 3 digits, coordinator personal details |
| D4 | One example of the **direct-check agency**: how the amount is known and what arrives with the check | the deposit record | account numbers |
| D5 | One family account's **bold header note** with a UCI number and coordinator contact, as a screenshot | FileMaker family screen | UCI → last 3 digits, coordinator name and phone |

**Settles:**
1. D1 becomes the seed for the `payer` rows: name, type, submission method, billing contact. It is the closest thing to a source of truth that exists.
2. D2 gives `price_agreement` real numbers and shows whether a contract rate is per lesson type, per student, or flat, and whether it has an explicit validity range.
3. D3 shows what a Regional Center funding reference looks like: whether there is a contract number to cite, and whether it carries dates. Together with A1 this fixes the `funding_reference` kinds and their fields.
4. D4 decides the invoice status flow for a payer that never receives an invoice: whether such an invoice is created internally and goes straight to `paid`, or whether no invoice exists and the payment stands alone.
5. D5 fixes the shape of the structured UCI and coordinator fields on `payer_assignment`, and confirms what the decode pass must lift out of bold notes.

## Handling rules while collecting

- Do not export or photograph credit-card fields on any FileMaker screen. Crop them out.
- Regional Center material identifies a child's developmental-disability status. Keep it to the gitignored folder and the billing-team channel; do not paste it into the ticket.
- Screenshots of portals must not include session URLs or saved-password prompts.
- If an artifact does not exist (no Excel sheet, no contract copy), record that in the Inventory as a fact. Absence is an answer.

## Inventory

*Fill in as artifacts land. One row per file.*

| Id | File | Source | Date of artifact | Redacted | Notes |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Facts settled

*Fill in on resolution. One row per question above, citing the artifact id.*

| Question | Answer | From |
| --- | --- | --- |
| Invoice per student or per payer batch | | A1 |
| PO number cited where, and valid for how long | | A1, D3 |
| Invoice lists lesson dates / counts, or flat rate | | A1 |
| Invoice number source | | A1, B2 |
| Payment terms | | A1 |
| QuickBooks edition and customer structure | | B2, B5 |
| One check to many invoices confirmed; partial applications | | B4 |
| Notes trail is a copy of QuickBooks, or the only record | | B1, B3 |
| Portal 1: what is entered, what comes back, replaces or accompanies invoice | | C1, C4 |
| Portal 2: same | | C2, C4 |
| Method per school (the 14 + 9) | | C3, D1 |
| Contract rate shape and validity | | D2 |
| Direct-check agency flow | | D4 |
| UCI / coordinator field shape | | D5 |
