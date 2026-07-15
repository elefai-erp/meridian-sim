# Meridian Sim — Technical Architecture

**Status:** v2 · **Date:** 2026-07-15
**v2 change:** Per project decision, the platform is built on **Frappe/ERPNext** — we use real, existing open-source software wherever it exists instead of writing new software. Custom code is limited to the simulation layer. Every student-facing tool is a faithful lookalike of the real product it simulates.

---

## 1. Design Principles

1. **Use real software, don't rebuild it.** The ERP the student works in *is* ERPNext. Payroll *is* Frappe HR. The student graduates with hands-on experience in real, employable software — and we maintain zero lines of accounting-engine code.
2. **Every simulated site mocks the original.** TaxPortal mirrors the GST portal's layout and workflow; InboxPro mirrors a Gmail-style client; PingDesk mirrors WhatsApp Web; DriveBox mirrors Google Drive. The student's muscle memory transfers to the real world on day one of a real job.
3. **One custom Frappe app carries the whole simulation.** Story clock, consequence engine, world generation, mock communication tools, appraisal — all live in `meridian_sim`, installed alongside ERPNext.
4. **The simulation is deterministic.** Same seed → same company, same numbers, same consequences. This powers the anti-cheat design and makes scenario testing possible in CI.
5. **Content lives in Git, not in the database.** Scenarios and the Company Bible are YAML/Markdown in this repo; the app loads them. CI validates content before it can merge.
6. **AI is a pluggable adapter, never a hard dependency.** Hosted platform uses Claude; self-hosters can point the adapter at any provider or a local model.

---

## 2. Stack Summary

| Layer | Choice | Why |
|---|---|---|
| Framework | **Frappe Framework v15** (Python) | Battle-tested multi-tenant platform; scheduler, background jobs (RQ), permissions, REST API, and real-time (socketio) built in |
| ERP (LedgerDesk role) | **ERPNext v15** — real, lightly themed | The actual accounting engine: vouchers, ledgers, trial balance, GST-ready Indian COA. Students learn software that appears in real job listings |
| Payroll (PayMate role) | **Frappe HR** — real | Real salary structures, payroll entry, payslips, PF/ESI/PT components |
| Simulation layer | **`meridian_sim`** custom Frappe app | Story clock, consequence engine, worldgen, mock sites, appraisal, AI adapter |
| Mock communication sites | Pages inside `meridian_sim` (Frappe-bundled React/JS per tool) | InboxPro, PingDesk, DriveBox, TaxPortal — lookalike UIs, all reading/writing simulation doctypes |
| Spreadsheet (SheetWork role) | **Univer** (Apache-2.0) embedded | A real open-source spreadsheet engine — we don't build one |
| Database | MariaDB (Frappe standard) | One DB per student site — hard tenant isolation |
| Jobs & scheduling | Frappe scheduler + RQ (Redis) | Story clock ticks, consequence checks, AI appraisal jobs |
| Tenancy | **One Frappe site per student instance** | Full isolation; site backup/restore gives free month-checkpoints and "repeat your weakest month" |
| AI | Adapter module in `meridian_sim` (Anthropic default / OpenAI / Ollama) | Queued jobs; simulation never blocks on AI availability |
| Deployment | frappe_docker-based compose | The standard, well-maintained way to run Frappe stacks |
| CI | GitHub Actions: scenario YAML validation, Python lint, app install test | The scenario validator is the same code the CA form pipeline uses |

### What changed from v1 and what it costs

v1 proposed a Go + PostgreSQL single-binary design optimised for minimal memory. v2 trades some of that for **not building an ERP** — which is the far bigger win: an accounting simulation lives or dies on the correctness of its ledger engine, and ERPNext's is 15+ years mature.

Honest memory numbers: a Frappe bench (MariaDB + 2×Redis + gunicorn workers + scheduler + socketio + nginx) idles around **3–4 GB** and serves hundreds of concurrently active students, because sites share all processes — the marginal cost of a student is **disk, not RAM** (~300–500 MB of MariaDB storage per site). Scaling is horizontal: add benches behind a router, exactly the Frappe Cloud model. This is heavier at the floor than the Go design but equivalently cheap per student at scale.

