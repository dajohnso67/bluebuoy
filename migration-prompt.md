# Blue Buoy Migration — Master Prompt

The working prompt for any agent or engineer executing this migration. It carries the mission, the file map, and the rules that hold everywhere; every fact about the stack, the business, and the legacy system lives in the support files it points at. Supersedes [`technical-prompt.md`](./technical-prompt.md), the original planning brief that produced `docs/migration/PLAN.md`.

## Mission

You are the principal engineer replacing Blue Buoy Swim School's FileMaker system — scheduling, billing, attendance, roughly twenty years of accumulated logic — with a modern web application:

| Layer | Choice |
| --- | --- |
| Backend | [Go](https://go.dev/) + [Chi](https://go-chi.io/) |
| Templating | [Templ](https://templ.guide/) (type-safe, server-rendered) |
| Interactivity | [htmx](https://htmx.org/) + [Alpine.js](https://alpinejs.dev/) |
| Styling | [Tailwind CSS](https://tailwindcss.com/) |
| Database | [PostgreSQL](https://www.postgresql.org/) |

Two surfaces, no GraphQL: the application's own screens are Templ fragments served straight from Chi handlers; a small JSON API serves the one client that genuinely needs data rather than markup — the offline-capable pool-deck iPad (`PLAN.md` §4).

The migration's substance is not porting features. FileMaker handles the routine cases and hands the rest to staff; the job is absorbing that manual layer — month-end hand-corrections, an institutional billing business that never touched the database, meaning encoded in typography — into a system that carries it (`PLAN.md` §1).

## Support files

### Authority — architecture and decisions

| File | What it is | Read it before |
| --- | --- | --- |
| [`docs/migration/PLAN.md`](./docs/migration/PLAN.md) | The migration blueprint: risk analysis, FileMaker-construct → Postgres mapping, core schema, domain events, cron jobs, API surface, phase gates. Source of truth for architecture. | Proposing any schema, endpoint, job, or phase work |
| [`docs/migration/open-questions.md`](./docs/migration/open-questions.md) | The decision register: every decision waiting on a staff answer, its working assumption, its state (`open` / `assumed` / `answered`), and the phase it blocks. | Building anything that prices, enforces a rule, or migrates data |
| [`CONTEXT.md`](./CONTEXT.md) | The domain glossary — household, slot, enrollment, lesson, payer, authorization, price agreement, credit ledger, billing run, flag. | Naming any domain concept in a table, endpoint, issue title, or test |
| [`docs/adr/`](./docs/adr/) | Architecture decision records. Created lazily as decisions land; proceed silently if absent. | Working in an area an ADR touches; contradicting one means surfacing it, never silently overriding |

### Business and domain truth

| File | What it is | Read it before |
| --- | --- | --- |
| [`resources/BlueBuoy_Complete_Context_Package.md`](./resources/BlueBuoy_Complete_Context_Package.md) | The deepest domain document, assembled from DDR analysis, live screenshots, ownership conversations, and an answered staff questionnaire. Technical appendix (verbatim billing calculations, verified join predicates, lesson-type codes, naming conventions, data landmines), Part A product requirements with staff answers folded in, Part B an alternative rollout plan, Part C its own questionnaire draft. Every claim carries a confidence label: **Confirmed / Reported / Inferred / Open**. | Designing any workflow, rule, or migration step; writing any code that touches legacy data |
| [`qa.md`](./qa.md) | The current staff discovery questionnaire — source of truth for question texts. `PLAN.md` and the register cite its numbering. | Citing a question, or preparing anything for staff review |
| [`qa1-1.md`](./qa1-1.md) | The earlier questionnaire draft. `qa.md` = `qa1-1.md` + 17 from Q24 on. | Interpreting any answer or citation traceable to the earlier draft |

The package's own instruction: its **business findings are the valuable part**; its architecture recommendations are the weakest part and defer to `PLAN.md`.

### Ground truth — the legacy system itself

`resources/DDR/` holds the FileMaker Database Design Report exports, the raw material every schema claim can be checked against:

| File | Contents |
| --- | --- |
| `BlueBuoy_FM_fmp12.xml` (~40 MB) | The main file: 22 base tables, 341 table occurrences, 316 relationships, 340 scripts, 70 layouts |
| `Instructor_Entry_fmp12.xml` (~11 MB) | The pool-deck iPad app — 1 base table of its own, 163 scripts |
| `20 Time_fmp12.xml` (~2 MB) | Legacy roll sheets |
| `Summary.xml`, `instructorentrySummary.xml` | Object counts per file |

They are UTF-16-encoded XML and too large to load whole: search for the object you need, then read the matched region. Facts the DDR cannot yield (record date ranges, name collisions, dual-key disagreements) are listed under the package's *Data profiling still needed* and require a CSV export from the live system.

### Workflow

| File | Governs |
| --- | --- |
| [`CLAUDE.md`](./CLAUDE.md) | Session instructions for agents working in this repo |
| [`docs/agents/issue-tracker.md`](./docs/agents/issue-tracker.md) | Issues live as GitHub issues in `dajohnso67/bluebuoy`, via the `gh` CLI |
| [`docs/agents/triage-labels.md`](./docs/agents/triage-labels.md) | The five canonical triage labels |
| [`docs/agents/domain.md`](./docs/agents/domain.md) | How to consume `CONTEXT.md` and ADRs while exploring |

### Historical

`technical-prompt.md` (root) and `resources/tech-promt.md` are identical copies of the original planning brief — superseded, kept because `PLAN.md` cites them. `docs/migration/bluebuoy-blueprint.html` is the stakeholder-facing rendering of `PLAN.md`; every `PLAN.md` edit re-renders it in the same change.

## Precedence

When sources disagree, authority runs:

1. **The DDR** on what FileMaker *is* — schema, calculations, scripts, relationships.
2. **The context package** on how the business *operates*, weighted by its confidence labels — a **Confirmed** finding outranks any assumption elsewhere; an **Inferred** one is a hypothesis.
3. **`PLAN.md`** on architecture — schema shape, invariants, API surface, gates.
4. **The register** on decision state — but see the hazard below: it predates the package.

A conflict between sources is a finding: surface it to the user with a recommendation, record the resolution (register row, `PLAN.md` edit, or ADR), and build on the resolution — never silently pick a side.

## Known hazards

These are live inconsistencies in the corpus, not hypotheticals:

- **The register is stale.** `PLAN.md` and `open-questions.md` were written when every `qa.md` answer was blank. The context package arrived later with staff answers folded into Part A, and some contradict recorded assumptions — for example, the package records charter-school authorization tracking as a corrected over-design, while `PLAN.md` §2 still models `authorization` consumption against a cap. Trust neither side until the sweep below reconciles them.
- **Three question-numbering schemes.** `qa.md` (current), `qa1-1.md` (offset −17 from Q24 on), and the package's Part C (its own numbering — the shift-start PIN is Q87 there and Q83 in `qa.md`). A bare "Q41" is ambiguous; every citation carries its document.
- **Two phase orderings — resolved 2026-09-07.** Attendance-first won, recorded as [ADR-0001](./docs/adr/0001-attendance-first-sequencing.md); `PLAN.md` §5 now carries the named phases (Foundations → Attendance → Scheduling & search → Billing → Institutional payers → Cutover), and bare phase numbers are retired. A document still citing "Phase 3" predates the ADR — resolve it against the named phases.
- **Every document here has been wrong before.** The package lists its own corrected errors and expects more. Verify a business claim against the DDR or the staff before it becomes schema or code.

## Rules that hold everywhere

1. **The money-path rule.** Build on an `assumed` register row freely; confirm it before it prices anything, enforces anything, or migrates anything irreversibly. An assumption reaching the money path unconfirmed is the project's named failure mode.
2. **Snapshot pricing.** A price is resolved once, by the pricing service, and persisted; nothing monetary recomputes on read. The legacy stamped-rate mechanism (auto-enter calculations frozen at row creation — package technical appendix) is the confirmed root cause of the price-propagation mess; reproduce the snapshot, retire the mechanism.
3. **Decode before normalize.** ALL-CAPS names, colour highlights, and note shorthand (`AUG PO`, `MU`, `$ OCT`) are operational data. The decode pass runs before any import normalizes text — the wrong order destroys the meaning irreversibly, and silently.
4. **Unknowns stay unknown.** Students exist with no level, no age, no payment plan. Import them as null; a default is a fabrication.
5. **Search parity is a gate, not a feature.** Replacing FileMaker's capable ad-hoc find and Saved Finds with a prettier, weaker search is the named capability regression. The Scheduling & search phase's acceptance is set-equality against the enumerated daily searches on the same data.
6. **The card vault stays put.** Authorize.Net CIM carries every stored card across cutover; changing gateways would force re-collecting every card from every family.
7. **The database enforces the two invariants.** Instructor no-overlap (exclusion constraint) and one committed billing run per period (partial unique index) stay constraints — never application discipline (`PLAN.md` §2).
8. **Import is repeatable and non-destructive.** It runs against live exports until it reconciles; pre-created future billing months import as intentions (enrollments), never as invoices.
9. **Rules live as data.** Eligibility bars, discount steps, prepay tiers, closure credit policy land as effective-dated rows a staff member can change, so an answered question is a row, not a deploy.
10. **Docs move together.** An answered question flips its register row, updates the affected `PLAN.md` section, and re-renders the blueprint page in the same change.

## How to work

- Use `CONTEXT.md`'s vocabulary everywhere a domain concept is named; a concept missing from the glossary is either invented language (reconsider) or a real gap (note it for `/domain-modeling`).
- Track work as GitHub issues in `dajohnso67/bluebuoy` per `docs/agents/issue-tracker.md`, labelled per `docs/agents/triage-labels.md`.
- A phase ends on its gate (`PLAN.md` §5), and passing a gate is an observation, not a judgement. Green shadow months — not feature completion — authorize cutover.
- Money correctness is proven by **shadow run**: price closed months in the new system, compare per household to the cent, classify every difference as a bug to fix or a recorded FileMaker error. The run is green when no unexplained difference remains.

## Start here

On a fresh engagement, in order:

1. **Reconciliation sweep** — done 2026-09-07 ([issue #2](https://github.com/dajohnso67/bluebuoy/issues/2)): 20 of 36 register rows flipped to `answered`; three assumptions corrected. The register is the live record.
2. **Settle the sequencing** — done 2026-09-07: [ADR-0001](./docs/adr/0001-attendance-first-sequencing.md), attendance-first targeting the December 2026 closure.
3. **Then build**, phase by phase, gate by gate, per the reconciled `PLAN.md` — once the wayfinder map ([issue #1](https://github.com/dajohnso67/bluebuoy/issues/1)) has no decision blocking the phase's gate.
