"""Golden template: turn a fresh ERPNext site into Meridian Trading Pvt Ltd.

Source of truth: company-bible/meridian-trading.md, chart-of-accounts.md,
opening-balances.md. The opening trial balance must total ₹4,37,70,400 on
both sides — verify() asserts it.

Run on a site (company must already exist from the setup wizard, abbr MT):
    bench --site <site> execute meridian_sim.setup.golden_template.setup
    bench --site <site> execute meridian_sim.setup.golden_template.verify
"""

import frappe

COMPANY = "Meridian Trading"
ABBR = "MT"

# ---------------------------------------------------------------- accounts --
# (number, account_name, parent, account_type, is_group)
# parent is resolved with the company abbr suffix.
NEW_ACCOUNTS = [
    # Assets
    ("1102", "Computers & Peripherals", "Fixed Assets", "Fixed Asset", 0),
    ("1103", "Vehicles", "Fixed Assets", "Fixed Asset", 0),
    ("1201", "Inventory - Trading Goods", "Current Assets", None, 0),
    ("1411", "HDFC Bank - Current A/c", "Bank Accounts", "Bank", 0),
    ("1501", "GST - Electronic Credit Ledger", "Tax Assets", None, 1),
    ("15011", "Input Tax CGST", "GST - Electronic Credit Ledger", "Tax", 0),
    ("15012", "Input Tax SGST", "GST - Electronic Credit Ledger", "Tax", 0),
    ("15013", "Input Tax IGST", "GST - Electronic Credit Ledger", "Tax", 0),
    ("1502", "TDS Receivable", "Tax Assets", None, 0),
    ("1601", "Security Deposits", "Securities and Deposits", None, 0),
    ("1602", "Prepaid Expenses", "Loans and Advances (Assets)", None, 0),
    ("1901", "Suspense Account", "Temporary Accounts", None, 0),
    # Liabilities
    ("2101", "HDFC Bank - Cash Credit A/c", "Loans (Liabilities)", "Bank", 0),
    ("2301", "GST - Output Liability", "Duties and Taxes", None, 1),
    ("23011", "Output Tax CGST", "GST - Output Liability", "Tax", 0),
    ("23012", "Output Tax SGST", "GST - Output Liability", "Tax", 0),
    ("23013", "Output Tax IGST", "GST - Output Liability", "Tax", 0),
    ("2302", "GST - RCM Payable", "Duties and Taxes", "Tax", 0),
    ("2401", "TDS Payable - 194C", "Duties and Taxes", "Tax", 0),
    ("2402", "TDS Payable - 194J", "Duties and Taxes", "Tax", 0),
    ("2403", "TDS Payable - 194I", "Duties and Taxes", "Tax", 0),
    ("2404", "TDS Payable - 192 Salaries", "Duties and Taxes", "Tax", 0),
    ("2501", "Salaries Payable", "Current Liabilities", None, 0),
    ("2502", "PF Payable", "Current Liabilities", None, 0),
    ("2503", "ESI Payable", "Current Liabilities", None, 0),
    ("2504", "Professional Tax Payable", "Current Liabilities", None, 0),
    ("2601", "Expenses Payable", "Current Liabilities", None, 0),
    ("2602", "Provision for Audit Fee", "Current Liabilities", None, 0),
    # Equity
    ("3101", "Share Capital", "Capital Account", "Equity", 0),
    # Income
    ("4101", "Sales - Cables & Wires", "Direct Income", "Income Account", 0),
    ("4102", "Sales - Switchgear", "Direct Income", "Income Account", 0),
    ("4103", "Sales - Fans & Appliances", "Direct Income", "Income Account", 0),
    ("4104", "Sales - Lighting", "Direct Income", "Income Account", 0),
    ("4105", "Sales - Accessories & Consumables", "Direct Income", "Income Account", 0),
    ("4106", "Sales - Counter (B2C)", "Direct Income", "Income Account", 0),
    ("4201", "Discount Received", "Indirect Income", "Income Account", 0),
    ("4301", "Interest Income", "Indirect Income", "Income Account", 0),
    ("4901", "Miscellaneous Income", "Indirect Income", "Income Account", 0),
    # Expenses
    ("5101", "Purchases - Trading Goods", "Direct Expenses", None, 0),
    ("5102", "Freight Inward", "Direct Expenses", None, 0),
    ("5202", "Employer PF Contribution", "Indirect Expenses", None, 0),
    ("5203", "Staff Welfare", "Indirect Expenses", None, 0),
    ("5301", "Rent - Warehouse", "Indirect Expenses", None, 0),
    ("5302", "Electricity & Water", "Indirect Expenses", None, 0),
    ("5303", "Internet & Telephone", "Indirect Expenses", None, 0),
    ("5304", "Insurance", "Indirect Expenses", None, 0),
    ("5305", "Repairs & Maintenance", "Indirect Expenses", None, 0),
    ("5306", "Housekeeping & Security", "Indirect Expenses", None, 0),
    ("5401", "Vehicle Running & Maintenance", "Indirect Expenses", None, 0),
    ("5402", "Freight Outward", "Indirect Expenses", None, 0),
    ("5501", "Professional & Legal Fees", "Indirect Expenses", None, 0),
    ("5502", "Audit Fee", "Indirect Expenses", None, 0),
    ("5503", "Rates & Taxes", "Indirect Expenses", None, 0),
    ("5504", "Bank Charges", "Indirect Expenses", None, 0),
    ("5505", "Interest on CC", "Indirect Expenses", None, 0),
    ("5601", "Printing & Stationery", "Indirect Expenses", None, 0),
    ("5602", "Business Promotion", "Indirect Expenses", None, 0),
    ("5603", "Travelling & Conveyance", "Indirect Expenses", None, 0),
    ("5991", "Discount Allowed", "Indirect Expenses", None, 0),
]