---

## 3. The Student's World — Tool by Tool

The student logs into one portal ("My Desk") and sees their workday tools. Each opens a full-screen app.

| Tool | Mocks | Implementation |
|---|---|---|
| **LedgerDesk** | Tally/Zoho-class ERP | **Real ERPNext**, themed: Meridian Trading branding, modules trimmed to the accounting surface a Level-2 accountant would have (role-based), all other workspaces hidden |
| **PayMate** | Payroll software | **Real Frappe HR** payroll module, same trimming approach |
| **TaxPortal** | services.gst.gov.in | Lookalike page in `meridian_sim`: same navigation, same filing flow (GSTR-1 → summary → file with EVC), same 2B download experience — backed by simulation doctypes, computing from the student's actual ERPNext data |
| **InboxPro** | Gmail-style webmail | Lookalike page; messages are `Sim Email` documents released by the story clock |
| **PingDesk** | WhatsApp Web | Lookalike page; `Sim Chat Message` documents, real-time via Frappe socketio |
| **DriveBox** | Google Drive | Lookalike page; `Sim Document` records (invoices, statements, notices dropped by characters) |
| **SheetWork** | Excel / Google Sheets | Embedded Univer engine; files stored per instance |

### Lookalike rules (legal + design)

- Mimic **layout, navigation, and workflow** — never logos, emblems, product names, or domains of the real product. TaxPortal carries no national emblem; InboxPro carries no Gmail branding.
- Every mock site shows a persistent, unobtrusive "Training simulation — Meridian Sim" marker.
- Fictional identifiers throughout (GSTIN `36AAECM4712F1Z8`, etc. — see Company Bible).
- This is standard practice for training simulators; the marker + absence of real branding keeps it clearly non-deceptive.

---

## 4. The `meridian_sim` App

```
meridian_sim/
├── hooks.py                  # doc_events (action capture), scheduler_events (story clock)
├── meridian_sim/
│   ├── doctype/
│   │   ├── sim_instance/     # one per student: seed, calendar, state, level
│   │   ├── sim_scenario/     # loaded from scenarios/*.yaml
│   │   ├── sim_email/  sim_chat_message/  sim_document/
│   │   ├── story_event/      # the pre-generated, time-gated release schedule
│   │   ├── consequence_check/# pending checks with surface_week
│   │   ├── action_log/       # every student action, for the appraisal
│   │   └── appraisal_report/
│   ├── worldgen/             # deterministic seed → ERPNext fixtures (COA, parties,
│   │                         #   invoices, seeded errors) + self-check invariants
│   ├── engine/               # story clock, consequence engine, idle detection
│   ├── appraisal/            # evidence collector + 6-dimension scoring
│   └── ai/                   # provider adapter: anthropic / openai / ollama
└── public/  www/             # the mock sites (InboxPro, PingDesk, DriveBox, TaxPortal)
```

### 4.1 World generation

- At enrollment: a new site is created by **restoring a golden template backup** (ERPNext + Frappe HR + meridian_sim + base Meridian Trading setup pre-installed — restore is seconds; fresh install is minutes), then `worldgen` runs with the student's seed to mutate the world: party balances, open invoices, bank lines, and the scenario-declared hidden errors.
- **Invariants enforced before a site is accepted** (see company-bible/opening-balances.md §5): trial balance balances, control accounts tie to schedules, statutory dues consistent, and every intentional imbalance is declared by a scenario — an undeclared imbalance fails generation. This keeps seeded errors distinguishable from generator bugs.
- Golden tests in CI lock determinism: a generator change that silently alters existing worlds fails.

### 4.2 Story clock

- Frappe scheduler (hourly tick per active instance) releases that simulation day's artifacts: emails into InboxPro, PingDesk messages, documents into DriveBox.
- Everything is pre-generated at enrollment as `Story Event` rows; the clock only flips them live. Idle detection (no meaningful actions for N days) enqueues in-story escalations.

