"""Determinism tests for the pure worldgen helpers.

These run without a Frappe bench (CI runs them with plain unittest). When the
full generator lands, golden-file tests join them here: a generator change
that silently alters existing worlds must fail.
"""

import unittest

from meridian_sim.worldgen import rng_for, vary


class TestDeterminism(unittest.TestCase):
    def test_same_seed_same_stream_is_identical(self):
        a = [rng_for(42, "debtors").random() for _ in range(100)]
        b = [rng_for(42, "debtors").random() for _ in range(100)]
        self.assertEqual(a, b)

    def test_streams_are_independent(self):
        self.assertNotEqual(
            rng_for(42, "debtors").random(),
            rng_for(42, "creditors").random(),
        )

    def test_seeds_differ(self):
        self.assertNotEqual(
            rng_for(42, "debtors").random(),
            rng_for(43, "debtors").random(),
        )

    def test_vary_stays_in_band_and_on_step(self):
        rng = rng_for(7, "vary")
        for _ in range(1000):
            v = vary(1_000_000, 0.15, rng)
            self.assertGreaterEqual(v, 850_000)
            self.assertLessEqual(v, 1_150_000)
            self.assertEqual(v % 100, 0)

    def test_vary_is_deterministic(self):
        self.assertEqual(
            vary(9_240_000, 0.15, rng_for(11, "x")),
            vary(9_240_000, 0.15, rng_for(11, "x")),
        )


if __name__ == "__main__":
    unittest.main()
