# Deploying Meridian Sim

Meridian Sim deploys as a standard Frappe bench — we use
[frappe_docker](https://github.com/frappe/frappe_docker), the officially
maintained containerised setup, rather than shipping our own compose stack.

## Apps on the bench

| App | Source | Role |
|---|---|---|
| frappe | v15 | framework |
| erpnext | v15 | the student's ERP ("LedgerDesk") |
| hrms | v15 | payroll ("PayMate") |
| meridian_sim | this repo | the simulation layer |

Build a custom image with the standard frappe_docker `apps.json` mechanism:

```json
[
  { "url": "https://github.com/frappe/erpnext",  "branch": "version-15" },
  { "url": "https://github.com/frappe/hrms",     "branch": "version-15" },
  { "url": "https://github.com/<org>/meridian-sim", "branch": "main" }
]
```

> Note: `bench get-app` from this monorepo picks up the app at `meridian_sim/`.

## Site topology

- **One Frappe site per student instance.** Provisioning restores a golden
  template backup (all apps installed + base Meridian Trading world), then
  runs `worldgen` with the student's seed. Target under 2 minutes end to end.
- **Golden template site** (`template.internal`): kept pristine; re-backed-up
  whenever the base world or app versions change.
- **Month checkpoints:** site backup at each simulation month boundary —
  powers "repeat only your weakest month".
- **Archival:** certified instances are backed up to object storage and
  dropped from the bench.

## Sizing

A single 4 GB / 2 vCPU VPS runs a pilot bench (MariaDB, 2×Redis, gunicorn
workers, scheduler, socketio, nginx) serving hundreds of active students —
per-site cost is disk (~300–500 MB), not RAM. Scale horizontally by adding
benches and routing site names to benches (the Frappe Cloud pattern).

## Configuration

Per-site AI settings (see `meridian_sim/ai/adapter.py`):

```bash
bench --site <site> set-config ai_provider anthropic
bench --site <site> set-config anthropic_api_key sk-ant-...
bench --site <site> set-config ai_model claude-sonnet-5
```

Scheduler must be enabled on every student site (`bench --site <site>
enable-scheduler`) — the story clock and consequence engine run on it.
