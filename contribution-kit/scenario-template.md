# Scenario Card Template

> This is the structured format every scenario ends up in. **CA contributors do not
> fill this file** — they fill the plain-English web form (see
> [how-to-contribute.md](how-to-contribute.md)); a Contribution Coordinator (or
> automation) converts the form into a YAML file matching this template, and CI
> validates it against [`scenarios/schema.json`](../scenarios/schema.json).

## The template (annotated)

```yaml
# scenarios/<domain>/<kebab-case-slug>.yaml
title: The Freight on the Purchase Invoice     # Short, evocative, no spoilers
domain: gst              # one of the domains in meridian_sim/taxonomy.py — purchase-cycle,
                         # sales-cycle, inventory, bank-reco, petty-cash, fixed-assets,
                         # journal-entries, credit-notes, debit-notes, customer-outstanding,
                         # vendor-payments, vendor-mgmt, payroll, gst, tds, tax-adjustments,
                         # month-end-closing, year-end-closing, finalization,
                         # revenue-recognition, accrual-provision, financial-statements,
                         # budget-vs-actual, mis, manufacturing-costing, multi-branch,
                         # intercompany, foreign-currency, audit-internal-control,
                         # fraud-detection, error-rectification, erp-workflow,
                         # business-decisions (33 total — see taxonomy.py for the full list)
level: junior-accountant # accounts-assistant | junior-accountant | senior-accountant |
                         # accounts-manager | finance-controller
difficulty: junior       # junior | mid | senior
week: 2                  # 1–12, where in the 3-month arc this fires
status: draft            # draft | in-review | approved | live | needs-update

trigger:                 # What starts this — the student never sees "a task"
  channel: drivebox      # inboxpro | pingdesk | drivebox | taxportal | ledgerdesk | storyline
  event: >
    Purchase invoice from Omega Switchgear arrives in DriveBox with freight
    charged as a separate line by a GTA, consignment note attached.

hidden_error: >          # What is seeded wrong in the data (omit if the scenario
                         # seeds no error). Written for the generator, precise.
  The freight line references Krishna Freight Carriers (GTA); RCM liability is
  NOT self-invoiced in the books. Books look fine until 3B preparation.

student_task: >          # What a competent student is expected to do
  Enter the purchase correctly, identify that GTA freight attracts GST under
  reverse charge, create the RCM self-invoice, and claim ITC on it.

common_wrong: >          # What a lazy or rushed student typically does
  Adds freight to purchase cost with no RCM entry, or posts freight to Freight
  Inward and ignores GST on it entirely.

correct_treatment: >     # The right answer, with the citation that proves it
  GTA freight (consignment note issued) attracts GST @5% under RCM per
  Notification 13/2017-CT(R); recipient self-invoices u/s 31(3)(f), pays in cash
  ledger, and claims ITC per s.16 read with s.17(5) — eligible here.
law_reference: "Notification 13/2017-CT(R); s.9(3) CGST Act; s.31(3)(f); s.16"

rajan:
  asked_probability: high   # how likely a student is to ask him (guides authoring effort)
  is_wrong_here: true       # Rajan is right ~60-70% platform-wide; mark this instance
  advice: >
    Freight? Add it to purchase cost only. We always do it that way. GST on
    freight all that is not needed for small amounts.
  why_wrong: >
    Oversimplified + outdated. RCM on GTA freight applies regardless of amount
    once a consignment note exists; skipping the self-invoice understates 3B
    liability and surfaces in the 2B/3B comparison at audit.

consequence:
  surfaces_week: 10
  how: >
    GSTR-3B vs books RCM mismatch appears during 2B reconciliation; auditor
    (Week 11) asks for the RCM self-invoice register the student never created.
  severity: moderate     # minor | moderate | major

appraisal_notes: >       # What the appraisal engine should credit / penalise
  Credit: caught RCM without prompting; verified Rajan's advice against the
  notification. Penalise: followed Rajan blindly; RCM surfaced only when the
  auditor asked.

authored_by:
  name: ""               # CA Full Name
  membership_no: ""      # ICAI/ICMAI membership number
reviewed_by:
  name: ""
  membership_no: ""
approved_date: null      # YYYY-MM-DD, set on approval
last_verified: null      # YYYY-MM-DD, updated at every re-verification
next_review_due: null    # approved_date + 12 months, or earlier if law changes
```

## Field-by-field guidance

- **Write amounts as relationships, never absolutes.** The generator binds your scenario to each student's unique numbers. "Suresh's February invoice for MCBs" ✔ · "invoice #4471 for ₹2,35,000" ✘
- **`hidden_error`** must be *discoverable* — it has to leave a trail (unbalanced reco, 2B mismatch, statement that doesn't tie). Never an error only luck can find. It must also be **declared** so the world generator's self-check knows the imbalance is intentional.
- **`correct_treatment` + `law_reference`** are what your Domain Reviewer verifies, and what students who research properly will find. Be precise; include circular/notification numbers.
- **`rajan`** — follow the [voice guide](rajan-character-guide.md). One of the four flavours, full confidence, disprovable.
- **`consequence`** — realistic and proportionate. Wrong TDS rate → short-deduction complaint and a notice, not a company collapse. Must name the week and the channel it surfaces through.
- **Continuity** — check the [Company Bible](../company-bible/meridian-trading.md) for the cast, vendor terms, and world rules. Your scenario inherits the mess earlier weeks left behind.
