"""Performance appraisal: six weighted dimensions over the 3-month record.

Deterministic scoring wherever possible (accuracy from the books, ownership
from who caught each error first, responsiveness from Action Log timestamps);
the AI adapter turns the evidence pack into the narrative appraisal and
conducts the examiner interrogation. No two appraisals are alike because no
two Action Logs are alike.
"""

# Master document §7.2 — changing these weights is a curriculum decision
# owned by the Core Team, not a code change to make casually.
DIMENSION_WEIGHTS = {
    "accuracy": 0.25,
    "ownership": 0.20,
    "responsiveness": 0.15,
    "communication": 0.15,
    "analytical_skill": 0.15,
    "ai_usage_quality": 0.10,
}

OUTCOMES = ("Exceeds Expectations", "Meets Expectations", "Below Expectations")

assert abs(sum(DIMENSION_WEIGHTS.values()) - 1.0) < 1e-9
