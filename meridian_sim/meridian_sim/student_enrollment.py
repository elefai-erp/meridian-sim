"""Student enrollment, triggered when a Student Application is set to Enrolled.

Creates (idempotently) a desk (System User) login with the "Meridian Student" role plus
LedgerDesk roles,
an Active Week-1 Sim Instance (demo story content) linked back to the application, and emails the student
a set-password link plus the sign-in URL. No plaintext password is ever sent.

The instance is seeded with the shared demo story (demo.setup_demo) as a
stopgap: per-student world generation isn't built yet, so all students see
the same Week-1 content and, via LedgerDesk, the shared Meridian Trading books.

If email can't be queued, a ToDo goes to the System Managers so the link can
be relayed by hand (same fallback model as notify.py).
"""

import frappe
from frappe.utils import get_url

from meridian_sim.notify import notify_reviewers

ROLE = "Meridian Student"
# Desk roles so LedgerDesk (/app) opens. Not Accounts Manager: students must not
# cancel/reverse other people's entries. Books are shared until per-student sites exist.
DESK_ROLES = ("Accounts User", "Sales User", "Purchase User")


def _ensure_role():
    if not frappe.db.exists("Role", ROLE):
        frappe.get_doc({"doctype": "Role", "role_name": ROLE, "desk_access": 0}).insert(
            ignore_permissions=True
        )


def _ensure_user(app):
    email = (app.email or "").strip().lower()
    if frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
    else:
        parts = (app.full_name or "Student").strip().split(" ", 1)
        user = frappe.get_doc({
            "doctype": "User", "email": email, "first_name": parts[0],
            "last_name": parts[1] if len(parts) > 1 else "",
            "mobile_no": app.phone or None,
            "send_welcome_email": 0, "user_type": "System User",
        }).insert(ignore_permissions=True)
    have = {r.role for r in user.roles}
    missing = [r for r in (ROLE, *DESK_ROLES) if r not in have]
    for r in missing:
        user.append("roles", {"role": r})
    if missing or user.user_type != "System User":
        user.user_type = "System User"
        user.save(ignore_permissions=True)
    return user


def enroll(app_name: str):
    """Idempotent. Safe to call twice: the linked_instance guard stops repeats."""
    app = frappe.get_doc("Student Application", app_name)
    if app.status != "Enrolled" or app.linked_instance:
        return
    if not app.email:
        notify_reviewers("Student Application", app.name,
                         f"{app.full_name} was enrolled but has no email — contact them by phone: {app.phone}.",
                         "High")
        return

    _ensure_role()
    user = _ensure_user(app)

    instance = frappe.db.get_value("Sim Instance", {"student": user.name, "status": ["!=", "Completed"]})
    if not instance:
        # Active Week-1 instance with the story content (inbox, chats, drive
        # documents). Stopgap until per-student world generation exists.
        from meridian_sim.demo import setup_demo

        setup_demo(user.name)
        instance = frappe.db.get_value("Sim Instance", {"student": user.name, "status": "Active"})
    app.db_set("linked_instance", instance, notify=False)

    link = user._reset_password(send_email=False)
    try:
        frappe.sendmail(
            recipients=[user.name],
            subject="You're enrolled — Knowledge Bridge Academy",
            message=(
                f"<p>Hi {user.first_name},</p>"
                "<p>Congratulations — your application to Knowledge Bridge Academy "
                "(Meridian Sim) has been approved.</p>"
                f"<p>Set your password and sign in here:<br><a href=\"{link}\">{link}</a></p>"
                f"<p>After that, sign in any time at <a href=\"{get_url('/login')}\">{get_url('/login')}</a>. "
                "Your username is this email address.</p>"
                "<p>The link can be used once, so set your password soon. "
                "We'll contact you when your simulation is ready to start.</p>"
                "<p>— Knowledge Bridge Academy</p>"
            ),
            reference_doctype="Student Application", reference_name=app.name,
        )
    except Exception:  # noqa: BLE001 - any mail failure falls back to a ToDo
        frappe.log_error(title="Student enrollment email failed")
        notify_reviewers("Student Application", app.name,
                         f"Enrolled {app.full_name} but the email failed. Send them this set-password link by hand: {link}",
                         "High")
        return

    notify_reviewers("Student Application", app.name,
                     f"{app.full_name} enrolled: login created, welcome email queued, {instance} (Active).",
                     "Low")
