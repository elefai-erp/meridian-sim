"""The consequence engine: mistakes compound silently and surface weeks later.

Scenario YAML declares the check ("April bank reco unbalanced", "ITC claimed
on ineligible invoice", "RCM liability absent from 3B workings") and when/how
it surfaces. Consequences are data, not code — CA-authored scenarios plug in
without platform changes. Each check maps to one named predicate below.
"""

# Registry of deterministic predicates a scenario's `consequence` may use.
# Each predicate inspects the student's live ERPNext data and returns
# True when the failure condition holds. Implemented with the doctypes.
PREDICATES: dict[str, str] = {
    "bank_reco_unbalanced": "meridian_sim.engine.checks.bank_reco_unbalanced",
    "vendor_ledger_mismatch": "meridian_sim.engine.checks.vendor_ledger_mismatch",
    "suspense_nonzero": "meridian_sim.engine.checks.suspense_nonzero",
    "rcm_liability_missing": "meridian_sim.engine.checks.rcm_liability_missing",
    "tds_deduction_incorrect": "meridian_sim.engine.checks.tds_deduction_incorrect",
    "itc_excess_claimed": "meridian_sim.engine.checks.itc_excess_claimed",
}


def evaluate_due_checks():
    """Daily scheduler entry point (hooks.scheduler_events).

    For every Active Sim Instance, find Consequence Check rows whose
    surface window has opened, run their predicate against live site data,
    and — where the failure condition holds — schedule the surfacing Story
    Event (the vendor email, the auditor query, the employee complaint).

    Safe no-op until the Consequence Check doctype ships — the scheduler must
    not accumulate failures on sites installed ahead of the simulation.
    """
    import frappe

    if not frappe.db.table_exists("Consequence Check"):
        return
    # Implemented alongside the Consequence Check doctype.
