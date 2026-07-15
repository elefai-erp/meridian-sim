"""Action capture: every student action feeds the appraisal's Action Log.

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
    """Append one action for the current site's simulation instance."""
    import frappe

    # No-op until the simulation doctypes ship — capture must never break a
    # voucher submission on a site that has the app but no simulation yet.
    if not frappe.db.table_exists("Sim Instance") or not frappe.db.table_exists("Action Log"):
        return

    # A site is one student instance; skip capture on non-simulation sites
    # (e.g. the golden template while it is being prepared by admins).
    if not frappe.db.exists("Sim Instance", {"status": "Active"}):
        return
    frappe.get_doc(
        {
            "doctype": "Action Log",
            "at": frappe.utils.now(),
            "user": frappe.session.user,
            "kind": kind,
            "reference": reference,
            "payload": frappe.as_json(payload or {}),
        }
    ).insert(ignore_permissions=True)
