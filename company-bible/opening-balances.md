# Opening Balances — Meridian Trading Pvt Ltd

> **Status:** Draft v0.1 — pending Domain Reviewer sign-off.
> Trial balance as at 1 April (simulation Day 1). These are **base figures for
> procedural generation** — each student instance varies them per the rules in §4,
> so no two students see identical numbers. The invariants in §5 must hold for every
> generated instance.

## 1. Opening Trial Balance (base) — as at 1 April

| Code | Account | Debit (₹) | Credit (₹) |
|---|---|---:|---:|
| 1101 | Furniture & Fixtures | 4,50,000 | |
| 1102 | Computers & Peripherals | 3,20,000 | |
| 1103 | Vehicles | 6,80,000 | |
| 1104 | Office Equipment | 1,50,000 | |
| 1151 | Accumulated Depreciation | | 4,10,000 |
| 1201 | Inventory — Trading Goods | 1,85,00,000 | |
| 1301 | Sundry Debtors | 2,10,45,000 | |
| 1401 | Cash in Hand | 48,000 | |
| 1411 | HDFC Bank — Current A/c | 12,35,000 | |
| 1501 | GST — Electronic Credit Ledger | 8,75,000 | |
| 1502 | TDS Receivable | 45,000 | |
| 1601 | Security Deposits | 3,00,000 | |
| 1602 | Prepaid Expenses | 85,000 | |
| 1901 | **Suspense Account** | **37,400** | |
| 2101 | HDFC Bank — Cash Credit A/c | | 38,50,000 |
| 2201 | Sundry Creditors | | 1,58,00,000 |
| 2401 | TDS Payable — 194C | | 22,000 |
| 2402 | TDS Payable — 194J | | 15,000 |
| 2403 | TDS Payable — 194I | | 7,500 |
| 2404 | TDS Payable — 192 (Salaries) | | 1,40,500 |
| 2501 | Salaries Payable | | 6,20,000 |
| 2502 | PF Payable | | 42,000 |
| 2503 | ESI Payable | | 8,000 |
| 2504 | Professional Tax Payable | | 7,600 |
| 2601 | Expenses Payable | | 55,000 |
| 2602 | Provision for Audit Fee | | 1,50,000 |
| 3101 | Share Capital | | 50,00,000 |
| 3201 | Reserves & Surplus | | 1,76,42,800 |
| | **Total** | **4,37,70,400** | **4,37,70,400** |

The ₹37,400 in **Suspense** is the outgoing accountant's parting gift: unexplained
differences parked over months. Investigating it is Week 1 work — it decomposes into
three real items the student can trace (a duplicated bank charge, an unrecorded counter
sale, and a transposition error in a vendor payment). The generator produces the
decomposition per instance.

## 2. Party-wise Schedules (base)

### 2.1 Sundry Debtors — ₹2,10,45,000

| Party | Amount (₹) | Ageing profile |
|---|---:|---|
| BuildRight Constructions Pvt Ltd | 92,40,000 | Chunks at 30/60/90+ days — chronic late payer |
| Sri Venkateshwara Electricals | 48,15,000 | Mostly current |
| Pavan Electrical Works | 31,20,000 | Irregular — includes unallocated on-account receipts |
| Metro Hardware Stores | 22,70,000 | Current |
| Sundry small parties | 16,00,000 | Mixed; includes two dormant balances |

### 2.2 Sundry Creditors — ₹1,58,00,000

| Party | Amount (₹) | Notes |
|---|---:|---|
| Deccan Wire Industries Ltd | 61,45,000 | 45-day terms |
| Suresh Electricals Pvt Ltd | 52,30,000 | **Includes one disputed invoice** (Week 4 story) |
| Omega Switchgear Ltd | 24,80,000 | Inter-state (IGST) |
| Sunrise Lighting Co | 15,60,000 | Inter-state (IGST) |
| Krishna Freight Carriers | 1,10,000 | GTA — RCM + 194C |
| Service vendors (rent, audit, housekeeping, internet) | 2,75,000 | |

### 2.3 GST Electronic Credit Ledger — ₹8,75,000

| Head | Amount (₹) |
|---|---:|
| CGST | 2,95,000 |
| SGST | 2,95,000 |
| IGST | 2,85,000 |

### 2.4 Statutory dues (all relating to March, payable in April)

| Due | Amount (₹) | Statutory deadline |
|---|---:|---|
| TDS (all sections) | 1,85,000 | 7 April |
| PF | 42,000 | 15 April |
| ESI | 8,000 | 15 April |
| Professional Tax | 7,600 | 10 April |
| March salaries (net) | 6,20,000 | 5 April |

The student's very first week contains live deadlines inherited from the handover.
Missing them is possible — and has consequences.

## 3. Pending Items at Handover (the Week 1 mess)

Generated per instance, drawn from this menu:

1. Suspense account balance (always present — see §1)
2. February bank reconciliation was the last one done — March is pending
3. 2–4 vendor invoices received but not entered (physical copies in DriveBox)
4. One customer cheque received 28 March, entered in books, **not yet on the bank statement**
5. Purchase register vs GSTR-2B for March: 1–2 invoices not appearing in 2B
6. Petty cash vouchers for March not entered (₹4,000–9,000 total)
7. The outgoing accountant's handover note — incomplete, occasionally wrong

## 4. Procedural Variation Rules

| Item | Variation band | Granularity |
|---|---|---|
| Turnover scale factor | 0.8× – 1.2× (sets the ₹8–12cr range) | Per instance, drives most other figures |
| Debtor/creditor party balances | ±15% around scaled base | Per party |
| Individual open invoices | Regenerated (count, dates, amounts) to sum to party balance | Per invoice |
| Bank & CC balances | ±10% | Per instance |
| Inventory | ±12% | Per instance |
| Suspense decomposition | Amount ₹18,000–₹64,000; always 3 traceable items | Per instance |
| Salary structure | Fixed roster and grosses (payroll scenarios depend on them) | Never varies |
| Share capital | Fixed ₹50,00,000 | Never varies |
| GST/TDS/PF/PT rates | **Never varied — these are law** | — |

## 5. Generator Invariants (enforced by `worldgen` self-check, CI-tested)

1. **Trial balance balances.** Sum of debits = sum of credits, exactly, for every instance. Reserves & Surplus is the balancing figure within a sanity band (₹1.2cr–₹2.4cr).
2. **Control accounts tie to schedules.** 1301 = Σ debtor parties; 2201 = Σ creditor parties; party balances = Σ their open invoices.
3. **Statutory dues are internally consistent.** TDS payable per section = Σ TDS on the underlying March transactions the student can inspect.
4. **CC utilisation ≤ ₹50,00,000** (the sanctioned limit) at generation time.
5. **Seeded errors are excluded from invariant checks by declaration** — a scenario's hidden error must be registered with the generator so the self-check knows the imbalance is intentional. An undeclared imbalance fails generation. This is what keeps seeded errors distinguishable from generator bugs.
