"""Zero-config admin notification: a ToDo per System Manager. No outgoing
email account is configured on this deployment, so this — not email — is
the reliable notification path, shared by the public API and doctype
controllers alike."""

import frappe


def notify_reviewers(reference_type, reference_name, description, priority="Medium"):
    reviewers = frappe.get_all(
        "Has Role", filters={"role": "System Manager", "parenttype": "User"}, pluck="parent"
    )
    for user in set(reviewers):
        frappe.get_doc({
            "doctype": "ToDo", "allocated_to": user, "status": "Open", "priority": priority,
            "reference_type": reference_type, "reference_name": reference_name,
            "description": description,
        }).insert(ignore_permissions=True)
