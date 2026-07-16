"""Public (guest-accessible) API for the Meridian Sim community website:
student enrollment applications, contributor applications, scenario
submissions, and the two ranking dashboards.

Everything here is intentionally allow_guest — this is the front door of an
open-source, community-driven platform. Writes are narrow (insert one
application/submission doc, nothing else) even though permissions are
bypassed, and reads expose only what is meant to be public.
"""

import frappe
from frappe.utils import now

from meridian_sim import contributor_login, scoring
from meridian_sim.contributors import find_or_create
from meridian_sim.notify import notify_reviewers


def _require(value, label):
    if not value or not str(value).strip():
        frappe.throw(f"{label} is required")


# ------------------------------------------------------------ enrollment ---

@frappe.whitelist(allow_guest=True)
def submit_student_application(full_name, email, phone=None, city=None,
                                education=None, level_interested="accounts-assistant",
                                why_join=None):
    _require(full_name, "Full name")
    _require(email, "Email")
    doc = frappe.get_doc({
        "doctype": "Student Application", "full_name": full_name.strip(),
        "email": email.strip(), "phone": phone, "city": city, "education": education,
        "level_interested": level_interested, "why_join": why_join,
        "status": "New", "applied_on": now(),
    }).insert(ignore_permissions=True)
    notify_reviewers("Student Application", doc.name,
                      f"New student application: {doc.full_name} ({doc.level_interested})")
    frappe.db.commit()
    return {"name": doc.name}


# ----------------------------------------------------------- contribution --

@frappe.whitelist(allow_guest=True)
def submit_contributor_application(full_name, email, specialization, phone=None,
                                    membership_body="ICAI", membership_no=None, city=None,
                                    years_of_practice=None, completed_level2=0, motivation=None):
    _require(full_name, "Full name")
    _require(email, "Email")
    _require(specialization, "Specialisation area")
    doc = frappe.get_doc({
        "doctype": "Contributor Application", "full_name": full_name.strip(),
        "email": email.strip(), "phone": phone, "membership_body": membership_body,
        "membership_no": membership_no, "city": city,
        "years_of_practice": years_of_practice or 0,
        "specialization": specialization, "completed_level2": int(bool(int(completed_level2 or 0))),
        "motivation": motivation, "status": "New", "applied_on": now(),
    }).insert(ignore_permissions=True)
    notify_reviewers("Contributor Application", doc.name,
                      f"New contributor application: {doc.full_name} ({doc.specialization})")
    frappe.db.commit()
    return {"name": doc.name}


@frappe.whitelist(allow_guest=True)
def submit_scenario(contributor_name, contributor_email, title, domain, situation,
                     student_task, correct_treatment, law_reference,
                     membership_no=None, specialization=None, city=None, years_of_practice=None,
                     difficulty="Junior", common_wrong=None, rajan_advice=None,
                     rajan_why_wrong=None, consequence_what=None, consequence_week=None,
                     supporting_file=None):
    for value, label in ((contributor_name, "Your name"), (contributor_email, "Your email"),
                         (title, "Scenario title"), (domain, "Domain"), (situation, "Situation"),
                         (student_task, "Student task"), (correct_treatment, "Correct treatment"),
                         (law_reference, "Law reference")):
        _require(value, label)

    contributor_name = contributor_name.strip()
    contributor_email = contributor_email.strip()

    # Resolve (or create) the Contributor record up front — per the badge
    # table, "🌱 Contributor" is earned at first submission, not at approval,
    # so this is also where their portal login gets provisioned.
    contributor = find_or_create(contributor_name, contributor_email, membership_no, specialization, city)
    frappe.db.set_value("Contributor", contributor, "scenarios_submitted",
                         (frappe.db.get_value("Contributor", contributor, "scenarios_submitted") or 0) + 1)
    scoring.award_points(contributor, "Submit a Scenario")
    temp_password = contributor_login.ensure_login(contributor)

    doc = frappe.get_doc({
        "doctype": "Scenario Submission",
        "contributor_name": contributor_name, "contributor_email": contributor_email,
        "membership_no": membership_no, "specialization": specialization, "city": city,
        "years_of_practice": years_of_practice or 0,
        "title": title.strip(), "domain": domain, "difficulty": difficulty,
        "situation": situation, "student_task": student_task, "common_wrong": common_wrong,
        "correct_treatment": correct_treatment, "law_reference": law_reference,
        "rajan_advice": rajan_advice, "rajan_why_wrong": rajan_why_wrong,
        "consequence_what": consequence_what, "consequence_week": consequence_week,
        "supporting_file": supporting_file, "status": "Submitted", "submitted_on": now(),
        "linked_contributor": contributor,
    }).insert(ignore_permissions=True)

    note = f"New scenario submission: \"{doc.title}\" ({doc.domain}) by {doc.contributor_name}"
    if temp_password:
        note += (f"\n\nNew contributor login created: {contributor_email} / temp password: "
                 f"{temp_password}\nPlease relay this to them (WhatsApp/email) — no SMTP is "
                 f"configured on this site, so they were not emailed automatically.")
    notify_reviewers("Scenario Submission", doc.name, note, priority="High")
    frappe.db.commit()
    return {"name": doc.name, "contributor": contributor}


