# Project Migration Blueprint: FileMaker Pro to Standard Web Stack

## Context & Objectives
You are acting as a Principal Systems Architect. Create a comprehensive, phase-by-phase migration plan to transition an existing legacy FileMaker Pro application—specializing in complex **calendar scheduling** and **automated billing/invoicing**—to a modern, scalable standard web stack.

### Target Architecture Preferences
-  **Backend Core:** [Golang](https://go.dev/)
-  **Routing & Middleware::** [Chi Router](https://go-chi.io/) or [Echo](https://echo.labstack.com/)
-  **Frontend Interactivity:** htmx + [Alpine.js](https://alpinejs.dev/)
-  **Type-Safe Templating:** [Templ](https://templ.guide/).
-  **Styling & Bundling:** [Tailwind CSS](https://tailwindcss.com/)
-  **Database:** [PostgreSQL](https://www.postgresql.org/)

## Scope Boundaries & Constraints
* Focus strictly on **architecture mapping**, **data schema translation** (converting FileMaker table occurrences, portals, and global fields to normalized Postgres tables), **business logic refactoring** (translating FileMaker script triggers and calculation fields into backend services), and a **phased rollout strategy**.
* Do not write full application code; deliver a structural migration blueprint and execution roadmap.
* Keep responses focused, concise, and structured with clear operational phases. Avoid over-narration or redundant caveats.

## Required Output Deliverables
Provide the plan organized under these exact headings:

1. **Executive Summary & Risk Analysis** (Top 3 migration bottlenecks, such as custom calculation translation or concurrent locking).
2. **Data Schema Mapping** (FileMaker Table Occurrences vs. PostgreSQL normalized relational schema for Customers, Schedules/Appointments, Line Items, and Invoices).
3. **Logic & Script Migration Strategy** (How to transition FileMaker auto-enter calculations, script triggers, and scheduled server scripts into backend cron jobs or event-driven microservices).
4. **API Contract & Integration Outline** (Core REST/GraphQL endpoints required for scheduling conflicts checking and invoice generation).
5. **Phased Execution Roadmap** (Milestones divided into: Phase 1: Data Extraction/DDR Analysis, Phase 2: Core Backend/DB, Phase 3: Scheduler UI, Phase 4: Billing/PDF Generation, Phase 5: Parallel Run & Cutover).
