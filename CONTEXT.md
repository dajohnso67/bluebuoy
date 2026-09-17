# Blue Buoy — Domain Context

Vocabulary for the swim school and the system replacing FileMaker. Output that names a domain concept — a table, an endpoint, an issue title, a test name — uses the term as defined here.

Seeded from the FileMaker analysis and [`qa.md`](./qa.md). Terms marked **open** are genuinely unsettled; [`docs/migration/open-questions.md`](./docs/migration/open-questions.md) tracks what each one blocks.

## People & accounts

- **Household** — the family unit a bill is addressed to. Siblings share one.
- **Person** — a human record: student, guardian, billing contact, instructor. One person holds several roles; an adult student is a person who is both student and billing contact.
- **Student** — a person enrolled in lessons. Carries level, date of birth, and flags.
- **Account** — **open**: whether the household or the student is the unit that owes money. FileMaker tracks both and neither clearly wins (qa.md Q49). Every billing surface waits on this.
- **Archived household** — a family moved out of the live FileMaker file after ten idle years (`BlueBuoy_FM_2024`). Restorable, never deleted; what the import does with them is **open** (qa.md Q99, the archive row).

## Catalog

- **Class type** — Parent & Me, Group (staff also say Stroke Prep), Semi-Private, Private, Stroke Tech, Adult. The three group types and Adult cap at six; group classes run on a fixed annual timetable, so joining one is a seat question (qa.md Q59, answered).
- **Group band** — the age-and-level range one particular group class admits, as the deck screen shows it (`AGE 7+ lv 8/9/10`). An eligibility rule scoped to a slot rather than a type.
- **Level** — the ordinal skill rank a student sits at. Combines with age to decide eligibility.
- **Eligibility rule** — the age-and-level bar for a class type, or for one slot, held as data rather than code so a confirmed answer lands as a row (qa.md Q60–Q63; the group bars are answered, Private and Semi-Private are not).

## Scheduling

- **Slot** — a recurring place on the schedule: instructor, weekday, time, class type, capacity. The thing a family holds week to week.
- **Slot repurpose** — an empty group slot lent for one day to other lesson types when a substitute is needed. A dated override, never an edit to the slot (qa.md Q59, answered).
- **Enrollment** — a student's claim on a slot over a date range. The billable relationship.
- **Lesson** — one dated occurrence of a slot. The thing attended, cancelled, or made up.
- **Attendance** — a student's outcome for a lesson, plus who marked it and on which device.
- **Closure** — a date range the pool is shut: the December/January break, a holiday, weather, maintenance. Carries whether it issues credit; an incidental closure issues credits in bulk by weekday or pool, per student either a credit or a closure waiver.
- **Waitlist entry** — a student wanting a slot that does not exist yet, with the availability their family stated.
- **Seat hold** — a semi-private slot kept free of a second student for a set period, typically four weeks, because a teacher thinks a child needs it; carries a review date. A seat attribute, never a student attribute (qa.md Q111, answered).
- **Instructor block** — a teacher's regular break or an ad hoc block for a day, excluded from availability like a seat hold but a different thing: day-level lifetime, no student (qa.md Q111, answered). _Avoid_: break, hold (FileMaker's `flag_hold` means "no lesson type").
- **Enrollment offer** — a slot offered to a family pending payment. Holds the slot until 5 pm the following day, then releases it and cancels the payment request (qa.md Q112, answered).
- **Make-up offer** — one or two slots offered to a family holding a make-up credit, each genuinely held for a short window (an hour or two, adjustable per offer) and offered to one family at a time; on expiry the slot passes to the next candidate (qa.md Q102 assumed, Q113 open). _Avoid_: shortlist.
- **Closure waiver** — skipping a holiday's make-up credit and prorating tuition instead: a new student whose first lesson falls on a closure, or a goodwill gesture allowed once per family and recorded so the answer is on screen next time (qa.md Q43 answered, Q114 open).

## Money

