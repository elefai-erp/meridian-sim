"""The contributor scorecard and badge system.

Points are never stored as a running counter on Contributor — they're a
ledger (Contributor Point Entry), summed on read. That's what makes both
"monthly" and "all-time" leaderboards possible from the same data, and
means a bug can never leave a contributor's total silently wrong: replay
the ledger and it's always correct.
"""

import frappe
from frappe.utils import get_first_day, get_last_day, now

# Master doc's scorecard, verbatim.
POINTS = {
    "Submit a Scenario": 5,
    "Scenario Approved": 25,
    "High Complexity Scenario": 15,
    "Zero Revisions Required": 10,
    "Top Rated by Review Team": 20,
    "Scenario Used in Certification": 30,
    "Major Revision of Existing Scenario": 10,
}

# Ordered lowest to highest; computed from `scenarios_authored` (published
# count), except Master Scenario Designer which is a manual Core Team call —
# "exceptional quality and impact" isn't a number you can threshold.
BADGE_TIERS = [
    ("bronze_author", "🥉 Bronze Author", 5),
    ("silver_author", "🥈 Silver Author", 15),
    ("gold_author", "🥇 Gold Author", 30),
    ("platinum_author", "💎 Platinum Author", 50),
]
BADGE_PUBLISHED = ("published_contributor", "🏅 Published Contributor", 1)
BADGE_CONTRIBUTOR = ("contributor", "🌱 Contributor", 1)
BADGE_MASTER = ("master_designer", "👑 Master Scenario Designer", None)


def compute_badge(scenarios_submitted: int, scenarios_authored: int, is_master: bool = False) -> dict:
    """The single highest badge earned, plus the full trail for display."""
    if is_master:
        key, label, _ = BADGE_MASTER
        return {"key": key, "label": label, "next": None, "progress": None}

    earned = []
    if scenarios_submitted > 0:
        earned.append(BADGE_CONTRIBUTOR)
    if scenarios_authored >= BADGE_PUBLISHED[2]:
        earned.append(BADGE_PUBLISHED)
    for tier in BADGE_TIERS:
        if scenarios_authored >= tier[2]:
            earned.append(tier)

    if not earned:
        return {"key": None, "label": "Not yet a contributor", "next": BADGE_CONTRIBUTOR[1],
                "progress": (scenarios_submitted, 1)}

    current = earned[-1]
    all_tiers = [BADGE_CONTRIBUTOR, BADGE_PUBLISHED] + BADGE_TIERS
    idx = all_tiers.index(current)
    nxt = all_tiers[idx + 1] if idx + 1 < len(all_tiers) else None
    return {
        "key": current[0], "label": current[1],
        "next": nxt[1] if nxt else None,
        "progress": (scenarios_authored, nxt[2]) if nxt else None,
    }


def award_points(contributor: str, reason: str, reference_scenario: str | None = None) -> int:
    """Insert one ledger entry. `reason` must be a POINTS key."""
    points = POINTS[reason]
    frappe.get_doc({
        "doctype": "Contributor Point Entry", "contributor": contributor,
        "points": points, "reason": reason, "reference_scenario": reference_scenario,
        "awarded_on": now(),
    }).insert(ignore_permissions=True)
    return points


def total_score(contributor: str, month_only: bool = False) -> int:
    clause = " and awarded_on between %(start)s and %(end)s" if month_only else ""
    params = {"c": contributor}
    if month_only:
        params.update(start=get_first_day(now()), end=get_last_day(now()))
    return frappe.db.sql(
        f"select ifnull(sum(points),0) from `tabContributor Point Entry` where contributor=%(c)s{clause}",
        params,
    )[0][0]