# Bible code -> existing standard account (reused, not renamed)
REUSED = {
    "1101": "Furnitures and Fixtures",
    "1104": "Office Equipments",  # NOTE: 1104 also exists as new? no — reuse only
    "1151": "Accumulated Depreciations",
    "1301": "Debtors",
    "1401": "Cash",
    "2201": "Creditors",
    "3201": "Reserves and Surplus",
    "5201": "Salary",
    "5901": "Miscellaneous Expenses",
    "5951": "Depreciation",
}

# ----------------------------------------------------------------- parties --
CUSTOMERS = [
    "BuildRight Constructions Pvt Ltd",
    "Sri Venkateshwara Electricals",
    "Pavan Electrical Works",
    "Metro Hardware Stores",
    "Sundry Small Parties",
]
SUPPLIERS = [
    "Deccan Wire Industries Ltd",
    "Suresh Electricals Pvt Ltd",
    "Omega Switchgear Ltd",
    "Sunrise Lighting Co",
    "Krishna Freight Carriers",
    "Sundry Service Vendors",
]

# --------------------------------------------------------------- employees --
# (name, gender, designation, date_of_joining, date_of_birth)
EMPLOYEES = [
    ("Vikram Agarwal", "Male", "Managing Director", "2011-06-14", "1971-03-02"),
    ("Rajan Mehta", "Male", "Senior Accounts Manager", "2014-04-01", "1979-08-19"),
    ("Arjun Nair", "Male", "Sales Manager", "2017-01-09", "1986-11-27"),
    ("Kavita Reddy", "Female", "HR & Admin Manager", "2016-07-11", "1988-05-14"),
    ("Mohammed Irfan", "Male", "Purchase Officer", "2018-02-05", "1990-12-03"),
    ("Sneha Kulkarni", "Female", "Sales Executive", "2021-08-16", "1996-04-22"),
    ("Ravi Teja", "Male", "Sales Executive", "2022-03-01", "1997-09-08"),
    ("Prakash Rao", "Male", "Warehouse Supervisor", "2015-10-12", "1983-01-30"),
    ("Deepak Verma", "Male", "Accounts Assistant", "2023-06-19", "1999-07-16"),
    ("Anil Kumar", "Male", "Service Technician", "2019-11-04", "1992-02-11"),
    ("Lakshmi Devi", "Female", "Office Admin", "2013-09-02", "1985-06-25"),
    ("Srinu Yadav", "Male", "Warehouse Assistant", "2020-01-20", "1995-10-05"),
    ("Ramesh Goud", "Male", "Warehouse Assistant", "2021-05-17", "1994-03-18"),
    ("Shankar", "Male", "Delivery Driver", "2018-08-27", "1989-09-01"),
]

