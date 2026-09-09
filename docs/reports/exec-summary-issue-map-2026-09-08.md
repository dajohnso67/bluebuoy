# Blue Buoy System Replacement: Executive Summary of the Work Map

Prepared 8 September 2026 for Blue Buoy leadership. Source: the project's work-tracking board as of this morning. Written for non-technical readers.

## 1. Executive TL;DR

The replacement of the FileMaker scheduling, attendance and billing system is in its decision-making phase, and that phase is healthy: every decision the project team could settle on its own has been settled and written down, and three costly wrong assumptions were caught before anything was built. Everything still open now waits on Blue Buoy staff rather than on the project team, with a hard target of training instructors on the new attendance tool during the December 2026 closure and going live when lessons resume in January. The two matters that need leadership attention this week are getting staff time released to answer the outstanding questions, and deciding what to do in the interim about customer card numbers that sit unprotected in the current system.

## 2. Key Business Themes & Impact

### Theme 1. Decision quality is high, and it has already saved money

- Four decisions were opened and closed on 7 September, each with a written rationale and a recorded outcome, so a new team member could pick the project up without re-arguing them.
- The most valuable of these was a correction: the earlier plan assumed Blue Buoy tracks how much charter-school and Regional Center funding each family has left. Billing staff confirmed the business never sees those balances. A feature that would have been built, tested and then ignored was removed before a dollar was spent on it.
- Two more assumptions were corrected the same way: no supporting paperwork is needed to release institutional payments, and early-exit refunds on prepaid plans are recalculated at the rate the family actually earned, not the rate they paid.
- Of the business questions the project keeps a running log of, the current tally is 20 answered, 9 provisional, 11 open. The provisional answers are working assumptions that staff still need to confirm.
- Payment continuity was verified against the processor's own documentation: the cards families already have on file with Authorize.Net will carry over to the new system. No family will be asked to re-enter card details.

### Theme 2. The December deadline now depends on staff availability, not on the project team

- The chosen sequence puts instructor attendance first, because December is the one window with no lessons for two weeks of training, and because it is the worst possible month to touch billing. Billing, scheduling and search follow later.
- The first batch of 17 staff questions is written and ready. Its most urgent section asks for answers within one week of delivery, because those answers decide whether the data move can even start. Whether the batch has actually reached staff is not recorded on the board and could not be verified for this report.
- One question alone blocks all data work: which of two similarly named copies of the FileMaker system is the live one. Nobody has confirmed this yet.
- A sample export from the live system, needed to size and clean the data, has not been produced. The instructions for whoever does it are ready, and they explicitly exclude card numbers and free-text notes.
- The fallback if December slips is safe: instructors keep using the current tool. But slipping would push go-live into the school term, where training time is scarce.

### Theme 3. Money handling stays on the old system well into 2027

- By design, the current system runs the December 2026 annual price change and bulk billing one more time. The new system takes over billing only after that has been observed and never during the summer peak. Leadership should not expect billing on the new system before spring 2027 at the very earliest, and realistically later.
- Institutional billing for the 14 charter schools and 9 Regional Center agencies is the least understood part of the business. Not one real invoice, receivables view or portal walkthrough has been collected yet. The pain point staff describe is slow payment, not non-payment, and the new system cannot help with that until this material is gathered.
- QuickBooks remains the accounting system. The new system will reconcile with it rather than replace it.
- Customer card numbers are stored in readable form in the current system. This is a live exposure under the card-industry security rules (PCI) and a liability if the system were ever breached. The board notes the exposure but contains no item to address it before the billing phase, which cannot start before spring 2027.

### Theme 4. Data quality is an unknown with a known shape

- The current system holds hundreds of thousands of attendance and billing records across roughly 14,000 families and 9,000 students, accumulated over many years. How many are active, duplicated or placeholders is not yet measured.
- Known hazards include placeholder records that every staff search silently skips, instructors identified by first name alone in some records (two instructors sharing a first name could be confused), and student names typed in capitals as an informal signal for a support need. Each of these can produce wrong rosters or wrong bills if carried over naively.
- The new system must find exactly the same records as the old one for the searches staff run every day. Half of that list has been reconstructed from the old system's design; the other half, what staff actually type and save, waits on the same question batch.