# ---------------------------------------------------------- contributor portal --

@frappe.whitelist()
def my_contributor_profile():
    """The logged-in contributor's own dashboard data. Requires login —
    unlike everything else in this module, this is not allow_guest."""
    contributor = frappe.db.get_value("Contributor", {"user": frappe.session.user})
    if not contributor:
        frappe.throw("No contributor profile is linked to your login.", frappe.DoesNotExistError)
    doc = frappe.get_doc("Contributor", contributor)
    badge = scoring.compute_badge(doc.scenarios_submitted or 0, doc.scenarios_authored or 0,
                                   is_master=(doc.role == "Core Contributor" and doc.scenarios_authored >= 50))
    submissions = frappe.get_all(
        "Scenario Submission", filters={"linked_contributor": contributor},
        fields=["name", "title", "domain", "difficulty", "status", "submitted_on"],
        order_by="submitted_on desc",
    )
    return {
        "full_name": doc.full_name, "role": doc.role, "specialization": doc.specialization,
        "city": doc.city, "scenarios_submitted": doc.scenarios_submitted or 0,
        "scenarios_authored": doc.scenarios_authored or 0,
        "scenarios_reviewed": doc.scenarios_reviewed or 0,
        "all_time_score": scoring.total_score(contributor),
        "month_score": scoring.total_score(contributor, month_only=True),
        "badge": badge, "submissions": submissions,
        "linkedin_badge_url": f"/api/method/meridian_sim.badge.linkedin_badge?contributor={contributor}",
    }


# -------------------------------------------------------------- rankings ---

def _handle(full_name):
    """First name + last-initial, e.g. 'Kashif J.' — a public leaderboard
    shouldn't expose a student's full legal name."""
    parts = (full_name or "Student").split()
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} {parts[-1][0]}."


@frappe.whitelist(allow_guest=True)
def student_leaderboard():
    rows = frappe.db.sql(
        """
        select si.name, si.student, si.level, si.sim_week, si.status,
               count(al.name) as actions
        from `tabSim Instance` si
        left join `tabSim Action Log` al on al.instance = si.name
        where si.status in ('Active', 'Completed', 'Certified')
        group by si.name
        order by si.sim_week desc, actions desc
        limit 50
        """, as_dict=True,
    )
    out = []
    for i, r in enumerate(rows, start=1):
        full_name = frappe.db.get_value("User", r.student, "full_name") or r.student
        out.append({
            "rank": i, "handle": _handle(full_name), "level": r.level,
            "week": r.sim_week, "actions": r.actions, "status": r.status,
        })
    return out


@frappe.whitelist(allow_guest=True)
def contributor_leaderboard(period="all"):
    """period: 'all' (all-time) or 'month' (current calendar month)."""
    month_only = period == "month"
    rows = frappe.get_all(
        "Contributor", filters={"status": "Active"},
        fields=["name", "full_name", "role", "specialization", "city",
                "scenarios_authored", "scenarios_submitted", "scenarios_reviewed", "linkedin"],
    )
    for r in rows:
        r["score"] = scoring.total_score(r["name"], month_only=month_only)
        r["badge"] = scoring.compute_badge(r["scenarios_submitted"] or 0, r["scenarios_authored"] or 0)
    rows = [r for r in rows if r["score"] > 0] if month_only else rows
    rows.sort(key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
    return rows
