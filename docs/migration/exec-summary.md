# Blue Buoy Migration: Executive Summary of Open Issues

_Prepared 2026-09-16 from the open issues in `dajohnso67/bluebuoy`._

## Executive Snapshot

The Blue Buoy migration is still in its decision phase, and the biggest unknown has just been removed: the live FileMaker data was exported and profiled this week, so the plan now rests on measured facts rather than estimates. Eight of the sixteen working tickets are closed, with four architecture decisions recorded and the phase order settled around the December 2026 closure. The export answered the questions it was meant to and raised three new ones: about 5,600 students in the billing history no longer exist in the live file, the make-up credit balances FileMaker shows staff are wrong for roughly three in four students who have any, and the adult class balances staff manage by hand are recorded nowhere. Overall risk is moderate and rising with time. December training and January go-live remain achievable, but the staff question sheet has now been ready and undelivered for nine days.

| | Count |
|---|---|
| Working tickets closed | 8 |
| Open, waiting on staff or office access | 4 |
| Open, ready for a decision or desk work now | 2 |
| Open, blocked by another open ticket | 2 (archive decision, schedule-row rules) |
| Weeks to the December closure | about 11 |

## Primary Operational Roadblocks

**Launch timeline (December training, January go-live)**

- **Staff question sheet still not delivered.** The 14-question batch has been ready since 7 September. Its first section decides what instructors see on the pool deck in December: which note abbreviations must be decoded, how attendance is credited, and where the deck has no connectivity. A few of its questions were answered informally during the export session and will be transcribed, but the deck section is untouched.
- **A third of the schedule is not lessons.** The export shows that of 127,700 schedule rows, 42,700 carry no lesson type, 9,600 are instructor breaks and 46 are placeholders. The import must know what each becomes before the first phase can be signed off. Ownership has already described the two things they want kept apart, a temporarily held seat and an instructor's blocked time, so this is a short decision once the September findings are folded into the plan.

**Data integrity and migration correctness**

- **The archive file is now a money question, not a housekeeping one.** About 5,600 students referenced by 215,000 billing rows, 1,400 of them carrying real payments, are absent from the live file. The ten-year-idle archive is the only place they can be. A one-hour pull of two tables from that file tells us how many it actually holds; that pull is the only thing still blocking the archive decision.
- **Make-up credit balances cannot be trusted as they stand.** FileMaker stores each student's balance as a number it recalculates only when a trigger fires. Replaying its own formula from the underlying records reproduces the stored balance for just 14 to 31 percent of students with any credits. The new system will rebuild balances from the records, so ownership must decide which number is the truth at go-live and what families and staff are told when a balance changes. This is a trust decision, not a technical one.
- **Adult class balances exist only in staff's heads.** The one field that was thought to hold them is empty on every row. Every adult enrollment will land on a review list at import for the office to confirm the remaining lessons. Small in number, but it needs staff time, not engineering time.
- **Card exposure is narrower than feared, but the leak is ongoing.** Every card lives with the payment gateway already, and the export found exactly one full card number written in a note. The remaining problem is process: when a family pays by phone, staff have to write the card down because only two people can reach the gateway. Ownership has chosen the fix, sending the family a payment link so no staff member handles a card, and the new system is being designed around it.

**Staff productivity and customer experience**

- **Search parity is only half measurable.** The new scheduling system must return the same results as FileMaker for every search staff run daily. The system-defined searches are catalogued and staff volunteered nine more, but each person's personal saved searches are invisible to us. Without staff screenshots, the scheduling phase has no acceptance test.

**Revenue from institutional payers**

- **Charter school and Regional Center billing remains largely undocumented.** Fourteen schools and nine agencies pay for lessons, yet we hold no real invoice, no QuickBooks receivables view, no walkthrough of either school portal, and no list of how each is billed. The Excel sheet the billing team uses to chase agency payments is confirmed and understood.
- **Sensitive material is involved.** Regional Center records reveal a child's disability status. Collection must stay inside the billing channel and out of the shared repository, which the plan already provides for.

## Strategic Resolution Roadmap

**Recommended path: deliver the question sheet now, finish the two small pulls, and hold one decision session with ownership on balances.** The engineering side is ready on every ticket, and the export has turned the largest risks into specific, answerable questions.

1. **This week, send the question sheet.** Section A to deck staff and the FileMaker administrator, Section B to the billing team, Section C to office staff. Ask for Section A back within one week and the rest within two. Its return also closes the search-parity gap.
2. **This week, one more hour in FileMaker.** Export the six-row closure calendar table and the family and student tables from the archive file, this time in a format that does not truncate long notes. That single pull unblocks the archive decision and tells us where the 5,600 missing students went.
3. **This week, fold in the September findings.** The export session produced corrections to the business context and a third round of staff answers on names, cards, invoicing, held seats, trades and enrollment holds. Desk work for the engineering side; it also unblocks the schedule-row decision.
4. **Within two weeks, a decision session on make-up balances.** Ownership chooses whether go-live balances come from FileMaker's displayed numbers or from the rebuilt ledger, who reviews the differences, and how families are told. This feeds question batch 2, which also carries the Adult no-show policy and the Christmas make-up rule.
5. **Within four weeks, one office visit for billing paperwork.** One real charter invoice, two QuickBooks screens, two portal walkthroughs, and the payer list. Not December-critical, but on the path to full cutover.

**Trade-offs considered**

- **Carry FileMaker's displayed make-up balances across unchanged.** Preserves what staff and families have been told, but bakes several thousand known-wrong numbers into the new ledger as if they were audited. Recommended only as an opening adjustment with the difference recorded, never as the silent truth.
- **Start the import rehearsal before the archive pull.** Reasonable: the live data is enough to build against, and the archive changes only how the missing students are handled. The pull is an hour of one person's time, so the rehearsal should not wait long.
- **Change the payment gateway at cutover.** Rejected. It would force every family to re-enter a card. Keeping Authorize.Net carries the card vault across untouched.

**Target milestones**

- **September:** question sheet delivered and answered, remaining exports pulled, September findings folded in, archive decision made.
- **October to November:** attendance app built and tested against the real exported data.
- **December 2026 closure:** two-week staff training on the attendance app.
- **January 2027 reopening:** attendance app becomes the system of record, running alongside FileMaker for two to four weeks.
- **2027, outside peak months:** billing shadow-runs until three consecutive months match FileMaker to the cent, then institutional payers, then cutover.
