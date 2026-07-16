"""Contributor identity resolution — shared by the public submission API and
the Scenario Submission / Contributor Application doctype controllers, so
"the same person" resolves to one Contributor record no matter which door
they came through (submitted a scenario first vs. applied first)."""

import frappe


def find_or_create(full_name, email=None, membership_no=None, specialization=None, city=None):
    """Match cascade: membership number (durable across name changes) →
    email → exact name. Creates a new Contributor if none match."""
    existing = None
    if membership_no:
        existing = frappe.db.get_value("Contributor", {"membership_no": membership_no})
    if not existing and email:
        existing = frappe.db.get_value("Contributor", {"email": email})
    if not existing and full_name:
        existing = frappe.db.get_value("Contributor", {"full_name": full_name})

    if existing:
        return existing

    return frappe.get_doc({
        "doctype": "Contributor", "full_name": full_name, "email": email,
        "membership_no": membership_no, "specialization": specialization, "city": city,
        "role": "Scenario Author", "status": "Active", "joined_on": frappe.utils.today(),
    }).insert(ignore_permissions=True).name
