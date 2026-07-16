# Reviewing Submissions — Admin Runbook

How a System Manager (today: the Core Team) processes what comes in through
the public site's forms. No email/SMTP is required — every submission
assigns a **ToDo** to every System Manager user, which shows up in the
Frappe desk notification bell (top right, `/app`) immediately.

## Where things land

| Form | Doctype | Desk list view |
|---|---|---|
| `/students/apply` | Student Application | `/app/student-application` |
| `/contribute/apply` | Contributor Application | `/app/contributor-application` |
| `/contribute/submit` | Scenario Submission | `/app/scenario-submission` |

Filter any list by `status = New` / `Submitted` to see what's unactioned.

## The contributor scorecard

Points are a ledger (`Contributor Point Entry`, one row per award — never a
counter you can get out of sync), summed live for both the all-time and
current-month leaderboards.

| Activity | Points | Awarded when |
|---|---:|---|
| Submit a Scenario | 5 | Automatically, the moment the form is submitted |
| Scenario Approved | 25 | Automatically, the moment you save status as `Approved`/`Live` |
| High Complexity Scenario | +15 | If you tick `is_high_complexity` **at the same save** as approving |
| Zero Revisions Required | +10 | If you tick `zero_revisions_required` at approval |
| Top Rated by Review Team | +20 | If you tick `top_rated_by_review_team` at approval |
| Scenario Used in Certification | +30 | If you tick `used_in_certification` at approval |
| Major Revision of Existing Scenario | 10 | Tick `major_revision` on an already-approved submission, any time |

**Important:** the four approval-time bonus checkboxes are a one-shot
snapshot — they're only read the instant status first reaches
`Approved`/`Live` (guarded by the hidden `points_awarded` field, so this
can't double-fire). If you realize afterward that a scenario deserved "Top
Rated," ticking the box later won't retroactively award it — use `major_revision`
for a substantive after-the-fact credit instead, or manually add a
`Contributor Point Entry` row.

## Badges (computed live, never stored)

| Badge | Requirement |
|---|---|
| 🌱 Contributor | First submission (`scenarios_submitted` ≥ 1) |
| 🏅 Published Contributor | First **published** scenario (`scenarios_authored` ≥ 1) |
| 🥉 Bronze Author | 5 published |
| 🥈 Silver Author | 15 published |
| 🥇 Gold Author | 30 published |
| 💎 Platinum Author | 50 published |
| 👑 Master Scenario Designer | Manual only — set `role = "Core Contributor"` **and** `scenarios_authored ≥ 50`; there's no formula for "exceptional quality and impact" |

A contributor's badge, both leaderboards, and their downloadable LinkedIn
badge image (`/contributor` → "Download LinkedIn Badge") all read
`scenarios_submitted` / `scenarios_authored` live — nothing to keep in sync.

## Reviewing a scenario submission

1. Open the record in `/app/scenario-submission`. Read `situation`,
   `student_task`, `correct_treatment`, `law_reference`, and Rajan's advice
   fields — this is the plain-English version of what a contribution-kit
   scenario card needs (see [contribution-kit/scenario-template.md](../contribution-kit/scenario-template.md)).
2. Verify the law reference is real and correctly applied. This is the one
   step that can't be skipped — a wrong citation published to students is
   the platform's worst failure mode.
3. Tick any bonus boxes that apply (High Complexity / Zero Revisions / Top
   Rated / Used in Certification) — do this **before** saving with the new status.
4. Set **Status**:
   - `Under Review` — you're actively checking it / went back to the author
     with questions (use `reviewer_notes` for the question)
   - `Approved` — technically sound. **Saving with this status
     automatically**: finds-or-creates the author's Contributor record,
     provisions their `/contributor` portal login on first approval (a temp
     password is relayed to you via the same ToDo notification — pass it on
     over WhatsApp/email, there's no SMTP), increments `scenarios_authored`,
     and awards the point bonuses above. This is what makes them appear on
     `/contribute/leaderboard` with a badge.
   - `Rejected` — not usable; leave a reason in `reviewer_notes`
   - `Live` — same auto-crediting as Approved; use once the scenario is
     actually deployed (see "Turning an approval into a real scenario" below)
5. The submission is *not* automatically converted into a
   `scenarios/<domain>/*.yaml` file yet — that conversion (this doctype's
   fields → the schema in `scenarios/schema.json`) is still a manual step
   for a Core Team member, or a good first automation to build next.

## Turning an approved submission into a real scenario file

Until the auto-conversion job exists, do this by hand:

1. Copy the approved submission's fields into a new file under
   `scenarios/<domain>/<kebab-case-title>.yaml`, following
   [contribution-kit/scenario-template.md](../contribution-kit/scenario-template.md).
   `domain` must be one of the slugs in [meridian_sim/taxonomy.py](../meridian_sim/meridian_sim/taxonomy.py)
   (33 domains — purchase cycle through revenue recognition; see that file
   for the full list).
2. Fill `authored_by` (name + membership_no from the submission) and
   `reviewed_by` (you, or the assigned Domain Reviewer) with real details.
3. Run `python3 tools/validate_scenarios.py` — it must pass before merging.
4. Commit and push. Set the Scenario Submission's status to `Live`.

## Contributor logins — separate from student logins

Contributors get their own portal at `/contributor`, distinct from the
student `/mydesk`. The role is `Meridian Contributor` (no Frappe desk
access — Website User only, so they can't see `/app`).

- A login is created **automatically** the first time someone either
  submits a scenario or gets a Contributor Application approved —
  whichever comes first.
- Since there's no outgoing Email Account configured on this site, the temp
  password is **not emailed**. It's included in the admin ToDo notification
  text — copy it from there and relay it to the contributor yourself
  (WhatsApp matches the platform's existing contributor-communication
  model; see master doc §9).
- The shared site nav's "My Dashboard" link (and `/go`) automatically
  routes a logged-in contributor to `/contributor` and a logged-in student
  to `/mydesk` — no manual configuration needed per user.

## Reviewing applications

Student and Contributor applications are simpler — read, then set status.
Approving a **Contributor Application** finds-or-creates their Contributor
record and provisions their login the same way (0 scenarios authored until
their first submission is approved — they'll show the 🌱 Contributor badge
only once they've actually submitted something). Approving a **Student
Application** does *not* yet provision a Sim Instance automatically —
enrollment is still a manual step (create the `Sim Instance` record, or run
`meridian_sim.demo.setup_demo` for a quick seeded instance) until the
enrollment flow is built.

## What's automatic vs. manual today

| Step | Automatic? |
|---|---|
| Notify System Managers on new submission/application | ✅ Yes — ToDo, no SMTP needed |
| Provision a contributor's `/contributor` login (first submission or approved application) | ✅ Yes |
| Award scorecard points (submission, approval, bonuses, major revision) | ✅ Yes |
| Compute badge tier + leaderboard rank (all-time and monthly) | ✅ Yes, live — nothing stored/stale |
| Generate a downloadable LinkedIn badge image | ✅ Yes — `/contributor` → Download LinkedIn Badge |
| Convert an approved submission into a `scenarios/*.yaml` file | ❌ Manual (see above) |
| Provision a student's Sim Instance on approval | ❌ Manual |
| Email the applicant/contributor anything | ❌ Not built — no outgoing Email Account configured; ToDo + manual relay is the current path |
