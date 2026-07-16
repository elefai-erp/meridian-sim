"""Action capture: every student action feeds the appraisal's Sim Action Log.

Wired to ERPNext doctypes via hooks.doc_events; mock sites call `record`
directly through their APIs.
"""


def capture(doc, method=None):
    """doc_events target — records a submitted/cancelled/amended voucher."""
    record(
        kind=f"{doc.doctype}:{method or 'update'}",
        reference=doc.name,
        payload={"doctype": doc.doctype, "docstatus": doc.docstatus},
    )


def record(kind: str, reference: str | None = None, payload: dict | None = None):
    """Append one action for the session user's active simulation instance.

    Must never break the calling transaction: silently a no-op when the
    simulation tables don't exist (app installed ahead of the simulation)
    or when the user has no active instance (admins working on the site).
    """
    import frappe

    if not frappe.db.table_exists("Sim Instance") or not frappe.db.table_exists("Sim Action Log"):
        return
    instance = frappe.db.get_value(
        "Sim Instance", {"student": frappe.session.user, "status": "Active"}
    )
    if not instance:
        return
    frappe.get_doc(
        {
            "doctype": "Sim Action Log",
            "instance": instance,
            "at": frappe.utils.now(),
            "user": frappe.session.user,
            "kind": kind,
            "reference": reference,
            "payload": frappe.as_json(payload or {}),
        }
    ).insert(ignore_permissions=True)
