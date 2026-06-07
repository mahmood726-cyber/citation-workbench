"""Unit tests for the citation-workbench builder's pure functions.

Imports the build module (main() is __name__-guarded, so import is
side-effect-free) and exercises the text/metadata helpers that have stable
contracts.
"""
import importlib.util
import os
import sys

import pytest

_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "scripts", "build_citation_workbench.py")
_spec = importlib.util.spec_from_file_location("build_citation_workbench", _SCRIPT)
bcw = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = bcw
_spec.loader.exec_module(bcw)


def test_compact_collapses_whitespace():
    assert bcw.compact("a  b\n c\t d") == "a b c d"
    assert bcw.compact(None) == ""
    assert bcw.compact("   ") == ""


def test_bibtex_escape_escapes_braces_and_backslash():
    assert bcw.bibtex_escape("{x}") == "\\{x\\}"
    assert bcw.bibtex_escape("a\\b") == "a\\\\b"


def test_quote_yaml_wraps_and_escapes_quotes():
    out = bcw.quote_yaml('he said "hi"')
    assert out.startswith('"') and out.endswith('"')
    assert '\\"' in out  # inner quotes escaped


def test_publication_year_extracts_or_defaults():
    assert bcw.publication_year({"lastTouch": "2023-05-01"}) == 2023
    assert bcw.publication_year({"generatedAt": "2019-12-31T10:00:00"}) == 2019
    assert bcw.publication_year({}) == 2026  # documented fallback


def test_release_date_passthrough_and_default():
    assert bcw.release_date({"lastTouch": "2024-02-02"}) == "2024-02-02"
    assert bcw.release_date({"generatedAt": "2024-02-02T09:00:00Z"}) == "2024-02-02"
    assert bcw.release_date({}) == "2026-03-30"  # documented fallback


def test_resource_type_general_mapping():
    assert bcw.resource_type_general("Public dataset", "Tier 1") == "Dataset"
    assert bcw.resource_type_general("HTML app", "Tier 1") == "Software"
    assert bcw.resource_type_general("ML model", "Tier 1") == "Model"
    assert bcw.resource_type_general("anything", "Tier 8") == "Text"
    assert bcw.resource_type_general("research project", "Tier 1") == "Project"
    assert bcw.resource_type_general("", "Tier 1") == "Other"


def test_cff_and_citeproc_types_cover_all_resource_types():
    # every value resource_type_general can emit must map without KeyError
    for rt in ("Dataset", "Text", "Model", "Software", "Project", "Other"):
        assert bcw.cff_type(rt) in {"dataset", "software", "generic"}
        assert bcw.citeproc_type(rt) in {"dataset", "report", "software", "webpage"}


def test_readiness_band_thresholds():
    assert bcw.readiness_band(80) == "high"
    assert bcw.readiness_band(79) == "medium"
    assert bcw.readiness_band(55) == "medium"
    assert bcw.readiness_band(54) == "low"
    assert bcw.readiness_band(0) == "low"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
