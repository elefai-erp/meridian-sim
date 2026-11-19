# Copyright (c) 2026, Meridian Sim Contributors — AGPL-3.0

import frappe
from frappe.model.document import Document


class StudentApplication(Document):
	def on_update(self):
		# Runs on every save; enroll() is idempotent via linked_instance.
		# Synchronous on purpose: the shared bench's background queue can lag
		# minutes, and a failure here must never block saving the application.
		if self.status == "Enrolled" and not self.linked_instance:
			try:
				from meridian_sim.student_enrollment import enroll

				enroll(self.name)
			except Exception:
				frappe.log_error(title="Student enrollment failed")
				from meridian_sim.notify import notify_reviewers

				notify_reviewers(
					"Student Application", self.name,
					f"Automatic enrollment failed for {self.full_name} — see Error Log. "
					f"Set up manually: {self.email} / {self.phone}.", "High",
				)
