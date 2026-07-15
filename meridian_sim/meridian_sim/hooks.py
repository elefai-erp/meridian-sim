app_name = "meridian_sim"
app_title = "Meridian Sim"
app_publisher = "Meridian Sim Contributors"
app_description = (
    "Simulation layer for the Meridian Sim accounting training platform: "
    "story clock, consequence engine, world generation, mock communication "
    "sites, and AI performance appraisal."
)
app_email = "contact@meridian-sim.org"
app_license = "AGPL-3.0"

# The bench must have both installed before this app
required_apps = ["erpnext", "hrms"]

# ---------------------------------------------------------------------------
# Action capture — every student action in the real ERP feeds the Action Log
# that the performance appraisal is computed from. Mock-site actions (email
# opened, message replied, file viewed) log themselves via their own APIs.
# ---------------------------------------------------------------------------
doc_events = {
    doctype: {
        "on_submit": "meridian_sim.engine.action_log.capture",
        "on_cancel": "meridian_sim.engine.action_log.capture",
        "on_update_after_submit": "meridian_sim.engine.action_log.capture",
    }
    for doctype in (
        "Journal Entry",
        "Payment Entry",
        "Purchase Invoice",
        "Sales Invoice",
        "Bank Transaction",
        "Salary Slip",
        "Payroll Entry",
    )
}

# ---------------------------------------------------------------------------
# The story clock and consequence engine run on the Frappe scheduler.
# ---------------------------------------------------------------------------
scheduler_events = {
    "hourly": [
        # Releases the current simulation day's artifacts (emails, chats,
        # documents) for every active instance; runs idle detection.
        "meridian_sim.engine.story_clock.tick",
    ],
    "daily": [
        # Evaluates pending consequence checks whose surface window opened.
        "meridian_sim.engine.consequence.evaluate_due_checks",
    ],
}

# Mock sites (InboxPro, PingDesk, DriveBox, TaxPortal) are served from
# meridian_sim/www/ — see docs/ARCHITECTURE.md §3.
