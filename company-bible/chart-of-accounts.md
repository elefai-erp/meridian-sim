# Chart of Accounts — Meridian Trading Pvt Ltd

> **Status:** Draft v0.1 — pending Domain Reviewer sign-off.
> This is the COA as it exists in LedgerDesk on Day 1 of the simulation. It was set up
> years ago by Rajan and has accumulated quirks — those quirks are deliberate and are
> part of the world (see §Notes at the bottom). Scenario authors must use these account
> codes and names exactly.

Account code convention: `1xxx` assets · `2xxx` liabilities · `3xxx` equity ·
`4xxx` income · `5xxx` expenses.

## 1xxx — Assets

| Code | Account | Notes |
|---|---|---|
| 1101 | Furniture & Fixtures | |
| 1102 | Computers & Peripherals | |
| 1103 | Vehicles | Delivery van (Tata Ace) |
| 1104 | Office Equipment | AC units, printer, UPS |
| 1151 | Accumulated Depreciation | Single lump account — **not split by asset class** (Rajan's setup) |
| 1201 | Inventory — Trading Goods | Single inventory control account |
| 1301 | Sundry Debtors | Control account; party-wise sub-ledgers |
| 1401 | Cash in Hand | Counter cash + petty cash mixed — a known mess |
| 1411 | HDFC Bank — Current A/c ****3417 | |
| 1501 | GST — Electronic Credit Ledger (ITC) | CGST/SGST/IGST tracked in sub-ledgers |
| 1502 | TDS Receivable | TDS deducted by customers on our interest/receipts |
| 1601 | Security Deposits | Warehouse deposit |
| 1602 | Prepaid Expenses | Insurance mostly |
| 1901 | Suspense Account | **Should be zero. Is not.** (Week 1 handover mess) |

## 2xxx — Liabilities

| Code | Account | Notes |
|---|---|---|
| 2101 | HDFC Bank — Cash Credit A/c | Limit ₹50,00,000 |
| 2201 | Sundry Creditors | Control account; party-wise sub-ledgers |
| 2301 | GST Payable — Output | CGST/SGST/IGST sub-ledgers |
| 2302 | GST — RCM Payable | Freight (GTA) reverse charge |
| 2401 | TDS Payable — 194C | Contractors & transport |
| 2402 | TDS Payable — 194J | Professional fees |
| 2403 | TDS Payable — 194I | Rent |
| 2404 | TDS Payable — 192 (Salaries) | |
| 2501 | Salaries Payable | |
| 2502 | PF Payable | Employee + employer portions |
| 2503 | ESI Payable | |
| 2504 | Professional Tax Payable | Telangana slabs |
| 2601 | Expenses Payable | Accrued utilities etc. |
| 2602 | Provision for Audit Fee | |

## 3xxx — Equity

| Code | Account |
|---|---|
| 3101 | Share Capital |
| 3201 | Reserves & Surplus |

## 4xxx — Income

| Code | Account | Notes |
|---|---|---|
| 4101 | Sales — Cables & Wires | |
| 4102 | Sales — Switchgear | |
| 4103 | Sales — Fans & Appliances | |
| 4104 | Sales — Lighting | |
| 4105 | Sales — Accessories & Consumables | |
| 4106 | Sales — Counter (B2C) | Daily cash/UPI sales, all product lines mixed — **another Rajan quirk** |
| 4201 | Discount Received | |
| 4301 | Interest Income | On security deposit / FD |
| 4901 | Miscellaneous Income | Scrap sales land here |

## 5xxx — Expenses

| Code | Account | Notes |
|---|---|---|
| 5101 | Purchases — Trading Goods | Single purchase account, all product lines |
| 5102 | Freight Inward | GTA freight — RCM applies |
| 5201 | Salaries & Wages | |
| 5202 | Employer PF Contribution | |
| 5203 | Staff Welfare | |
| 5301 | Rent — Warehouse | TDS 194I |
| 5302 | Electricity & Water | |
| 5303 | Internet & Telephone | |
| 5304 | Insurance | |
| 5305 | Repairs & Maintenance | |
| 5306 | Housekeeping & Security | TDS 194C |
| 5401 | Vehicle Running & Maintenance | |
| 5402 | Freight Outward | Customer deliveries |
| 5501 | Professional & Legal Fees | TDS 194J |
| 5502 | Audit Fee | |
| 5503 | Rates & Taxes | |
| 5504 | Bank Charges | |
| 5505 | Interest on CC | |
| 5601 | Printing & Stationery | |
| 5602 | Business Promotion | |
| 5603 | Travelling & Conveyance | |
| 5901 | Miscellaneous Expenses | **Rajan's dumping ground.** Students inherit years of bad habits here |
| 5951 | Depreciation | |
| 5991 | Discount Allowed | |

## Notes — the deliberate quirks (for scenario authors)

These imperfections are part of the world. Scenarios may exploit them; do not "fix" them
in the Bible:

1. **1901 Suspense Account** has a non-zero opening balance — the outgoing accountant parked unexplained differences there. Cleaning it up is Week 1 work.
2. **1151 Accumulated Depreciation** is one lump account across asset classes — makes the Level 3 depreciation schedule harder than it should be.
3. **4106 Counter Sales** mixes all product lines — makes product-wise margin analysis in the Week 8 MIS impossible without extra work, which is the point.
4. **5901 Miscellaneous Expenses** contains things that belong elsewhere — an audit flag waiting to happen.
5. **1401 Cash in Hand** mixes counter float and petty cash — reconciliation friction by design.

New accounts may be added by scenarios only via Core Team approval, since every
student's LedgerDesk must stay consistent with this document.
