# Blue Buoy Migration: Executive Summary of Open Issues

_Prepared 2026-09-10 from the open issues in `dajohnso67/bluebuoy`._

## Executive Snapshot

The Blue Buoy migration is in its decision phase, not yet in build, and the decision work is landing well: seven of the twelve working tickets are closed, with four architecture decisions recorded and the phase order settled around the December 2026 closure. Every remaining open item is waiting on people, not engineering. Five open tickets all need something only staff or office-system owners can supply: answers to a question sheet, a data export from the live FileMaker system, or billing paperwork. Overall risk is moderate and rising with time. The December training window and January go-live are still achievable, but only if the two deadline-critical inputs move this week.

| | Count |
|---|---|
| Working tickets closed | 7 |
| Open, waiting on staff or office access | 5 |
| Open, blocked by another open ticket | 1 (archive decision) |
| Weeks to the December closure | about 12 |

## Primary Operational Roadblocks

**Launch timeline (December training, January go-live)**

- **Staff question sheet not yet delivered.** A 14-question batch is finished and ready to send, but has not gone out. Its first section decides what instructors will see on the pool deck in December: which note abbreviations must be decoded, how attendance is credited, and where the deck has no connectivity.
- **No data has been exported from the live system.** Until a half-day export runs, we do not know real record counts, how many families are genuinely active, or how many instructors share a first name. The import cannot be rehearsed and the first phase cannot be signed off without it.

**Data integrity and migration correctness**

- **Ten-year-idle families sit in a separate archive file that has never been examined.** We must decide whether those families come across as dormant but restorable records or stay only in a frozen read-only copy. That choice is stuck behind the export above.
- **Placeholder records hide in every search.** Dummy schedule rows and pseudo-students exist in the current database, and every staff search silently excludes them. The import must drop or flag them or the new system's counts will be wrong on day one.
- **Card numbers are stored in plain text today.** This is an existing compliance exposure in FileMaker, not a migration defect. The export plan already excludes those fields, and the new system ends the practice by keeping cards only with the payment gateway.

**Staff productivity and customer experience**

- **Search parity is only half measurable.** The new scheduling system must return the same results as FileMaker for every search staff run daily. The system-defined searches are catalogued, and staff volunteered nine more, but each person's personal saved searches are invisible to us. Without staff screenshots, the scheduling phase has no acceptance test.

**Revenue from institutional payers**

- **Charter school and Regional Center billing remains largely undocumented.** Fourteen schools and nine agencies pay for lessons, yet we hold no real invoice, no QuickBooks receivables view, no walkthrough of either school portal, and no list of how each is billed. Progress so far: the Excel sheet the billing team uses to chase agency payments is confirmed and understood.
- **Sensitive material is involved.** Regional Center records reveal a child's disability status. Collection must stay inside the billing channel and out of the shared repository, which the plan already provides for.

## Strategic Resolution Roadmap

**Recommended path: clear the human-dependent inputs in parallel, this month, and protect December.** The engineering side is ready on every ticket. Each item below is a few hours of one person's time.

1. **This week, send the question sheet.** Section A to deck staff and the FileMaker administrator, Section B to the billing team, Section C to office staff. Ask for Section A back within one week and the rest within two. Its return also closes the search-parity gap.
2. **This week, book one export session.** A staff member with full FileMaker access spends about half a day exporting twelve tables plus a small pull from the archive file. The profiling script then produces the headline facts automatically. This unblocks the archive decision and the import rehearsal.
3. **Within two weeks, prepare question batch 2.** It leads with the Adult class no-show policy staff have already asked about, the Christmas make-up rule, and the loose ends on class packs and expiry.
4. **Within four weeks, one office visit for billing paperwork.** One real charter invoice, two QuickBooks screens, two portal walkthroughs, and the payer list. This phase is deliberately sequenced after billing, so it is not December-critical, but it is on the path to full cutover.

**Trade-offs considered**

- **Build now on assumptions instead of waiting for the export.** Saves two to three weeks of calendar time but risks reworking the import and the deck display once real data contradicts the guesses. Not recommended while the export costs half a day.
- **Fold institutional billing into a later release.** Already the plan: the app goes live for attendance in January, billing follows only after one observed December rollover, and institutional invoicing comes last. No further deferral needed.
- **Change the payment gateway at cutover.** Rejected. It would force every family to re-enter a card. Keeping Authorize.Net carries the card vault across untouched.

**Target milestones**

- **September:** question sheet delivered and answered, data export complete, archive decision made.
- **October to November:** attendance app built and tested against real exported data.
- **December 2026 closure:** two-week staff training on the attendance app.
- **January 2027 reopening:** attendance app becomes the system of record, running alongside FileMaker for two to four weeks.
- **2027, outside peak months:** billing shadow-runs until three consecutive months match FileMaker to the cent, then institutional payers, then cutover.
