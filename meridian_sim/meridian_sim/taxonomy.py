"""The scenario domain taxonomy — single source of truth.

Referenced by: Scenario Submission / Contributor / Contributor Application
doctype Select options, scenarios/schema.json's domain enum, and the
contribute/submit + contribute/apply web forms. When adding a domain, update
this list, then regenerate the doctype JSON, schema.json, and web form
dropdowns from it (see tools/sync_taxonomy.py).
"""

DOMAINS = [
    ("purchase-cycle", "Purchase Cycle"),
    ("sales-cycle", "Sales Cycle"),
    ("inventory", "Inventory Management"),
    ("bank-reco", "Banking & Reconciliation"),
    ("petty-cash", "Petty Cash"),
    ("fixed-assets", "Fixed Assets"),
    ("journal-entries", "Journal Entries"),
    ("credit-notes", "Credit Notes"),
    ("debit-notes", "Debit Notes"),
    ("customer-outstanding", "Customer Outstanding Management"),
    ("vendor-payments", "Vendor Payments"),
    ("vendor-mgmt", "Vendor Management (general)"),
    ("payroll", "Payroll"),
    ("gst", "GST Compliance"),
    ("tds", "TDS Compliance"),
    ("tax-adjustments", "Tax Adjustments"),
    ("month-end-closing", "Month-End Closing"),
    ("year-end-closing", "Year-End Closing"),
    ("finalization", "Finalization (general)"),
    ("revenue-recognition", "Revenue Recognition"),
    ("accrual-provision", "Accrual & Provision Entries"),
    ("financial-statements", "Financial Statement Preparation"),
    ("budget-vs-actual", "Budget vs Actual Analysis"),
    ("mis", "MIS & Reporting"),
    ("manufacturing-costing", "Manufacturing Costing"),
    ("multi-branch", "Multi-Branch Accounting"),
    ("intercompany", "Intercompany Transactions"),
    ("foreign-currency", "Foreign Currency Transactions"),
    ("audit-internal-control", "Internal Control & Audit Cases"),
    ("fraud-detection", "Fraud Detection Cases"),
    ("error-rectification", "Error Identification & Rectification"),
    ("erp-workflow", "ERP-based Workflow Scenarios"),
    ("business-decisions", "Business Decision Cases"),
    ("other", "Other"),
]

DOMAIN_SLUGS = [slug for slug, _ in DOMAINS]
DOMAIN_SELECT_OPTIONS = "\n".join(DOMAIN_SLUGS)
