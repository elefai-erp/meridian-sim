"""Contributor login provisioning.

Contributors get their own Frappe User account, separate from students —
a distinct role ("Meridian Contributor") and a distinct portal (/contributor).

There's no outgoing email account configured on this deployment, so instead
of Frappe's usual "welcome email with a set-password link" flow, we generate
a temporary password directly and hand it back to the caller — who puts it
in the admin notification ToDo so a System Manager can relay it to the
contributor over WhatsApp or their own email. Matches the platform's
existing WhatsApp-first contributor communication model (see master doc §9).
"""

import secrets
import string

import frappe

ROLE = "Meridian Contributor"


def _ensure_role():
    if not frappe.db.exists("Role", ROLE):
        frappe.get_doc({
            "doctype": "Role", "role_name": ROLE, "desk_access": 0,
        }).insert(ignore_permissions=True)


def _generate_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def ensure_login(contributor_name: str) -> str | None:
    """Idempotent: provisions a login for this Contributor if it doesn't
    already have one. Returns the plaintext temp password on first
    creation, or None if a login already existed (nothing to relay)."""
    contributor = frappe.get_doc("Contributor", contributor_name)
    if contributor.login_created:
        return None
    if not contributor.email:
        return None  # can't create a login without an email to log in with

    _ensure_role()
    temp_password = _generate_password()

    user_name = contributor.email
    if frappe.db.exists("User", user_name):
        user = frappe.get_doc("User", user_name)
    else:
        parts = (contributor.full_name or "Contributor").split(" ", 1)
        user = frappe.get_doc({
            "doctype": "User", "email": user_name, "first_name": parts[0],
            "last_name": parts[1] if len(parts) > 1 else "",
            "send_welcome_email": 0, "user_type": "Website User",
        }).insert(ignore_permissions=True)

    if ROLE not in [r.role for r in user.roles]:
        user.append("roles", {"role": ROLE})
    user.new_password = temp_password
    user.save(ignore_permissions=True)

    contributor.db_set("user", user.name, notify=False)
    contributor.db_set("login_created", 1, notify=False)
    return temp_password