- **Payer** — whoever the invoice goes to: a household, one of 14 charter schools, or one of 9 Regional Center agencies. A household's children can have different payers (qa.md Q11).
- **Funding reference** — the family-obtained funding a student's institutional invoicing cites: a charter-school **PO** (the staff term) or a Regional Center contract. A reference number and kind, not a balance — Blue Buoy has no visibility into amounts or caps ([ADR-0002](./docs/adr/0002-no-authorization-balance-tracking.md)); its *absence* for a billing period is what surfaces as an exception (qa.md Q6–Q7, answered).
- **Price agreement** — the rate a given enrollment is actually charged, with its reason (list price, sibling step, prepay lock, negotiated institutional rate) and the dates it holds. The record that makes a locked prepay rate survive a price rise without monthly hand-correction.
- **Snapshot price** — the amount resolved onto an invoice line at issue. Reprinting an old invoice reproduces it exactly, because nothing recomputes.
- **Credit ledger** — the append-only record of credits issued and consumed: make-up, referral, gift certificate, courtesy, account. A balance is a query over it, never a field someone must remember to reset.
- **Make-up credit** — a credit issued when a lesson is missed or cancelled by the school, spendable on a future lesson; never issued for Adult, whose class packs cover attendance. Denominated **private**, **semi-private**, or **group** (Group, Stroke Tech and Parent & Me are one denomination), counted in whole lessons, convertible between denominations at the conversion table's rates in either direction when redeemed, and expiring only if the expiry rule says so (qa.md Q100 answered; Q47 open; [ADR-0003](./docs/adr/0003-denominated-makeup-credit-ledger.md)). _Avoid_: MU, make-up balance.
- **Reservation** — a make-up credit held against a booked make-up lesson. Consumed when the lesson happens, released if the school cancels it; a reserved credit cannot expire.
- **Credit event** — a conversion, transfer, reversal, expiry, void, or reconciliation on the ledger, with an author. A reversal is a new event that negates an earlier one; nothing is ever deleted.
- **Reconciliation event** — the one event per student and denomination written at import that issues or consumes the difference between the replayed rows and FileMaker's stored counter, carrying both numbers and who confirmed it. Unreviewed until the office confirms it or management corrects it; an unreviewed one shows as a marker when a make-up is booked, never a block ([ADR-0005](./docs/adr/0005-makeup-balance-reconciliation-at-import.md)). _Avoid_: opening balance, adjustment.
- **Credit liability** — outstanding make-up credits valued in private-lesson equivalents: four group or two semi-private per private. Dollars are only ever a reporting column.
- **Conversion rate** — a row in the exchange table: two semi-private make one private, two group make one semi-private, four group make one private. Data, not code.
- **Credit transfer** — moving make-up credits from one sibling to another inside a household, keeping their origin and expiry, recorded as an event with an author. Today a hand-written note.
- **Class pack** — lessons bought up front (one, four, or eight) and consumed one at a time when the roll marks the student present. A purchase, never a credit; today sold only for the Adult class (qa.md Q61, answered for Adult; [ADR-0004](./docs/adr/0004-adult-class-packs.md)). _Avoid_: package, punch card, adult credit.
- **Billing mode** — how an enrollment is charged: **monthly tuition** through the billing run, or **class pack**, which the billing run skips.
- **Pack deficit** — a lesson attended with no pack lesson left to consume. Recorded, never blocked at the roll; the next pack sold absorbs it.
- **First-responder discount** — ten percent off for military, police and fire families, stacking with sibling steps and prepay; carries whether ID was verified (qa.md Q101, answered).
- **Billing run** — the month-end process that prices every active enrollment and issues invoices. Runs in three modes: dry run, shadow, committed.
- **Exception** — a household the billing run declines to price without a human look. Replaces the spreadsheet cross-reference.
- **Adjustment** — a deliberate one-off correction to an invoice, with a reason and an author. Kept for real one-offs, once the routine cases become price agreements and credits.
- **Payment request** — a hosted payment link sent to a household (SMS first) carrying an amount the system computed; the family enters its own card and the payment posts back. Office staff never see or type a card (qa.md Q35 Round 3; flow open on the map). _Avoid_: invoice (that is the payer-facing document), phone payment.
- **Billing exemption** — a household the billing run skips on purpose, with a reason from a short list — trade, staff family, courtesy, other — and a note. Today's "do not bill", about twenty households (qa.md Q51, answered). _Avoid_: do not bill.
- **Trade** — lessons exchanged for goods or services, recorded as a payment of method trade with a dollar value and a note (qa.md Q51 answered; Q115 open for the accountant).

## Flags & notes

- **Flag** — typed, structured fact about a student that changes how staff act: allergy, support need, swim-diaper requirement, account handling. Replaces meaning encoded in ALL CAPS names and colour highlights (qa.md Q67, Q68, Q71, answered).
- **Account handling flag** — the office-only "handle with care" flag on a guardian, with a reason note; office screens render the guardian's name in caps when it is set, and instructors and families never see it (qa.md Q71, answered). _Avoid_: difficult parent.
- **Override action** — one of a short set of discretionary actions — adjust a bill by an amount, set a special price, issue or waive a credit, hold a seat, refund or offer a make-up — each recording who and a one-line reason. Discretion is a design requirement, not a gap (Findings §3.2).
- **Audit event** — the record of an override action or a deletion: what, who, when, why. FileMaker's `Audits` table holds only schedule deletions (Findings §2.4).
- **Big-pool readiness** — an instructor-confirmed, dated judgement that a student can stand in the big pool's shallow end and move from the small pool; the system surfaces Level-4 students to assess and never decides (Findings §3.6).
- **Note** — free text about a student or household, with an explicit audience: office-only, instructor-visible, or both.