## 3. High-Priority Risk Assessment

### Risk 1. Staff response time is now the critical path to December

The project team has done everything it can do without staff input. The next moves require the deck staff, the billing team, ownership and whoever administers the current system to give up a few hours each within one to two weeks. Nobody outside the project team is named on any open item, and no due dates are recorded. If left unaddressed, the December training window is missed by default, instructors go another year on the old tool, and the whole sequence shifts into a busier part of 2027.

### Risk 2. Unprotected card numbers with no interim plan

Full card numbers stored in readable form are a breach-and-fines exposure today, independent of the replacement project. The only remedy on the board is the eventual move of card storage to the payment processor, which arrives with billing in 2027. There is no recorded decision on interim measures such as restricting who can see those fields or purging cards for inactive families. If a breach occurred in the meantime, the consequence would be regulatory penalties, processor sanctions and reputational damage with families.

### Risk 3. One person carries the entire project

Every one of the nine items is assigned to the same individual, who opened and closed four decisions and prepared three handover checklists in a single day. That productivity is a strength, but it means an illness, a holiday or a competing priority stops the project entirely. It also means no one else is positioned to challenge a decision before it becomes expensive.

## 4. Resource & Strategic Recommendations

1. **Release staff time this week, with names and dates.** Assign a named person from each group to the three open handovers: the question batch (deck staff, billing team, office staff), the live-system export (whoever holds full access to the current system) and the institutional billing paperwork (whoever has QuickBooks and portal access). Ask for the urgent question section back by 15 September and the rest by 22 September. Confirm today whether the question batch has actually been delivered; the board does not say.

2. **Put a visible go or no-go date on December.** The project has committed that any slip is a decision someone makes openly, not a drift. Give that decision a date, ideally early October, once the first staff answers and the data export are in hand. If the answers are late, decide then whether to hold December or name the next realistic window, knowing the board identifies no other lesson-free period.

3. **Decide the interim handling of stored card numbers now.** This does not need the new system. Options range from restricting access to those fields, to removing card details for families who have not paid by card in the last year, to accelerating card storage at the processor ahead of the rest of billing. Whichever is chosen, record it as its own item so it stops being a footnote in an export checklist.

4. **Add a second person to the project's decision loop.** Even a few hours a week from someone who reviews decisions and can act on the board reduces the single-person dependency and gives the December commitment a backup owner.

5. **Do not pull effort toward billing early.** The ordering is deliberate and well argued: attendance first is the cheapest test of whether instructors will adopt the new tool, and billing must watch one more year-end run before it can be trusted. Requests to see invoices or payments in the new system before 2027 should be declined.

6. **Plan the payment-processor handover as a dated event.** When the new system gets its own credentials for Authorize.Net, the old system's card processing stops working within a day. That switch must be scheduled for a moment when billing is not running, and the current system's card features must be retired the same day.

## Basis for this report

This summary covers 9 work items (5 open, 4 closed) on the project board, all created on 7 September 2026 and all assigned to one person. No due dates or milestones exist on the board. The question log stands at 20 answered, 9 provisional, 11 open.

| Item | Status | What it settled or still needs |
| --- | --- | --- |
| Overall decision map | Open | The running record of decisions and unknowns |
| Reconciling the question log against staff findings | Closed 7 Sep | 20 questions answered, 3 assumptions corrected, 4 new questions raised |
| Order of delivery | Closed 7 Sep | Attendance first, December 2026 closure, billing after the year-end run |
| Institutional funding model | Closed 7 Sep | No funding-balance tracking; track invoices and receivables instead |
| Payment-card continuity | Closed 7 Sep | Existing stored cards carry over; new credentials disable the old system within a day |
| Staff question batch 1 | Open | Written and ready; delivery to staff not confirmed on the board |
| Live-system data export | Open | Nothing exported yet; instructions ready; needs full-access user |
| Daily staff searches list | Open | Half reconstructed; other half waits on staff answers |
| Institutional billing paperwork | Open | Nothing collected yet; needs QuickBooks and portal access |

Items marked as not verified above reflect gaps in the board itself, not judgments about the people involved.
