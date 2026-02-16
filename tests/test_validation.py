import pandas as pd

from amr_fusion_lab.validation import validate_canonical_hits


def test_validation_warns_on_bad_ranges():
    df = pd.DataFrame([
        {"sample_id": "S1", "tool": "x", "gene": "bla", "identity": 120, "coverage": -1}
    ])
    msgs = validate_canonical_hits(df, strict=False)
    assert any("identity outside 0-100" in m for m in msgs)
    assert any("coverage outside 0-100" in m for m in msgs)


def test_validation_strict_escalates_warning():
    df = pd.DataFrame([
        {"sample_id": "S1", "tool": "x", "gene": None, "identity": 99, "coverage": 99}
    ])
    msgs = validate_canonical_hits(df, strict=True)
    assert any(m.startswith("ERROR:") for m in msgs)
