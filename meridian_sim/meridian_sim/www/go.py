import frappe


def get_context(context):
    """Dashboard dispatcher: sends a logged-in user to the right home —
    the contributor portal if they have a Contributor profile, else the
    student desk. Keeps the shared nav's "My Desk" link correct for both
    audiences without per-page server context plumbing."""
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/go"
        raise frappe.Redirect
    if frappe.db.exists("Contributor", {"user": frappe.session.user}):
        frappe.local.flags.redirect_location = "/contributor"
    else:
        frappe.local.flags.redirect_location = "/mydesk"
    raise frappe.Redirect
