from amr_fusion_lab.scoring import score_hits
import pandas as pd


def test_scoring_has_confidence_columns():
    df = pd.DataFrame([
        {"gene": "blaTEM-1", "identity": 99.0, "coverage": 98.0},
        {"gene": "tetA", "identity": 91.0, "coverage": 75.0},
    ])
    out = score_hits(df)
    assert "confidence" in out.columns
    assert "confidence_score" in out.columns