# ---------------------------------------------------- opening trial balance --
# (code, debit, credit, party_type, party) — totals must be 4,37,70,400 / side
OPENING_ROWS = [
    ("1101", 450000, 0, None, None),
    ("1102", 320000, 0, None, None),
    ("1103", 680000, 0, None, None),
    ("1104", 150000, 0, None, None),
    ("1151", 0, 410000, None, None),
    ("1201", 18500000, 0, None, None),
    ("1301", 9240000, 0, "Customer", "BuildRight Constructions Pvt Ltd"),
    ("1301", 4815000, 0, "Customer", "Sri Venkateshwara Electricals"),
    ("1301", 3120000, 0, "Customer", "Pavan Electrical Works"),
    ("1301", 2270000, 0, "Customer", "Metro Hardware Stores"),
    ("1301", 1600000, 0, "Customer", "Sundry Small Parties"),
    ("1401", 48000, 0, None, None),
    ("1411", 1235000, 0, None, None),
    ("15011", 295000, 0, None, None),
    ("15012", 295000, 0, None, None),
    ("15013", 285000, 0, None, None),
    ("1502", 45000, 0, None, None),
    ("1601", 300000, 0, None, None),
    ("1602", 85000, 0, None, None),
    ("1901", 37400, 0, None, None),
    ("2101", 0, 3850000, None, None),
    ("2201", 0, 6145000, "Supplier", "Deccan Wire Industries Ltd"),
    ("2201", 0, 5230000, "Supplier", "Suresh Electricals Pvt Ltd"),
    ("2201", 0, 2480000, "Supplier", "Omega Switchgear Ltd"),
    ("2201", 0, 1560000, "Supplier", "Sunrise Lighting Co"),
    ("2201", 0, 110000, "Supplier", "Krishna Freight Carriers"),
    ("2201", 0, 275000, "Supplier", "Sundry Service Vendors"),
    ("2401", 0, 22000, None, None),
    ("2402", 0, 15000, None, None),
    ("2403", 0, 7500, None, None),
    ("2404", 0, 140500, None, None),
    ("2501", 0, 620000, None, None),
    ("2502", 0, 42000, None, None),
    ("2503", 0, 8000, None, None),
    ("2504", 0, 7600, None, None),
    ("2601", 0, 55000, None, None),
    ("2602", 0, 150000, None, None),
    ("3101", 0, 5000000, None, None),
    ("3201", 0, 17642800, None, None),
]

EXPECTED_TOTAL = 43_770_400


def _acc(code):
    """Resolve a Bible code to the site's account docname."""
    if code in REUSED:
        return f"{REUSED[code]} - {ABBR}"
    name = frappe.db.get_value("Account", {"company": COMPANY, "account_number": code})
    if not name:
        frappe.throw(f"Account for Bible code {code} not found")
    return name


def _ensure_accounts():
    made = 0
    for number, account_name, parent, account_type, is_group in NEW_ACCOUNTS:
        if frappe.db.exists("Account", {"company": COMPANY, "account_number": number}):
            continue
        parent_name = frappe.db.get_value(
            "Account", {"company": COMPANY, "account_number": parent, "is_group": 1}
        ) or f"{parent} - {ABBR}"
        if not frappe.db.exists("Account", parent_name):
            # parent may itself be a new group referenced by name
            parent_name = frappe.db.get_value(
                "Account", {"company": COMPANY, "account_name": parent, "is_group": 1}
            )
        doc = frappe.get_doc({
            "doctype": "Account", "company": COMPANY, "account_name": account_name,
            "account_number": number, "parent_account": parent_name,
            "is_group": is_group, "account_type": account_type or "",
        })
        doc.insert(ignore_permissions=True)
        made += 1
    print(f"accounts: {made} created")


def _ensure_parties():
    cg = frappe.db.get_value("Customer Group", {"is_group": 0}) or "All Customer Groups"
    terr = frappe.db.get_value("Territory", {"is_group": 0}) or "All Territories"
    sg = frappe.db.get_value("Supplier Group", {"is_group": 0}) or "All Supplier Groups"
    made = 0
    for c in CUSTOMERS:
        if not frappe.db.exists("Customer", {"customer_name": c}):
            frappe.get_doc({
                "doctype": "Customer", "customer_name": c, "customer_type": "Company",
                "customer_group": cg, "territory": terr,
            }).insert(ignore_permissions=True)
            made += 1
    for s in SUPPLIERS:
        if not frappe.db.exists("Supplier", {"supplier_name": s}):
            frappe.get_doc({
                "doctype": "Supplier", "supplier_name": s, "supplier_type": "Company",
                "supplier_group": sg,
            }).insert(ignore_permissions=True)
            made += 1
    print(f"parties: {made} created")


