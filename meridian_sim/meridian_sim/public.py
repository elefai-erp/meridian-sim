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
    doc = frappe.get_doc({
        "doctype": "Scenario Submission",
        "contributor_name": contributor_name.strip(), "contributor_email": contributor_email.strip(),
        "membership_no": membership_no, "specialization": specialization, "city": city,
        "years_of_practice": years_of_practice or 0,
        "title": title.strip(), "domain": domain, "difficulty": difficulty,
        "situation": situation, "student_task": student_task, "common_wrong": common_wrong,
        "correct_treatment": correct_treatment, "law_reference": law_reference,
        "rajan_advice": rajan_advice, "rajan_why_wrong": rajan_why_wrong,
        "consequence_what": consequence_what, "consequence_week": consequence_week,
        "supporting_file": supporting_file, "status": "Submitted", "submitted_on": now(),
    })
    existing = frappe.db.get_value("Contributor", {"membership_no": membership_no}) \
        if membership_no else None
    if existing:
        doc.linked_contributor = existing
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name}


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


_ROLE_WEIGHT = {"Core Contributor": 3, "Domain Reviewer": 2, "Scenario Author": 1}


@frappe.whitelist(allow_guest=True)
def contributor_leaderboard():
    rows = frappe.get_all(
        "Contributor", filters={"status": "Active"},
        fields=["name", "full_name", "role", "specialization", "city",
                "scenarios_authored", "scenarios_reviewed", "linkedin"],
    )
    for r in rows:
        r["score"] = (r["scenarios_authored"] or 0) + 2 * (r["scenarios_reviewed"] or 0) \
            + 5 * _ROLE_WEIGHT.get(r["role"], 0)
    rows.sort(key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
    return rows
