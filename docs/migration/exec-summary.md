# Blue Buoy Migration: Executive Summary of Open Issues

_Prepared 2026-09-16 from the open issues in `dajohnso67/bluebuoy`._

## Executive Snapshot

The Blue Buoy migration is still in its decision phase, and this week removed its biggest unknown: the live FileMaker data was exported and profiled, and the notes and staff answers gathered during that export are now folded into the plan. Nine of the eighteen working tickets are closed, with four architecture decisions recorded and the phase order settled around the December 2026 closure. The export answered the questions it was meant to and raised three new ones: about 5,600 students in the billing history no longer exist in the live file, the make-up credit balances FileMaker shows staff are wrong for roughly three in four students who have any, and the adult class balances staff manage by hand are recorded nowhere. Ownership also settled how phone payments will work without staff ever handling a card. Overall risk is moderate and rising with time. December training and January go-live remain achievable, but the staff question sheet has now been ready and undelivered for nine days.

| | Count |
|---|---|
| Working tickets closed | 9 |
| Open, waiting on staff or office access | 4 |
| Open, ready for a decision now | 2 |
| Open, research under way | 1 |
| Open, blocked by another open ticket | 2 (archive decision, payment-request flow) |
| Weeks to the December closure | about 11 |

## Primary Operational Roadblocks

**Launch timeline (December training, January go-live)**

- **Staff question sheet still not delivered.** The 14-question batch has been ready since 7 September. Its first section decides what instructors see on the pool deck in December: which note abbreviations must be decoded, how attendance is credited, and where the deck has no connectivity. Two of its questions were settled informally during the export session, but the deck section is untouched.
- **A third of the schedule is not lessons.** Of 127,700 schedule rows, 42,700 carry no lesson type, 9,600 are instructor breaks and 46 are placeholders. Ownership has described the two things they want kept apart, a temporarily held seat and an instructor's blocked time, and both are now in the plan. What each legacy row becomes is a short decision that is ready to take.

**Data integrity and migration correctness**

- **The archive file is now a money question, not a housekeeping one.** About 5,600 students referenced by 215,000 billing rows, 1,400 of them carrying real payments, are absent from the live file. The ten-year-idle archive is the only place they can be. A one-hour pull of two tables from that file tells us how many it actually holds; that pull is the only thing still blocking the archive decision.
- **Make-up credit balances cannot be trusted as they stand.** FileMaker stores each student's balance as a number it recalculates only when a trigger fires. Replaying its own formula from the underlying records reproduces the stored balance for just 14 to 31 percent of students with any credits. The new system will rebuild balances from the records, so ownership must decide which number is the truth at go-live and what families and staff are told when a balance changes. This is a trust decision, not a technical one.
- **Adult class balances exist only in staff's heads.** The one field that was thought to hold them is empty on every row. Every adult enrollment will land on a review list at import for the office to confirm the remaining lessons. Small in number, but it needs staff time, not engineering time.

**Card handling and payments**

- **The card leak is a process problem, and the fix is chosen.** Every card already lives with the payment gateway, and the export found exactly one full card number written in a note. The remaining leak is that phone payments get written down because only two people can reach the gateway. Ownership has decided the office will send the family a payment link by text with the amount already computed, so no staff member handles a card and no amount is typed by hand. Which gateway product provides the link is being researched now; the flow around it is the next decision.
- **Cleaning up the old card data is not part of this project.** Replacing stored card numbers in FileMaker, restricting who can see the fields, and clearing old export copies are operations on the system being replaced. They can start at once, and the one thing the migration asks is that the frozen copy of FileMaker taken at cutover is made after that clean-up.

**Staff productivity and customer experience**

- **Search parity is only half measurable.** The new scheduling system must return the same results as FileMaker for every search staff run daily. The system-defined searches are catalogued and staff volunteered nine more, but each person's personal saved searches are invisible to us. Without staff screenshots, the scheduling phase has no acceptance test.
- **Make-up offers will hold slots for hours, not days.** Staff corrected an earlier assumption: every slot held against an unanswered offer blocks another family, so the new system offers one or two options with a short window. Whether an expired offer moves on automatically, and whether the family is told, are questions for the next staff batch.

**Revenue from institutional payers**

- **Charter school and Regional Center billing remains largely undocumented.** Fourteen schools and nine agencies pay for lessons, yet we hold no real invoice, no QuickBooks receivables view, no walkthrough of either school portal, and no list of how each is billed. The Excel sheet the billing team uses to chase agency payments is confirmed and understood.
- **Sensitive material is involved.** Regional Center records reveal a child's disability status. Collection must stay inside the billing channel and out of the shared repository, which the plan already provides for.

## Strategic Resolution Roadmap

**Recommended path: deliver the question sheet now, finish the one small pull, and hold one decision session with ownership on balances.** The engineering side is ready on every ticket, and the export has turned the largest risks into specific, answerable questions.

1. **This week, send the question sheet.** Section A to deck staff and the FileMaker administrator, Section B to the billing team, Section C to office staff. Ask for Section A back within one week and the rest within two. Its return also closes the search-parity gap.
2. **This week, one more hour in FileMaker.** Export the six-row closure calendar table and the family and student tables from the archive file, this time in a format that does not truncate long notes. That single pull unblocks the archive decision and tells us where the 5,600 missing students went.
3. **Within two weeks, a decision session on make-up balances and legacy schedule rows.** Ownership chooses whether go-live balances come from FileMaker's displayed numbers or from the rebuilt ledger, who reviews the differences, and how families are told; and confirms what held, break and placeholder rows become at import. This feeds question batch 2, which also carries the Adult no-show policy, the Christmas make-up rule, and the offer and closure questions raised this week.
4. **Within two weeks, settle the payment-link flow.** Once the gateway research lands, ownership confirms who may create and send a payment request and whether billing reviews it first.
5. **Within four weeks, one office visit for billing paperwork.** One real charter invoice, two QuickBooks screens, two portal walkthroughs, and the payer list. Not December-critical, but on the path to full cutover.

**Trade-offs considered**

- **Carry FileMaker's displayed make-up balances across unchanged.** Preserves what staff and families have been told, but bakes several thousand known-wrong numbers into the new ledger as if they were audited. Recommended only as an opening adjustment with the difference recorded, never as the silent truth.
- **Start the import rehearsal before the archive pull.** Reasonable: the live data is enough to build against, and the archive changes only how the missing students are handled. The pull is an hour of one person's time, so the rehearsal should not wait long.
- **Change the payment gateway at cutover.** Rejected. It would force every family to re-enter a card. Keeping Authorize.Net carries the card vault across untouched, and the payment-link design rides the same gateway.

**Target milestones**

- **September:** question sheet delivered and answered, remaining exports pulled, archive decision made, payment-link flow settled.
- **October to November:** attendance app built and tested against the real exported data.
- **December 2026 closure:** two-week staff training on the attendance app.
- **January 2027 reopening:** attendance app becomes the system of record, running alongside FileMaker for two to four weeks.
- **2027, outside peak months:** billing shadow-runs until three consecutive months match FileMaker to the cent, then institutional payers, then cutover.
