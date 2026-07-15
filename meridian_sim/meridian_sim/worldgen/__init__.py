"""Deterministic world generation.

Same seed -> same company: party balances, open invoices, bank lines, payroll
figures, and the scenario-declared hidden errors. Base figures and variation
bands come from company-bible/opening-balances.md; invariants (trial balance
balances, control accounts tie, statutory dues consistent, all intentional
imbalances declared) are enforced by `selfcheck` before an instance is
accepted.

Everything in this package is pure (no frappe imports, no I/O) except the
`materialize` module, which writes a generated world into an ERPNext site.
Purity is what lets CI golden-test determinism without a bench.
"""

import hashlib
import random

# Turnover scale band per opening-balances.md §4 — sets the 8-12 crore range.
TURNOVER_SCALE = (0.8, 1.2)


def rng_for(seed: int, stream: str) -> random.Random:
    """A deterministic, independent RNG stream for one generation concern.

    Separate streams ("debtors", "invoices:suresh", ...) keep additions to one
    part of the generator from silently reshuffling every other part — the
    property the golden tests lock down.
    """
    digest = hashlib.sha256(f"{seed}:{stream}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def vary(base: int, band: float, rng: random.Random, step: int = 100) -> int:
    """Vary a base amount within ±band, rounded to a realistic step."""
    factor = 1 + rng.uniform(-band, band)
    return max(step, round(base * factor / step) * step)
