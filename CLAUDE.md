# bluebuoy

## Project

Blue Buoy is replacing a legacy FileMaker system (scheduling, billing, attendance) with Go + Chi, Templ, htmx + Alpine.js, Tailwind, and PostgreSQL.

- **Master prompt** — `migration-prompt.md` at the repo root: mission, support-file map, precedence when sources disagree, and the rules that hold everywhere. Start any migration work session there.
- **Migration plan** — architecture, schema mapping, phased roadmap: `docs/migration/PLAN.md`. Read before proposing schema, endpoints, or phase work.
- **Business truth** — `resources/BlueBuoy_Complete_Context_Package.md`: confidence-labelled domain findings, with staff answers folded in; `resources/DDR/` holds the raw FileMaker DDR XML (UTF-16, search rather than load). Newer than the planning docs — see the master prompt's precedence and hazards before trusting either side.
- **Open questions** — the decision each unanswered discovery question blocks: `docs/migration/open-questions.md`. Read before building anything that prices, enforces a rule, or migrates data.
- **`qa.md`** — the staff discovery questionnaire, every answer currently blank. Source of truth for the questions themselves. The earlier draft `qa1-1.md` renumbers everything from Q24 on: `qa.md` = `qa1-1.md` + 17.
- **Blueprint page** — `docs/migration/bluebuoy-blueprint.html`, a stakeholder-facing rendering of `PLAN.md`. `PLAN.md` is the source of truth; changing it means re-rendering this page in the same edit.

## Agent skills

### Issue tracker

Issues live as GitHub issues in `dajohnso67/bluebuoy`, managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical triage roles, each label string equal to its name. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
