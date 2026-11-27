"""Intentional failing check used as documented CI-blocking evidence.

This file exists only on the evidence/blocked-quality-gate branch. It must not
be merged into dev or main.
"""


def test_documented_quality_gate_block():
    """Keep this evidence PR red so the required gate blocks it."""
    assert False, "Intentional failure for the blocked-PR evidence"
