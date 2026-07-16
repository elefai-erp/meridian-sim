# Reviewing Submissions — Admin Runbook

How a System Manager (today: the Core Team) processes what comes in through
the public site's three forms. No email/SMTP is required — every submission
assigns a **ToDo** to every System Manager user, which shows up in the
Frappe desk notification bell (top right, `/app`) immediately.

## Where things land

| Form | Doctype | Desk list view |
|---|---|---|
| `/students/apply` | Student Application | `/app/student-application` |
| `/contribute/apply` | Contributor Application | `/app/contributor-application` |
| `/contribute/submit` | Scenario Submission | `/app/scenario-submission` |

Filter any list by `status = New` / `Submitted` to see what's unactioned.

## Reviewing a scenario submission

1. Open the record in `/app/scenario-submission`. Read `situation`,
   `student_task`, `correct_treatment`, `law_reference`, and Rajan's advice
   fields — this is the plain-English version of what a contribution-kit
   scenario card needs (see [contribution-kit/scenario-template.md](../contribution-kit/scenario-template.md)).
2. Verify the law reference is real and correctly applied. This is the one
   step that can't be skipped — a wrong citation published to students is
   the platform's worst failure mode.
3. Set **Status**:
   - `Under Review` — you're actively checking it / went back to the author
     with questions (use `reviewer_notes` for the question)
   - `Approved` — technically sound, ready to be turned into a real
     scenario file. **Saving with this status automatically creates or
     credits the author's Contributor record** (matched by membership
     number, falling back to name) and bumps `scenarios_authored` —
     this is what makes them appear on `/contribute/leaderboard`.
   - `Rejected` — not usable; leave a reason in `reviewer_notes`
   - `Live` — same auto-credit as Approved; use once the scenario is
     actually deployed (see "Turning an approval into a real scenario" below)
4. The submission is *not* automatically converted into a
   `scenarios/<domain>/*.yaml` file yet — that conversion (this doctype's
   fields → the schema in `scenarios/schema.json`) is still a manual step
   for a Core Team member, or a good first automation to build next.

## Turning an approved submission into a real scenario file

Until the auto-conversion job exists, do this by hand:

1. Copy the approved submission's fields into a new file under
   `scenarios/<domain>/<kebab-case-title>.yaml`, following
   [contribution-kit/scenario-template.md](../contribution-kit/scenario-template.md).
2. Fill `authored_by` (name + membership_no from the submission) and
   `reviewed_by` (you, or the assigned Domain Reviewer) with real details.
3. Run `python3 tools/validate_scenarios.py` — it must pass before merging.
4. Commit and push. Set the Scenario Submission's status to `Live`.

## Reviewing applications

Student and Contributor applications are simpler — read, then set status.
Approving a **Contributor Application** auto-creates their Contributor
record the same way (0 scenarios authored until their first submission is
approved). Approving a **Student Application** does *not* yet provision a
Sim Instance automatically — enrollment is still a manual step (create the
`Sim Instance` record, or run `meridian_sim.demo.setup_demo` for a quick
seeded instance) until the enrollment flow is built.

## What's automatic vs. manual today

| Step | Automatic? |
|---|---|
| Notify System Managers on new submission | ✅ Yes — ToDo, no SMTP needed |
| Credit a Contributor's scenario count on Approved/Live | ✅ Yes |
| Appear on `/contribute/leaderboard` | ✅ Yes, once credited |
| Convert an approved submission into a `scenarios/*.yaml` file | ❌ Manual (see above) |
| Provision a student's Sim Instance on approval | ❌ Manual |
| Email the applicant that they were approved | ❌ Not built — no outgoing Email Account configured yet |