def _ensure_employees():
    made = 0
    for name, gender, designation, doj, dob in EMPLOYEES:
        if frappe.db.exists("Employee", {"employee_name": name, "company": COMPANY}):
            continue
        if designation and not frappe.db.exists("Designation", designation):
            frappe.get_doc({"doctype": "Designation", "designation_name": designation}).insert(
                ignore_permissions=True)
        parts = name.split(" ", 1)
        frappe.get_doc({
            "doctype": "Employee", "first_name": parts[0],
            "last_name": parts[1] if len(parts) > 1 else "",
            "gender": gender, "date_of_birth": dob, "date_of_joining": doj,
            "company": COMPANY, "status": "Active", "designation": designation,
        }).insert(ignore_permissions=True)
        made += 1
    print(f"employees: {made} created")


def _post_opening():
    if frappe.db.exists("Journal Entry",
                        {"company": COMPANY, "is_opening": "Yes", "docstatus": 1}):
        print("opening entry: already posted, skipping")
        return
    dr = sum(r[1] for r in OPENING_ROWS)
    cr = sum(r[2] for r in OPENING_ROWS)
    assert dr == cr == EXPECTED_TOTAL, f"TB rows unbalanced: dr={dr} cr={cr}"

    je = frappe.get_doc({
        "doctype": "Journal Entry", "voucher_type": "Opening Entry",
        "company": COMPANY, "posting_date": "2026-04-01", "is_opening": "Yes",
        "user_remark": "Opening balances as at 1 April — golden template "
                       "(company-bible/opening-balances.md)",
        "accounts": [
            {
                "account": _acc(code),
                "debit_in_account_currency": debit,
                "credit_in_account_currency": credit,
                "party_type": party_type, "party": party,
            }
            for code, debit, credit, party_type, party in OPENING_ROWS
        ],
    })
    je.insert(ignore_permissions=True)
    je.submit()
    print(f"opening entry: {je.name} posted "
          f"(dr={dr:,} cr={cr:,})")


def setup():
    if not frappe.db.exists("Company", COMPANY):
        frappe.throw(f"Company '{COMPANY}' not found — run the ERPNext setup wizard first")
    # Non-perpetual inventory: Level-2 books treat inventory as one control
    # account (Bible 1201); item-wise perpetual stock is a later level.
    frappe.db.set_value("Company", COMPANY, "enable_perpetual_inventory", 0)
    frappe.db.set_value("Company", COMPANY, "tax_id", "AAECM4712F")
    if not frappe.get_all("Fiscal Year", filters=[
            ["year_start_date", "<=", "2026-04-01"], ["year_end_date", ">=", "2026-04-01"]]):
        frappe.throw("No fiscal year covers 2026-04-01 — create it first")
    _ensure_accounts()
    _ensure_parties()
    _ensure_employees()
    _post_opening()
    frappe.db.commit()
    verify()


def verify():
    dr, cr = frappe.db.sql(
        "select ifnull(sum(debit),0), ifnull(sum(credit),0) from `tabGL Entry` "
        "where company=%s and is_cancelled=0", COMPANY)[0]
    ok = dr == cr == EXPECTED_TOTAL
    print(f"GL totals: debit={dr:,.0f} credit={cr:,.0f} "
          f"(expected {EXPECTED_TOTAL:,}) -> {'BALANCED ✓' if ok else 'MISMATCH ✗'}")
    for label, code in (("Debtors", "1301"), ("Creditors", "2201"),
                        ("Suspense", "1901"), ("Reserves", "3201")):
        bal = frappe.db.sql(
            "select ifnull(sum(debit-credit),0) from `tabGL Entry` "
            "where company=%s and account=%s and is_cancelled=0",
            (COMPANY, _acc(code)))[0][0]
        print(f"  {label:<10} {bal:>15,.0f}")
    if not ok:
        frappe.throw("Opening trial balance does not match the Company Bible")
