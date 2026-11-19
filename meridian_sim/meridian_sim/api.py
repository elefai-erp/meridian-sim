"""Whitelisted API for the student portal and mock statutory sites.

Every student-visible action routes through here and is recorded in the
Sim Action Log — response times and behaviour feed the performance appraisal.
"""

import json
import random

import frappe
from frappe.utils import now

from meridian_sim.engine.action_log import record

MONTH_NAMES = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December",
}


def _instance() -> str:
    """The session user's active instance; admins fall back to any active one."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("Login required", frappe.PermissionError)
    name = frappe.db.get_value("Sim Instance", {"student": user, "status": "Active"})
    if not name and "System Manager" in frappe.get_roles(user):
        name = frappe.db.get_value("Sim Instance", {"status": "Active"})
    if not name:
        frappe.throw("No active simulation instance for your user. Ask your administrator to enroll you.")
    return name


# ---------------------------------------------------------------- My Desk ---

@frappe.whitelist()
def desk_summary():
    inst = _instance()
    doc = frappe.db.get_value(
        "Sim Instance", inst,
        ["name", "company", "sim_week", "status", "level", "gstin", "tan"],
        as_dict=True,
    )
    doc.update(
        unread_email=frappe.db.count("Sim Email", {"instance": inst, "folder": "Inbox", "is_read": 0}),
        unread_chat=frappe.db.count("Sim Chat Message", {"instance": inst, "direction": "In", "is_read": 0}),
        documents=frappe.db.count("Sim Document", {"instance": inst}),
        filed_returns=frappe.db.count("Sim GST Return", {"instance": inst, "status": "Filed"}),
    )
    return doc


# --------------------------------------------------------------- InboxPro ---

@frappe.whitelist()
def inbox_list(folder="Inbox"):
    inst = _instance()
    return frappe.get_all(
        "Sim Email",
        filters={"instance": inst, "folder": folder},
        fields=["name", "sender", "sender_email", "to_email", "subject", "received_at", "is_read"],
        order_by="received_at desc",
        limit_page_length=200,
    )


@frappe.whitelist()
def email_get(name):
    inst = _instance()
    doc = frappe.get_doc("Sim Email", name)
    if doc.instance != inst:
        frappe.throw("Not permitted", frappe.PermissionError)
    if not doc.is_read and doc.folder == "Inbox":
        frappe.db.set_value("Sim Email", name, "is_read", 1)
        record("inboxpro:read", reference=name, payload={"subject": doc.subject})
    return {
        "name": doc.name, "sender": doc.sender, "sender_email": doc.sender_email,
        "to_email": doc.to_email, "subject": doc.subject, "body": doc.body,
        "received_at": str(doc.received_at), "folder": doc.folder,
    }


@frappe.whitelist()
def email_send(to_email, subject, body, reply_to=None):
    inst = _instance()
    doc = frappe.get_doc({
        "doctype": "Sim Email", "instance": inst, "folder": "Sent",
        "sender": "You", "sender_email": "accounts@meridiantrading.in",
        "to_email": to_email, "subject": subject, "body": body,
        "received_at": now(), "is_read": 1, "reply_to": reply_to,
    }).insert(ignore_permissions=True)
    record("inboxpro:sent", reference=doc.name, payload={"to": to_email, "subject": subject})
    return {"name": doc.name}


# --------------------------------------------------------------- PingDesk ---

@frappe.whitelist()
def chat_list():
    inst = _instance()
    msgs = frappe.get_all(
        "Sim Chat Message",
        filters={"instance": inst},
        fields=["name", "channel", "direction", "sender", "message", "sent_at", "is_read"],
        order_by="sent_at asc",
        limit_page_length=500,
    )
    unread = [m["name"] for m in msgs if m["direction"] == "In" and not m["is_read"]]
    if unread:
        frappe.db.sql(
            "update `tabSim Chat Message` set is_read=1 where name in %(names)s",
            {"names": unread},
        )
        record("pingdesk:read", payload={"count": len(unread)})
    return msgs


@frappe.whitelist()
def chat_send(channel, message):
    inst = _instance()
    doc = frappe.get_doc({
        "doctype": "Sim Chat Message", "instance": inst, "channel": channel,
        "direction": "Out", "sender": "You", "message": message,
        "sent_at": now(), "is_read": 1,
    }).insert(ignore_permissions=True)
    record("pingdesk:sent", reference=doc.name, payload={"channel": channel})
    return {"name": doc.name, "sent_at": str(doc.sent_at)}


# --------------------------------------------------------------- DriveBox ---

@frappe.whitelist()
def drive_list():
    inst = _instance()
    return frappe.get_all(
        "Sim Document",
        filters={"instance": inst},
        fields=["name", "title", "category", "file", "dropped_by", "dropped_at", "description"],
        order_by="dropped_at desc",
        limit_page_length=200,
    )


@frappe.whitelist()
def document_get(name):
    inst = _instance()
    doc = frappe.get_doc("Sim Document", name)
    if doc.instance != inst:
        frappe.throw("Not permitted", frappe.PermissionError)
    record("drivebox:open", reference=name, payload={"title": doc.title})
    return {
        "name": doc.name, "title": doc.title, "category": doc.category,
        "file": doc.file, "content": doc.content, "dropped_by": doc.dropped_by,
        "dropped_at": str(doc.dropped_at or ""), "description": doc.description,
    }


# ----------------------------------------------------- TaxPortal (GST) ------

def _period_label(period):
    return f"{MONTH_NAMES.get(period[:2], period[:2])} {period[2:]}"


@frappe.whitelist()
def gst_dashboard():
    inst = _instance()
    info = frappe.db.get_value("Sim Instance", inst, ["company", "gstin"], as_dict=True)
    returns = frappe.get_all(
        "Sim GST Return",
        filters={"instance": inst},
        fields=["name", "return_type", "period", "status", "filed_at", "arn"],
        order_by="period asc, return_type asc",
    )
    for r in returns:
        r["period_label"] = _period_label(r["period"])
    two_b = frappe.get_all(
        "Sim Document",
        filters={"instance": inst, "category": "GSTR-2B"},
        fields=["name", "title", "dropped_at"],
        order_by="dropped_at desc",
    )
    record("taxportal:login")
    return {"company": info.company, "gstin": info.gstin, "returns": returns, "gstr2b": two_b}


def _books_summary(period):
    """Compute return figures from the student's actual ERPNext books.

    Zeroes until the company is set up — the portal still works, teaching the
    'books drive the return' relationship from day one.
    """
    year, month = period[2:], period[:2]
    out = {"outward_taxable": 0.0, "outward_tax": 0.0, "invoices": 0,
           "itc_taxable": 0.0, "itc_tax": 0.0, "purchase_invoices": 0}
    try:
        si = frappe.db.sql(
            """select count(*), ifnull(sum(base_net_total),0), ifnull(sum(base_total_taxes_and_charges),0)
               from `tabSales Invoice`
               where docstatus=1 and year(posting_date)=%s and month(posting_date)=%s""",
            (year, month),
        )[0]
        pi = frappe.db.sql(
            """select count(*), ifnull(sum(base_net_total),0), ifnull(sum(base_total_taxes_and_charges),0)
               from `tabPurchase Invoice`
               where docstatus=1 and year(posting_date)=%s and month(posting_date)=%s""",
            (year, month),
        )[0]
        out.update(invoices=int(si[0]), outward_taxable=float(si[1]), outward_tax=float(si[2]),
                   purchase_invoices=int(pi[0]), itc_taxable=float(pi[1]), itc_tax=float(pi[2]))
    except Exception:  # noqa: BLE001 - dashboard degrades to zeros if books are unreadable
        frappe.log_error(title="gst dashboard books summary failed")
    return out


@frappe.whitelist()
def gst_prepare(return_type, period):
    _instance()
    summary = _books_summary(period)
    record("taxportal:prepare", payload={"return_type": return_type, "period": period})
    return {"return_type": return_type, "period": period,
            "period_label": _period_label(period), "summary": summary}


@frappe.whitelist()
def gst_file(return_type, period):
    inst = _instance()
    if frappe.db.exists("Sim GST Return",
                        {"instance": inst, "return_type": return_type, "period": period, "status": "Filed"}):
        frappe.throw(f"{return_type} for {_period_label(period)} is already filed.")
    summary = _books_summary(period)
    arn = "AA3604" + "".join(random.choices("0123456789", k=10))
    doc = frappe.get_doc({
        "doctype": "Sim GST Return", "instance": inst, "return_type": return_type,
        "period": period, "status": "Filed", "filed_at": now(), "arn": arn,
        "summary": json.dumps(summary),
    }).insert(ignore_permissions=True)
    record("taxportal:filed", reference=doc.name,
           payload={"return_type": return_type, "period": period, "arn": arn, **summary})
    return {"arn": arn, "filed_at": str(doc.filed_at), "period_label": _period_label(period)}


# ------------------------------------------------- Income Tax (e-Pay) -------

@frappe.whitelist()
def challan_list():
    inst = _instance()
    info = frappe.db.get_value("Sim Instance", inst, ["company", "tan"], as_dict=True)
    challans = frappe.get_all(
        "Sim Challan",
        filters={"instance": inst},
        fields=["name", "challan_type", "section", "assessment_year", "period",
                "amount", "status", "paid_at", "cin"],
        order_by="paid_at desc",
    )
    record("incometax:login")
    return {"company": info.company, "tan": info.tan, "challans": challans}


@frappe.whitelist()
def challan_pay(challan_type, section, assessment_year, period, amount):
    inst = _instance()
    amount = float(amount)
    if amount <= 0:
        frappe.throw("Amount must be positive")
    cin = "HDFC" + "".join(random.choices("0123456789", k=5)) + "-" + "".join(random.choices("0123456789", k=5))
    doc = frappe.get_doc({
        "doctype": "Sim Challan", "instance": inst, "challan_type": challan_type,
        "section": section, "assessment_year": assessment_year, "period": period,
        "amount": amount, "status": "Paid", "paid_at": now(), "cin": cin,
    }).insert(ignore_permissions=True)
    record("incometax:challan_paid", reference=doc.name,
           payload={"section": section, "amount": amount, "cin": cin, "period": period})
    return {"cin": cin, "paid_at": str(doc.paid_at), "name": doc.name}
