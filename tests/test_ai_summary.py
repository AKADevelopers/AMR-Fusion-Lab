import pytest

from amr_fusion_lab.ai_summary import _parse_ai_json


def test_parse_ai_json_valid():
    raw = '{"executive_summary":"ok","high_priority_genes":[],"disagreement_notes":[],"recommended_review_actions":[],"limitations":[]}'
    parsed = _parse_ai_json(raw)
    assert parsed["executive_summary"] == "ok"


def test_parse_ai_json_missing_keys():
    raw = '{"executive_summary":"ok"}'
    with pytest.raises(ValueError):
        _parse_ai_json(raw)
