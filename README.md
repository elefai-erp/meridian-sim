# Meridian Sim

**An accounting simulation training platform. Not a course — a parallel reality job.**

Meridian Sim is an open-source, CA-community-driven platform where a student spends 3 immersive months as the accountant of a fictional company — **Meridian Trading Pvt Ltd** — working daily with mock versions of real accounting software, responding to emails and chat messages from virtual colleagues, and living with the consequences of every decision they make.

The student does not know what is being tested. They just come to work every day.

## What makes it different

- **Procedurally generated company** — every student gets unique numbers; no shared answer key exists
- **Calendar-gated story** — time and process determine progress, not scores
- **Consequences compound silently** — a wrong entry in Week 2 surfaces as a failed bank reco in Week 6, exactly like real work
- **A vague, occasionally-wrong virtual boss** (Rajan Mehta) whose advice must be verified, not followed blindly
- **AI usage is mandatory but graded** — the quality of the questions a student asks matters more than the answers
- **Certification via AI performance appraisal** — six weighted dimensions over the student's actual 3-month record, not MCQs

## Repository layout

| Path | What it is | License |
|---|---|---|
| [`company-bible/`](company-bible/) | The Meridian Trading world — company profile, chart of accounts, opening balances, characters | CC BY-SA 4.0 |
| [`scenarios/`](scenarios/) | CA-authored scenario cards (YAML), organised by domain | CC BY-SA 4.0 |
| [`meridian_sim/`](meridian_sim/) | The custom Frappe app — story clock, consequence engine, world generation, mock sites, AI appraisal | AGPL-3.0 |
| [`contribution-kit/`](contribution-kit/) | Everything a CA contributor needs — templates, Rajan's voice guide, how-to | CC BY-SA 4.0 |
| [`tools/`](tools/) | Offline scripts — scenario validation, form conversion | AGPL-3.0 |
| [`deploy/`](deploy/) | frappe_docker-based deployment notes | AGPL-3.0 |
| [`docs/`](docs/) | Architecture and design documents | CC BY-SA 4.0 |

## The stack — real software, not rebuilt software

The ERP the student works in **is real ERPNext** (themed as "LedgerDesk"); payroll **is real Frappe HR** ("PayMate"). Students graduate with hands-on experience in software that appears in actual job listings. The other workplace tools are faithful lookalikes of the products they simulate — TaxPortal mirrors the GST portal's filing flow, InboxPro a Gmail-style client, PingDesk a WhatsApp-style chat, DriveBox a Drive-style file store — built inside the `meridian_sim` app, with a persistent "training simulation" marker and no real-world branding. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Quick start (development)

On a Frappe v15 bench with ERPNext and Frappe HR installed:

```bash
bench get-app https://github.com/<org>/meridian-sim   # app lives in meridian_sim/
bench --site <site> install-app meridian_sim

# Validate scenario files (no bench needed)
python3 tools/validate_scenarios.py

# Pure simulation-core tests (no bench needed)
cd meridian_sim && PYTHONPATH=. python3 -m unittest discover -s meridian_sim/tests
```

Each student instance is its own Frappe site, provisioned by restoring a golden template and mutating it with the student's unique seed — see the architecture doc for tenancy, checkpoints, and scaling.

## Contributing

There are two very different ways to contribute:

- **Chartered Accountants / finance professionals** — you write scenarios, and you never need to touch Git. Start with [`contribution-kit/how-to-contribute.md`](contribution-kit/how-to-contribute.md).
- **Developers** — the platform is a Go + PostgreSQL + React modular monolith. Start with [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

Every scenario in production is authored and reviewed by named professionals with ICAI/ICMAI membership numbers. That accountability chain is what makes the certification credible.

## License

- Platform code: [AGPL-3.0](LICENSE)
- Content (company bible, scenarios, contribution kit, docs): [CC BY-SA 4.0](company-bible/LICENSE)
