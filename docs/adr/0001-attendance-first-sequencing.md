# Attendance-first phase sequencing

Status: accepted (2026-09-07 · wayfinder ticket [#3](https://github.com/dajohnso67/bluebuoy/issues/3))

The corpus carried two phase orderings: `PLAN.md` §5's backend-first (extraction → core backend → scheduler UI → billing → parallel run) and the context package Part B's attendance-first, targeting the December closure. We chose **attendance-first**: foundations narrowed to what attendance needs, the attendance app trained and cut over during the December 2026 closure with go-live at the January reopening, then scheduling and search, then billing, then institutional payers.

Why: December is a hard deadline for the stakeholders, and it is *confirmed* (package 3.6, 2.8) as the most billing-intensive moment of the year — annual rate change, prepay-at-old-rate sales, bulk next-year generation — so it is the best possible window for attendance (no lessons run, staff can train) and the worst possible one for billing. Attendance-first also fronts the cheapest trust test the project has: if instructors don't prefer the new app, that gets fixed before anything with money in it is built. The fallback is safe — `Launcher_Teacher` stays fully operational.

## Decisions folded in

- **The December commitment** is *readiness at the closure*: staff train during the two weeks of no lessons; the app is system of record when lessons resume in January, with a 2–4 week parallel run against FileMaker reconciling attendance nightly. Shipping before the closure was rejected (costs three build weeks for a riskier parallel run); treating the date as soft was rejected outright — slippage is a decision someone makes visibly, not drift.
- **The December slice is strict** (package Part B Phase 1 scope): roster view, present/absent, backfill of a prior day, free instructor switching, profile-note *indicator* with the read-only two-channel notes display, swim-diaper badge, offline caching of the full day's schedule for all instructors, PIN at shift start. Explicitly excluded: make-up issuance, scheduling changes, waitlist, and any billing visibility. Deck-manager tools land in the scheduling phase.
- **Billing's slot is defined by two constraints, not a date**: it cuts over only after one more annual rollover has been observed running in FileMaker (December 2026's), and never in a peak month (summer's confirmed 10–12-hour runs). The shadow-run gate — green months to the cent — remains the real authorization.
- **Phases get names, and bare phase numbers are retired.** `PLAN.md` and Part B numbered their phases incompatibly (PLAN's "Phase 1" was extraction; Part B's was attendance) — the same ambiguity as the three questionnaire numbering schemes. The named phases are **Foundations → Attendance → Scheduling & search → Billing → Institutional payers → Cutover**, and every document cites them by name.

## Consequences

- `PLAN.md` §5 is rewritten to the named phases, keeping its gate discipline; the register's section headers cite phase names.
- Staff question batch 1 front-loads what gates Foundations and Attendance — above all the live-file identity question (`BlueBuoy_FM` vs `BlueBuoy_FM_2024`), which blocks any import.
- The decode pass narrows for December to the deck-visible conventions (ALL-CAPS student names → support-need flag; under-4 diaper badge); the full decode still gates the wider import.
- FileMaker performs the December 2026 rollover and remains the billing system of record until the Billing phase's shadow runs go green.
