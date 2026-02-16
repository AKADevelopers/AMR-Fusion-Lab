import pandas as pd

from amr_fusion_lab.quality import normalize_and_filter_hits


def test_quality_filters_and_deduplication():
    df = pd.DataFrame([
        {"sample_id": "S1", "tool": "resfinder", "gene": "blaTEM-1", "identity": "99.0", "coverage": "98.0"},
        {"sample_id": "S1", "tool": "resfinder", "gene": "blaTEM-1", "identity": "99.0", "coverage": "98.0"},
        {"sample_id": "S1", "tool": "amrfinder", "gene": "tetA", "identity": "85.0", "coverage": "65.0"},
    ])

    out = normalize_and_filter_hits(df, min_identity=90, min_coverage=70, deduplicate=True)
    assert len(out) == 1
    assert out.iloc[0]["gene"] == "blaTEM-1"
