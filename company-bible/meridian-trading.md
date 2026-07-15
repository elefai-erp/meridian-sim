# The Company Bible — Meridian Trading Pvt Ltd

> **Status:** Draft v0.1 — pending Domain Reviewer sign-off.
> This is the single source of truth for the fictional world every scenario is set in.
> Every CA contributor reads this before writing a scenario. If your scenario contradicts
> this document, the scenario changes — not the Bible.

All names, registration numbers, and identifiers in this document are fictional. Any
resemblance to real entities is coincidental. Base figures below are the **procedural
generation baseline** — each student's instance varies these numbers within defined
bands, so no two students share an answer key.

---

## 1. Company Profile

| Attribute | Detail |
|---|---|
| Legal name | Meridian Trading Private Limited |
| CIN | U51909TG2011PTC076543 (fictional) |
| Incorporated | 14 June 2011 |
| Type | Private limited — trading company |
| Industry | Electrical goods distribution (B2B ~70%, B2C ~30%) |
| Registered office | Plot 42, Industrial Development Area, Balanagar, Hyderabad, Telangana 500037 |
| Warehouse | Survey No. 118, Medchal Road, Hyderabad (rented, ₹75,000/month) |
| Employees | 15 (accounts team of 3, including the student) |
| Annual turnover | ₹8–12 crore (varies by student instance) |
| Financial year | April – March |
| GSTIN | 36AAECM4712F1Z8 (fictional) — **regular scheme, monthly filer** |
| PAN | AAECM4712F (fictional) |
| TAN | HYDM04712B (fictional) |
| TDS sections active | 194C (transport, contractors), 194J (professional fees), 192 (salaries), 194I (rent) |
| Banking | HDFC Bank current a/c ****3417, Balanagar branch + cash credit limit ₹50,00,000 |
| Statutory auditor | M/s Kulkarni & Associates, Chartered Accountants, Hyderabad (fictional) |
| Accounting software | LedgerDesk (the platform's mock ERP) |

### What the company sells

Distribution of electrical goods to electrical contractors, builders, and retail counters:

| Product line | Share of revenue | Typical GST rate |
|---|---|---|
| Cables & wires | ~35% | 18% |
| Switchgear, MCBs, distribution boards | ~25% | 18% |
| Fans & appliances | ~15% | 18% |
| Lighting (LED fixtures, panels) | ~15% | 18% |
| Conduits, accessories, consumables | ~10% | 18% |

Nearly everything trades at 18% GST. This is deliberate — rate complexity is not the
point at Level 2; process discipline is. Higher levels introduce rate edge cases.

### Why this company profile (for scenario authors)

- Trading = widest scenario range: purchases, sales, GST, inventory, debtors, creditors, TDS
- ₹8–12 crore = large enough for complexity, small enough that one accountant owns everything
- Monthly GST filing = a hard deadline every month — the engine of the simulation
- 15 employees = payroll is real but manageable for a junior-mid student

---

## 2. People

### 2.1 The accounts team

| Name | Role | Gross salary/month | Notes |
|---|---|---|---|
| Rajan Mehta | Senior Accounts Manager | ₹85,000 | The student's boss. See [characters.md](characters.md) |
| **The student** | Accounts Executive | ₹35,000 | The player. Joined Day 1 of the simulation |
| Deepak Verma | Accounts Assistant | ₹28,000 | Handles filing, petty cash, bank runs. Junior to the student |

### 2.2 Full employee roster (payroll baseline)

| # | Name | Role | Gross/month |
|---|---|---|---|
| 1 | Vikram Agarwal | Managing Director | ₹1,50,000 |
| 2 | Rajan Mehta | Senior Accounts Manager | ₹85,000 |
| 3 | Arjun Nair | Sales Manager | ₹75,000 |
| 4 | Kavita Reddy | HR & Admin Manager | ₹55,000 |
| 5 | Mohammed Irfan | Purchase Officer | ₹40,000 |
| 6 | *(Student)* | Accounts Executive | ₹35,000 |
| 7 | Sneha Kulkarni | Sales Executive | ₹35,000 |
| 8 | Ravi Teja | Sales Executive | ₹35,000 |
| 9 | Prakash Rao | Warehouse Supervisor | ₹32,000 |
| 10 | Deepak Verma | Accounts Assistant | ₹28,000 |
| 11 | Anil Kumar | Service Technician | ₹25,000 |
| 12 | Lakshmi Devi | Office Admin / Reception | ₹22,000 |
| 13 | Srinu Yadav | Warehouse Assistant | ₹20,000 |
| 14 | Ramesh Goud | Warehouse Assistant | ₹20,000 |
| 15 | Shankar | Delivery Driver | ₹18,000 |
| | **Total gross payroll** | | **₹6,75,000/month** |

Payroll notes for scenario authors:
- Salary structure: Basic 50% / HRA 20% / Special allowance 30% of gross
- PF applies to employees with basic ≤ ₹15,000 wage ceiling per standard rules; PT per Telangana slabs
- TDS u/s 192 applies to the MD, Rajan, Arjun, and Kavita on baseline figures; instance variation can pull others in or out — scenarios must reference roles, not exact tax amounts
- Salaries are paid on the 5th of the following month via HDFC net banking

---

## 3. Vendors (Sundry Creditors)

The five recurring suppliers. **Suresh Electricals is the character vendor** — disputes,
escalations, and supply-stop threats come from Suresh (see [characters.md](characters.md)).

| Vendor | Supplies | Location (GST) | Terms | Baseline monthly purchases |
|---|---|---|---|---|
| Suresh Electricals Pvt Ltd | Switchgear, MCBs | Hyderabad (intra-state: CGST+SGST) | 30 days | ₹18–25 lakh |
| Deccan Wire Industries Ltd | Cables & wires | Hyderabad (intra-state) | 45 days | ₹20–28 lakh |
| Omega Switchgear Ltd | Panels, distribution boards | Mumbai (inter-state: IGST) | 30 days | ₹8–12 lakh |
| Sunrise Lighting Co | LED fixtures | Bengaluru (inter-state: IGST) | 30 days | ₹6–10 lakh |
| Krishna Freight Carriers | Transport (GTA) | Hyderabad | 15 days | ₹60,000–1,00,000 — **RCM + TDS 194C apply** |

Recurring service vendors: CityNet Broadband (internet, ₹4,500/m), SecureSpace
Warehousing (warehouse rent ₹75,000/m — **TDS 194I**), Kulkarni & Associates
(audit fee, annual — **TDS 194J**), GreenClean Services (housekeeping contract,
₹28,000/m — **TDS 194C**).

---

## 4. Customers (Sundry Debtors)

| Customer | Type | Terms | Baseline monthly sales | Payment behaviour |
|---|---|---|---|---|
| BuildRight Constructions Pvt Ltd | B2B — builder | 45 days | ₹15–22 lakh | Slow. Always 10–20 days late |
| Sri Venkateshwara Electricals | B2B — contractor | 30 days | ₹10–15 lakh | Reliable |
| Pavan Electrical Works | B2B — contractor | 30 days | ₹6–9 lakh | Pays in irregular lump sums — allocation headaches |
| Metro Hardware Stores | B2B — retail counter | 15 days | ₹5–8 lakh | Reliable |
| Counter sales (B2C) | Walk-in / cash & UPI | Immediate | ₹18–25 lakh | Daily cash/UPI deposits — reconciliation risk |

---

## 5. Financial Baseline

- Full account list: [chart-of-accounts.md](chart-of-accounts.md)
- Opening trial balance (procedural generation base): [opening-balances.md](opening-balances.md)

Headline baseline figures (as at 1 April, simulation start):

| Item | Baseline |
|---|---|
| Share capital | ₹50,00,000 |
| Reserves & surplus | ₹1,76,63,000 |
| Sundry debtors | ₹2,10,45,000 |
| Sundry creditors | ₹1,58,00,000 |
| Closing inventory | ₹1,85,00,000 |
| HDFC current account | ₹12,35,000 |
| CC utilisation (limit ₹50L) | ₹38,50,000 |
| GST electronic credit ledger (ITC) | ₹8,75,000 |
| Gross margin | 12–15% (varies by instance) |

---

## 6. The Compliance Calendar (the simulation's heartbeat)

| Day of month | Obligation |
|---|---|
| 5th | Salary payment for previous month |
| 7th | TDS deposit for previous month |
| 11th | GSTR-1 filing (previous month) |
| 13th–14th | GSTR-2B available — purchase reconciliation window |
| 20th | GSTR-3B filing + tax payment |
| Month-end | Bank reconciliation, vendor/customer statements, MIS to management |
| Quarterly | TDS returns 24Q/26Q (Level 3+) |

Missing these dates has in-story consequences: interest, late fees, notices, and an
increasingly stressed Rajan.

---

## 7. World Rules for Scenario Authors

1. **Continuity is sacred.** Your scenario inherits the state left by earlier weeks. A Week 6 scenario can (and should) reference the messy handover from Week 1.
2. **Use the named cast.** Vendor disputes come from Suresh Electricals. Payroll inputs come from Kavita. GST questions go to Priya. Don't invent new characters without Core Team approval — the world stays small on purpose.
3. **Reference roles and relationships, not absolute amounts.** Amounts are procedurally varied per student. Write "Suresh's February invoice for MCBs" not "invoice #4471 for ₹2,35,000". The generator binds your scenario to concrete numbers.
4. **Every error must be discoverable.** A seeded error must leave a trail a diligent student can find — an unbalanced reco, a mismatched 2B, a vendor statement that doesn't tie. Never seed an error that only luck can catch.
5. **Consequences are proportionate and realistic.** A wrong TDS rate leads to a short-deduction notice, not a company collapse.
6. **Law references are mandatory.** Every correct treatment cites its section, rule, or circular — that citation is what Domain Reviewers verify and what keeps the platform credible.
