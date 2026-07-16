# Copyright (c) 2026, Meridian Sim Contributors — AGPL-3.0

import frappe
from frappe.model.document import Document

from meridian_sim import contributor_login, scoring
from meridian_sim.contributors import find_or_create


class ScenarioSubmission(Document):
	def on_update(self):
		self._credit_approval()
		self._credit_major_revision()

	def _credit_approval(self):
		"""Fires once, the moment status first reaches Approved/Live. Tick the
		High Complexity / Zero Revisions / Top Rated / Used in Certification
		boxes *before or at* this save — bonuses are a snapshot taken right
		here, not re-evaluated on later edits."""
		if self.status not in ("Approved", "Live") or self.points_awarded:
			return

		contributor = self.linked_contributor
		if not contributor:
			# Defensive fallback: a submission created directly in the desk
			# (bypassing the public API) won't have a contributor linked yet.
			contributor = find_or_create(self.contributor_name, self.contributor_email,
										  self.membership_no, self.specialization, self.city)
			self.db_set("linked_contributor", contributor, notify=False)

		doc = frappe.get_doc("Contributor", contributor)
		doc.scenarios_authored = (doc.scenarios_authored or 0) + 1
		doc.save(ignore_permissions=True)

		scoring.award_points(contributor, "Scenario Approved", reference_scenario=self.name)
		if self.is_high_complexity:
			scoring.award_points(contributor, "High Complexity Scenario", reference_scenario=self.name)
		if self.zero_revisions_required:
			scoring.award_points(contributor, "Zero Revisions Required", reference_scenario=self.name)
		if self.top_rated_by_review_team:
			scoring.award_points(contributor, "Top Rated by Review Team", reference_scenario=self.name)
		if self.used_in_certification:
			scoring.award_points(contributor, "Scenario Used in Certification", reference_scenario=self.name)

		temp_password = contributor_login.ensure_login(contributor)
		if temp_password:
			frappe.msgprint(
				f"A login was just created for this contributor ({doc.email}) — "
				f"temp password: {temp_password}. Relay it to them; no outgoing "
				f"email is configured on this site.",
				title="Contributor login created", indicator="blue",
			)

		self.db_set("points_awarded", 1, notify=False)

	def _credit_major_revision(self):
		if not self.major_revision or self.revision_points_awarded or not self.linked_contributor:
			return
		scoring.award_points(self.linked_contributor, "Major Revision of Existing Scenario",
							  reference_scenario=self.name)
		self.db_set("revision_points_awarded", 1, notify=False)
