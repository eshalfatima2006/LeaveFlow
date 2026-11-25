"""A2.4: the case manifest, the generated module and the spec belong together."""

import hashlib
import json
from pathlib import Path

from django.test import SimpleTestCase

from tests.team.generated import test_generated_api as generated

HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / "generated_cases.json").read_text(encoding="utf-8"))


class GeneratedManifestTests(SimpleTestCase):
    def test_every_manifest_case_is_an_executed_test(self):
        """GEN-001: the manifest lists exactly the generated tests; none is dropped or added by hand."""
        listed = [case["test"] for case in MANIFEST["cases"]]
        present = [
            f"{name}.{method}"
            for name, cls in vars(generated).items()
            if isinstance(cls, type) and issubclass(cls, generated.GeneratedApiTestCase)
            for method in vars(cls) if method.startswith("test_")
        ]
        self.assertEqual(len(listed), len(set(listed)))
        self.assertEqual(sorted(listed), sorted(present))

    def test_module_is_the_unedited_generator_output(self):
        """GEN-001: module and spec hashes match the manifest (fails after a hand edit or a stale generation)."""
        module = Path(generated.__file__).read_text(encoding="utf-8")
        self.assertEqual(hashlib.sha256(module.encode("utf-8")).hexdigest(), MANIFEST["module_sha256"])
        self.assertEqual(generated.SPEC_SHA256, MANIFEST["spec_sha256"])
