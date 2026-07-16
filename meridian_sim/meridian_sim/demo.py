"""Demo/dev seeder: a Week-1 instance with story content from the Company Bible.

Run on a site:
    bench --site <site> execute meridian_sim.demo.setup_demo
    bench --site <site> execute meridian_sim.demo.reset_demo
"""

import json
import random

import frappe
from frappe.utils import add_to_date, now_datetime

EMAILS = [
    dict(sender="Priya Sharma", sender_email="priya.sharma@meridiantrading.in", hours_ago=30,
         subject="Welcome + March GST data pending",
         body="Hi,\n\nWelcome aboard. Heads up — March GSTR-1 data preparation is pending "
              "from the handover. The 2B for March is already in DriveBox.\n\nI can answer "
              "specific questions but I can't prepare it for you, I'm buried in the "
              "composition client filings this week.\n\nPriya"),
    dict(sender="Suresh Electricals", sender_email="accounts@sureshelectricals.in", hours_ago=26,
         subject="OUTSTANDING PAYMENT — statement attached",
         body="Sir,\n\nOur ledger statement is in your DriveBox. Balance as per our books "
              "differs from what your Rajan sir told us on phone. Clear the outstanding "
              "THIS WEEK or we cannot release the pending MCB consignment.\n\nSuresh"),
    dict(sender="HDFC Bank", sender_email="statements@hdfcbank.net.in", hours_ago=20,
         subject="Account statement — March (A/c ****3417)",
         body="Dear Customer,\n\nYour account statement for March has been placed in your "
              "document folder (DriveBox).\n\nThis is a system generated email."),
    dict(sender="Kavita Reddy", sender_email="hr@meridiantrading.in", hours_ago=6,
         subject="April attendance + payroll inputs",
         body="Hi,\n\nApril attendance sheet and payroll inputs are in DriveBox. Salaries "
              "must be credited by the 5th. The previous accountant's TDS working is also "
              "there — please check it before processing, I don't fully trust it.\n\nKavita"),
]

CHATS = [
    dict(channel="Rajan Mehta", sender="Rajan Mehta", hours_ago=28,
         message="joined? good. handover files are in drivebox. suspense account hai kuch, old items, adjust later"),
    dict(channel="Rajan Mehta", sender="Rajan Mehta", hours_ago=25,
         message="close the march bank reco by friday. also suresh outstanding sort it out, he called me twice"),
    dict(channel="Rajan Mehta", sender="Rajan Mehta", hours_ago=5,
         message="gst data for march — check with priya for the 2b. file hona chahiye on time"),
    dict(channel="Kavita Reddy", sender="Kavita Reddy", hours_ago=4,
         message="Hi! Sent payroll inputs on email. Salary by 5th please, last month one warehouse boy's salary was late and he sat in my cabin for an hour"),
]

DOCUMENTS = [
    dict(title="Handover note — outgoing accountant", category="Handover", dropped_by="Rajan Mehta",
         hours_ago=30, description="Incomplete. Occasionally wrong.",
         content="HANDOVER NOTE (as dictated)\n\n1. Books are in LedgerDesk. Mostly updated till March.\n"
                 "2. Suspense a/c 1901 — old items, small amounts, adjust later.\n"
                 "3. Feb bank reco done. March pending.\n"
                 "4. Suresh Electricals says balance difference — their mistake probably.\n"
                 "5. TDS working sheet is in the payroll folder. Same to same copy every month.\n"
                 "6. GST: Priya helps with 2B. File by due date.\n\n(no signature)"),
    dict(title="HDFC Bank statement — March", category="Bank Statement", dropped_by="HDFC Bank",
         hours_ago=20, description="Current account ****3417",
         content="HDFC BANK — STATEMENT (EXTRACT) — A/c ****3417 — March\n\n"
                 "01-Mar  OPENING BALANCE                          14,82,350.00 Cr\n"
                 "04-Mar  NEFT-DECCAN WIRE INDUSTRIES    1,84,320.00 Dr\n"
                 "07-Mar  TDS PAYMENT ITNS281              1,62,000.00 Dr\n"
                 "12-Mar  RTGS-BUILDRIGHT CONSTRUCTIONS   6,50,000.00 Cr\n"
                 "18-Mar  CHQ 004512 SURESH ELECTRICALS   3,20,000.00 Dr\n"
                 "25-Mar  COUNTER DEPOSIT                    1,86,400.00 Cr\n"
                 "28-Mar  BANK CHARGES                           1,180.00 Dr\n"
                 "31-Mar  CLOSING BALANCE                         12,35,000.00 Cr\n"),
    dict(title="Suresh Electricals — ledger statement", category="Invoice", dropped_by="Suresh Electricals",
         hours_ago=26, description="Vendor claims a different balance than our books.",
         content="SURESH ELECTRICALS PVT LTD — STATEMENT OF ACCOUNT: MERIDIAN TRADING PVT LTD\n\n"
                 "Balance as per our books: Rs. 51,05,000 Dr\n"
                 "(Your books may differ — check credit note CN-078 dated 12-Feb, rate difference "
                 "on MCB consignment, Rs. 1,25,000)\n\nPay immediately.\n"),
    dict(title="April attendance + TDS working (payroll inputs)", category="Payroll", dropped_by="Kavita Reddy",
         hours_ago=6, description="Attendance for April + the inherited TDS computation sheet.",
         content="PAYROLL INPUTS — APRIL\n\nAttendance: all 15 present full month except "
                 "Srinu Yadav (2 LOP days).\n\nTDS WORKING (inherited sheet — verify!):\n"
                 "  Vikram Agarwal   28,400\n  Rajan Mehta       6,150\n  Arjun Nair        3,200\n"
                 "  Kavita Reddy      4,950\n  (others below threshold)\n\n"
                 "NOTE from HR: figures copied forward since December. Please recompute."),
]

