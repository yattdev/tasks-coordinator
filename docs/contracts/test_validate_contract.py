#!/usr/bin/env python3
"""Tests for validate_contract.py against fixtures in fixtures/.

Stdlib-only (unittest). Run with:
    python3 -m unittest docs/contracts/test_validate_contract.py -v
or, from this directory:
    python3 test_validate_contract.py
"""

import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import validate_contract as vc  # noqa: E402

CANONICAL = os.path.join(HERE, "coordinator-policy-contract.json")
FIXTURES = os.path.join(HERE, "fixtures")


def load(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as fh:
        return json.load(fh)


def load_canonical():
    with open(CANONICAL, encoding="utf-8") as fh:
        return json.load(fh)


class TestCanonicalContract(unittest.TestCase):
    def test_canonical_contract_is_valid(self):
        failures = vc.validate_contract(load_canonical())
        self.assertEqual(failures, [], f"canonical contract must be valid, got: {failures}")

    def test_canonical_digest_matches_recomputation(self):
        contract = load_canonical()
        self.assertEqual(contract["digest"], vc.compute_digest(contract))


class TestFixtureContracts(unittest.TestCase):
    def test_valid_contract_fixture_passes(self):
        failures = vc.validate_contract(load("valid_contract.json"))
        self.assertEqual(failures, [])

    def test_stale_version_is_rejected(self):
        failures = vc.validate_contract(load("stale_version_contract.json"))
        checks = [c for c, _ in failures]
        self.assertIn("stale_version", checks)

    def test_stale_digest_is_rejected(self):
        failures = vc.validate_contract(load("stale_digest_contract.json"))
        checks = [c for c, _ in failures]
        self.assertIn("stale_digest", checks)

    def test_missing_required_invariant_is_rejected(self):
        failures = vc.validate_contract(load("missing_invariant_contract.json"))
        checks = [c for c, _ in failures]
        self.assertIn("missing_required_invariant", checks)

    def test_unknown_required_field_is_rejected(self):
        failures = vc.validate_contract(load("unknown_required_field_contract.json"))
        checks = [c for c, _ in failures]
        self.assertIn("unknown_required_field", checks)

    def test_exclusion_leaking_secret_shaped_value_is_rejected(self):
        failures = vc.validate_contract(load("exclusion_leak_contract.json"))
        checks = [c for c, _ in failures]
        self.assertIn("exclusion_leaks_secret", checks)

    def test_bare_exclusion_category_names_are_not_flagged(self):
        # Regression guard for the opposite failure mode: legitimate bare
        # category names ("secrets", "credentials") must never themselves
        # trip the leak check.
        failures = vc.validate_contract(load_canonical())
        checks = [c for c, _ in failures]
        self.assertNotIn("exclusion_leaks_secret", checks)


class TestPluginSnapshot(unittest.TestCase):
    def test_valid_plugin_snapshot_passes(self):
        contract = load_canonical()
        snapshot = load("valid_plugin_snapshot.json")
        failures = vc.validate_plugin_snapshot(contract, snapshot)
        self.assertEqual(failures, [])

    def test_contradictory_plugin_snapshot_is_rejected(self):
        contract = load_canonical()
        snapshot = load("contradictory_plugin_snapshot.json")
        failures = vc.validate_plugin_snapshot(contract, snapshot)
        checks = [c for c, _ in failures]
        self.assertIn("contradictory_plugin_prompt_default", checks)


class TestWorkspaceOverlay(unittest.TestCase):
    def test_narrowing_overlay_passes(self):
        contract = load_canonical()
        overlay = load("narrowing_overlay.json")
        failures = vc.validate_overlay(contract, overlay)
        self.assertEqual(failures, [])

    def test_widening_overlay_is_rejected(self):
        contract = load_canonical()
        overlay = load("widening_overlay.json")
        failures = vc.validate_overlay(contract, overlay)
        checks = [c for c, _ in failures]
        self.assertIn("overlay_widens_authority", checks)
        # Both the cross-workspace flip and the added decidable-example
        # should each independently trip the same check category.
        self.assertGreaterEqual(checks.count("overlay_widens_authority"), 2)


class TestCli(unittest.TestCase):
    """Exercises the actual CLI entry point (subprocess) for a couple of
    cases, so the argparse wiring itself is covered, not just the importable
    functions."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, os.path.join(HERE, "validate_contract.py"), *args],
            capture_output=True,
            text=True,
        )

    def test_cli_contract_valid_exit_zero(self):
        result = self._run("contract", "--contract", CANONICAL)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK", result.stdout)

    def test_cli_contract_invalid_exit_one(self):
        result = self._run(
            "contract", "--contract", os.path.join(FIXTURES, "stale_digest_contract.json")
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("stale_digest", result.stderr)

    def test_cli_contract_exclusion_leak_exit_one(self):
        result = self._run(
            "contract", "--contract", os.path.join(FIXTURES, "exclusion_leak_contract.json")
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("exclusion_leaks_secret", result.stderr)

    def test_cli_plugin_snapshot_contradictory_exit_one(self):
        result = self._run(
            "plugin-snapshot",
            "--contract", CANONICAL,
            "--snapshot", os.path.join(FIXTURES, "contradictory_plugin_snapshot.json"),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("contradictory_plugin_prompt_default", result.stderr)

    def test_cli_overlay_widening_exit_one(self):
        result = self._run(
            "overlay",
            "--contract", CANONICAL,
            "--overlay", os.path.join(FIXTURES, "widening_overlay.json"),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("overlay_widens_authority", result.stderr)


if __name__ == "__main__":
    unittest.main()
