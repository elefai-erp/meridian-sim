# Contributing to Meridian Sim

There are two contribution paths. Pick yours.

## Path 1 — CA / Finance professionals (scenario authors)

**You never need Git, GitHub, or YAML.** You write scenarios through a simple web form; everything technical happens automatically behind it.

1. Read [`contribution-kit/how-to-contribute.md`](contribution-kit/how-to-contribute.md)
2. Read the [Company Bible summary](company-bible/meridian-trading.md) so your scenario fits Meridian Trading's world
3. Read [Rajan's voice guide](contribution-kit/rajan-character-guide.md) — every scenario includes his bad advice, and he must sound like Rajan
4. Fill the scenario submission form (link shared in the contributor WhatsApp group)

Your scenario will be reviewed by a Domain Reviewer (a qualified CA/CMA with 5+ years in that domain). Once approved, it goes live with your name and membership number on it.

## Path 2 — Developers

### Stack

Frappe Framework v15 · **real ERPNext** (the student's ERP) · **real Frappe HR** (payroll) · one custom app, [`meridian_sim/`](meridian_sim/), carrying the whole simulation layer. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) first — it explains what we build versus what we deliberately reuse.

### Setup

```bash
# On a Frappe v15 bench with erpnext + hrms installed:
bench get-app /path/to/meridian-sim
bench --site <dev-site> install-app meridian_sim

# Without a bench (content + pure simulation-core work):
python3 tools/validate_scenarios.py
cd meridian_sim && PYTHONPATH=. python3 -m unittest discover -s meridian_sim/tests
```

### Rules of the road

- **Scenario YAML must pass validation**: `python3 tools/validate_scenarios.py` (CI enforces this; it is the same validator that powers the CA form pipeline)
- **The simulation core stays deterministic** — `worldgen` and the consequence predicates are pure (no frappe imports, no I/O) except at the materialization boundary; same seed must always produce the same world. Golden tests enforce this; a change that alters existing worlds must say so loudly in the PR.
- **Don't rebuild what ERPNext/Frappe HR already do.** Accounting and payroll behaviour belong to the real apps; `meridian_sim` orchestrates the story around them.
- **Mock sites mimic layout and workflow only** — never real logos, product names, or emblems, and the "training simulation" marker stays.
- **Sign your commits** with `git commit -s` (DCO). We use sign-offs, not a CLA.

### Content accuracy

Technical accounting content (rates, sections, standards) is owned by Domain Reviewers, not developers. If a code change touches accounting behaviour, tag the relevant domain in the PR.

## Licensing of contributions

- Code contributions are accepted under **AGPL-3.0**
- Content contributions (scenarios, company bible material) are accepted under **CC BY-SA 4.0**

By submitting, you confirm you have the right to contribute the material and accept the DCO.