GSTR2B = dict(
    title="GSTR-2B — March (JSON)", category="GSTR-2B", dropped_by="TaxPortal",
    hours_ago=22, description="Auto-drafted ITC statement for March.",
    content=json.dumps({
        "gstin": "36AAECM4712F1Z8", "rtnprd": "032026",
        "docdata": {"b2b": [
            {"ctin": "36AAACS8912K1ZP", "trdnm": "Suresh Electricals Pvt Ltd",
             "inv": [{"inum": "SE/1873", "dt": "04-03-2026", "val": 412000, "txval": 349152, "igst": 0, "cgst": 31424, "sgst": 31424}]},
            {"ctin": "36AABCD4471M1ZC", "trdnm": "Deccan Wire Industries Ltd",
             "inv": [{"inum": "DW/9917", "dt": "11-03-2026", "val": 590000, "txval": 500000, "igst": 0, "cgst": 45000, "sgst": 45000}]},
            {"ctin": "27AAECO3319Q1ZF", "trdnm": "Omega Switchgear Ltd",
             "inv": [{"inum": "OS/2201", "dt": "17-03-2026", "val": 236000, "txval": 200000, "igst": 36000, "cgst": 0, "sgst": 0}]},
        ]},
        "note": "TRAINING SIMULATION DATA — compare with your purchase register.",
    }, indent=1),
)


def setup_demo(user="Administrator"):
    """Create an Active Week-1 instance for `user` with story content."""
    if frappe.db.exists("Sim Instance", {"student": user, "status": "Active"}):
        print(f"Active instance already exists for {user} — run reset_demo first to recreate.")
        return

    inst = frappe.get_doc({
        "doctype": "Sim Instance", "student": user, "status": "Active",
        "level": "junior-accountant", "seed": random.randint(1, 2**31),
        "start_date": now_datetime().date(), "sim_week": 1,
    }).insert(ignore_permissions=True)

    for e in EMAILS:
        frappe.get_doc({
            "doctype": "Sim Email", "instance": inst.name, "folder": "Inbox",
            "sender": e["sender"], "sender_email": e["sender_email"],
            "to_email": "accounts@meridiantrading.in", "subject": e["subject"],
            "body": e["body"], "received_at": add_to_date(now_datetime(), hours=-e["hours_ago"]),
        }).insert(ignore_permissions=True)

    for c in CHATS:
        frappe.get_doc({
            "doctype": "Sim Chat Message", "instance": inst.name, "channel": c["channel"],
            "direction": "In", "sender": c["sender"], "message": c["message"],
            "sent_at": add_to_date(now_datetime(), hours=-c["hours_ago"]),
        }).insert(ignore_permissions=True)

    for d in DOCUMENTS + [GSTR2B]:
        frappe.get_doc({
            "doctype": "Sim Document", "instance": inst.name, "title": d["title"],
            "category": d["category"], "dropped_by": d["dropped_by"],
            "dropped_at": add_to_date(now_datetime(), hours=-d["hours_ago"]),
            "description": d["description"], "content": d["content"],
        }).insert(ignore_permissions=True)

    frappe.db.commit()
    print(f"Demo instance {inst.name} created for {user}: "
          f"{len(EMAILS)} emails, {len(CHATS)} chats, {len(DOCUMENTS) + 1} documents.")


def reset_demo(user="Administrator"):
    """Delete all simulation data for `user`'s instances and reseed."""
    for inst in frappe.get_all("Sim Instance", filters={"student": user}, pluck="name"):
        for dt in ("Sim Email", "Sim Chat Message", "Sim Document", "Sim Story Event",
                   "Sim Action Log", "Sim GST Return", "Sim Challan"):
            frappe.db.delete(dt, {"instance": inst})
        frappe.delete_doc("Sim Instance", inst, ignore_permissions=True, force=True)
    frappe.db.commit()
    setup_demo(user)