### 4.3 Consequence engine

- Scenario YAML declares `trigger`, a deterministic `check` (predicate over the student's actual ERPNext data — e.g., "April bank reco unbalanced", "ITC claimed on ineligible invoice"), `surfaces.week`, and `surfaces.how` (which email/notice fires).
- Week-boundary jobs evaluate pending checks against live site data and schedule the surfacing events. Consequences are **data, not code** — CA-authored scenarios plug in without platform changes.

### 4.4 Action capture & appraisal

- `doc_events` hooks on ERPNext doctypes (Journal Entry, Payment Entry, Purchase/Sales Invoice, Bank Reconciliation…) plus mock-site events (email opened/replied, message read, file viewed, AI conversation submitted) append to `Action Log`.
- The appraisal job walks the log + final books, computes the six dimension scores (Accuracy 25 · Ownership 20 · Responsiveness 15 · Communication 15 · Analytical 15 · AI Usage 10) deterministically where possible, and hands the evidence pack to the AI adapter for the narrative appraisal and examiner interrogation.

---

## 5. Tenancy, Memory & Scale

| Concern | Approach |
|---|---|
| Isolation | One Frappe site (= one MariaDB database) per student instance. No permission-leak risk between students |
| Month checkpoints | Site backup at each month boundary — powers "repeat only your weakest month" for a Below-Expectations appraisal |
| Provisioning | Queued job: restore golden template → run worldgen(seed) → activate. Target < 2 minutes from enrollment |
| Bench capacity | Hundreds of active students per bench (shared workers; per-site RAM ≈ 0, per-site disk 300–500 MB) |
| Horizontal scale | Multiple benches + a routing layer (site-name → bench), the Frappe Cloud pattern. Archive certified instances as compressed backups to object storage |
| Floor cost | One 4 GB VPS runs a full pilot bench. The public marketing site + docs are static and free to serve |

---

## 6. Repository Layout

```
meridian-sim/
├── company-bible/            # The Meridian Trading world (CC BY-SA)
├── scenarios/                # CA-authored scenario YAML by domain (CC BY-SA)
│   └── schema.json           # validated in CI; powers the form auto-merge pipeline
├── meridian_sim/             # the custom Frappe app (AGPL-3.0)
├── contribution-kit/         # scenario template, Rajan voice guide, CA how-to
├── tools/                    # validate_scenarios.py, form→YAML converter
├── deploy/                   # frappe_docker compose overrides, Caddy/nginx notes
├── docs/
└── .github/workflows/
```

ERPNext and Frappe HR are **not vendored** — they're installed on the bench alongside `meridian_sim` (standard Frappe practice), pinned by version in deploy docs.

## 7. Licensing

- `meridian_sim` app + tools: **AGPL-3.0** (compatible with ERPNext's GPL-3.0; consistent with the Frappe ecosystem — Frappe HR and Insights are AGPL)
- Content (company-bible, scenarios, contribution-kit, docs): **CC BY-SA 4.0** — attribution preserves the ICAI signed-off-by chain
- Embedded Univer: Apache-2.0 (compatible)
- DCO sign-off on commits, no CLA

## 8. Alternatives Considered

| Option | Verdict |
|---|---|
| **v1: Go + PostgreSQL single binary, custom mock ERP** | Lightest possible footprint (<700 MB), but requires building and forever maintaining a correct double-entry/GST/payroll engine — the highest-risk component of the whole platform. Superseded by decision to use real ERPNext |
| **ERPNext multi-company on one shared site** (one Company per student instead of one site) | Cheaper provisioning and disk, but tenant isolation rests entirely on permission configuration — one mistake leaks another student's books. Site-per-student is the safe default; revisit only if disk economics demand it |
| **Custom-built spreadsheet for SheetWork** | Rejected — Univer exists and is Apache-2.0 |
| **Standalone mock GST portal as a separate service** | Rejected — it must read the student's live ERPNext data anyway; a page inside `meridian_sim` is simpler and stays in one deployment unit |
