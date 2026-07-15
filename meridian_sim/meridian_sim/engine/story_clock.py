"""The story clock: calendar-gated release of pre-generated story events.

Everything a character "does" (emails, PingDesk messages, DriveBox drops) is
pre-generated at enrollment as Story Event rows; this module only flips them
live when their simulation timestamp arrives, and watches for idleness.
"""


def tick():
    """Hourly scheduler entry point (hooks.scheduler_events).

    For every Active Sim Instance:
      1. Release Story Events whose scheduled time has arrived — insert the
         corresponding Sim Email / Sim Chat Message / Sim Document and notify
         the student via socketio.
      2. Run idle detection: no meaningful Action Log entries for N simulation
         days enqueues an in-story escalation (vendor follow-up, Rajan ping,
         eventually an audit notice).

    Safe no-op until the Sim Instance doctype ships — the scheduler must not
    accumulate failures on sites where the app is installed ahead of the
    simulation going live.
    """
    import frappe

    if not frappe.db.table_exists("Sim Instance"):
        return
    # Implemented alongside the Sim Instance doctype.
