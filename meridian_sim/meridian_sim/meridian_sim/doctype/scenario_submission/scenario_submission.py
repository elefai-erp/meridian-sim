# Copyright (c) 2026, Meridian Sim Contributors — AGPL-3.0

import frappe
from frappe.model.document import Document


class ScenarioSubmission(Document):
	def on_update(self):
		if self.status in ("Approved", "Live") and not self.linked_contributor:
			self.linked_contributor = _credit_contributor(
				name=self.contributor_name,
				membership_no=self.membership_no,
				specialization=self.specialization,
				city=self.city,
			)
			self.db_set("linked_contributor", self.linked_contributor, notify=False)


def _credit_contributor(name, membership_no, specialization, city):
	"""Find-or-create the Contributor record and bump their authored count.
	Matches on membership number first (the durable identity); falls back to
	an exact name match for contributors without one yet — good enough while
	submission volume is low, worth tightening (e.g. require email match too)
	once two contributors are likely to share a name."""
	existing = None
	if membership_no:
		existing = frappe.db.get_value("Contributor", {"membership_no": membership_no})
	if not existing:
		existing = frappe.db.get_value("Contributor", {"full_name": name})

	if existing:
		contributor = frappe.get_doc("Contributor", existing)
		contributor.scenarios_authored = (contributor.scenarios_authored or 0) + 1
		contributor.save(ignore_permissions=True)
		return contributor.name

	contributor = frappe.get_doc({
		"doctype": "Contributor", "full_name": name, "membership_no": membership_no,
		"specialization": specialization, "city": city, "role": "Scenario Author",
		"scenarios_authored": 1, "status": "Active", "joined_on": frappe.utils.today(),
	}).insert(ignore_permissions=True)
	return contributor.name
