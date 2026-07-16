# Copyright (c) 2026, Meridian Sim Contributors — AGPL-3.0

import frappe
from frappe.model.document import Document


class ContributorApplication(Document):
	def on_update(self):
		if self.status == "Approved" and not self.linked_contributor:
			existing = None
			if self.membership_no:
				existing = frappe.db.get_value("Contributor", {"membership_no": self.membership_no})
			if not existing:
				existing = frappe.db.get_value("Contributor", {"full_name": self.full_name})

			if existing:
				contributor_name = existing
			else:
				contributor_name = frappe.get_doc({
					"doctype": "Contributor", "full_name": self.full_name,
					"membership_body": self.membership_body, "membership_no": self.membership_no,
					"city": self.city, "specialization": self.specialization,
					"role": "Scenario Author", "status": "Active",
					"joined_on": frappe.utils.today(), "source_application": self.name,
				}).insert(ignore_permissions=True).name

			self.linked_contributor = contributor_name
			self.db_set("linked_contributor", contributor_name, notify=False)
