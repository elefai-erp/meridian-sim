# Copyright (c) 2026, Meridian Sim Contributors — AGPL-3.0

import frappe
from frappe.model.document import Document

from meridian_sim import contributor_login
from meridian_sim.contributors import find_or_create


class ContributorApplication(Document):
	def on_update(self):
		if self.status != "Approved" or self.linked_contributor:
			return

		contributor = find_or_create(self.full_name, self.email, self.membership_no,
									  self.specialization, self.city)
		# membership_body and source_application aren't captured by find_or_create
		# (shared with Scenario Submission, which has neither) — backfill here.
		updates = {}
		if self.membership_body:
			updates["membership_body"] = self.membership_body
		if not frappe.db.get_value("Contributor", contributor, "source_application"):
			updates["source_application"] = self.name
		if updates:
			frappe.db.set_value("Contributor", contributor, updates)

		self.db_set("linked_contributor", contributor, notify=False)

		temp_password = contributor_login.ensure_login(contributor)
		if temp_password:
			frappe.msgprint(
				f"A login was just created for this contributor ({self.email}) — "
				f"temp password: {temp_password}. Relay it to them; no outgoing "
				f"email is configured on this site.",
				title="Contributor login created", indicator="blue",
			)
