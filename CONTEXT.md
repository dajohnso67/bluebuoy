# Blue Buoy — Domain Context

Vocabulary for the swim school and the system replacing FileMaker. Output that names a domain concept — a table, an endpoint, an issue title, a test name — uses the term as defined here.

Seeded from the FileMaker analysis and [`qa.md`](./qa.md). Terms marked **open** are genuinely unsettled; [`docs/migration/open-questions.md`](./docs/migration/open-questions.md) tracks what each one blocks.

## People & accounts

- **Household** — the family unit a bill is addressed to. Siblings share one.
- **Person** — a human record: student, guardian, billing contact, instructor. One person holds several roles; an adult student is a person who is both student and billing contact.
- **Student** — a person enrolled in lessons. Carries level, date of birth, and flags.
- **Account** — **open**: whether the household or the student is the unit that owes money. FileMaker tracks both and neither clearly wins (qa.md Q49). Every billing surface waits on this.

## Catalog

- **Class type** — Parent & Me, Group, Semi-Private, Private, Stroke Tech, Adult.
- **Level** — the ordinal skill rank a student sits at. Combines with age to decide eligibility.
- **Eligibility rule** — the age-and-level bar for a class type, held as data rather than code so a confirmed answer lands as a row (qa.md Q60–Q63).

## Scheduling

- **Slot** — a recurring place on the schedule: instructor, weekday, time, class type, capacity. The thing a family holds week to week.
- **Enrollment** — a student's claim on a slot over a date range. The billable relationship.
- **Lesson** — one dated occurrence of a slot. The thing attended, cancelled, or made up.
- **Attendance** — a student's outcome for a lesson, plus who marked it and on which device.
- **Closure** — a date range the pool is shut: the December/January break, a holiday, weather, maintenance. Carries whether it issues credit.
- **Waitlist entry** — a student wanting a slot that does not exist yet, with the availability their family stated.

## Money

- **Payer** — whoever the invoice goes to: a household, one of 14 charter schools, or one of 9 Regional Center agencies. A household's children can have different payers (qa.md Q11).
- **Funding reference** — the family-obtained funding a student's institutional invoicing cites: a charter-school **PO** (the staff term) or a Regional Center contract. A reference number and kind, not a balance — Blue Buoy has no visibility into amounts or caps ([ADR-0002](./docs/adr/0002-no-authorization-balance-tracking.md)); its *absence* for a billing period is what surfaces as an exception (qa.md Q6–Q7, answered).
- **Price agreement** — the rate a given enrollment is actually charged, with its reason (list price, sibling step, prepay lock, negotiated institutional rate) and the dates it holds. The record that makes a locked prepay rate survive a price rise without monthly hand-correction.
- **Snapshot price** — the amount resolved onto an invoice line at issue. Reprinting an old invoice reproduces it exactly, because nothing recomputes.
- **Credit ledger** — the append-only record of credits issued and consumed: make-up, referral, gift certificate, courtesy, account. A balance is a query over it, never a field someone must remember to reset.
- **Make-up credit** — a credit issued when a lesson is missed or cancelled by the school, spendable on a future lesson.
- **Billing run** — the month-end process that prices every active enrollment and issues invoices. Runs in three modes: dry run, shadow, committed.
- **Exception** — a household the billing run declines to price without a human look. Replaces the spreadsheet cross-reference.
- **Adjustment** — a deliberate one-off correction to an invoice, with a reason and an author. Kept for real one-offs, once the routine cases become price agreements and credits.

## Flags & notes

- **Flag** — typed, structured fact about a student that changes how staff act: allergy, support need, swim-diaper requirement, account handling. Replaces meaning encoded in ALL CAPS names and colour highlights (qa.md Q67, Q68, Q71).
- **Note** — free text about a student or household, with an explicit audience: office-only, instructor-visible, or both.
