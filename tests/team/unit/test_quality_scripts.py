"""Exercise fail-closed quality gates with deliberately failing report inputs."""

import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[3]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/sqe" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QualityGateTests(SimpleTestCase):
    def mutation(self, data):
        gate = load("check_mutation_threshold")
        with patch("sys.argv", ["check_mutation_threshold.py"]), patch.object(Path, "exists", return_value=True), patch.object(Path, "read_text", return_value=json.dumps(data)):
            return gate.main()

    def test_mutation_above_threshold_passes(self):
        self.assertEqual(self.mutation({"total": 100, "killed": 90, "survived": 10}), 0)

    def test_mutation_below_threshold_fails(self):
        self.assertEqual(self.mutation({"total": 100, "killed": 84, "survived": 16}), 1)

    def test_timeout_cannot_be_hidden_by_high_tested_score(self):
        self.assertEqual(self.mutation({"total": 101, "killed": 99, "survived": 1, "timeout": 1}), 1)

    def test_unclassified_mutants_fail(self):
        self.assertEqual(self.mutation({"total": 101, "killed": 99, "survived": 1}), 1)

    def test_missing_coverage_file_fails(self):
        gate = load("check_coverage")
        with patch.object(Path, "exists", return_value=False):
            self.assertEqual(gate.main(), 1)
