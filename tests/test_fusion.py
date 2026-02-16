import pandas as pd

from amr_fusion_lab.fusion import build_gene_summary, build_disagreement_table


def test_gene_summary_and_disagreements():
    df = pd.DataFrame(
        [
            {"sample_id": "S1", "tool": "resfinder", "gene": "blaTEM-1", "identity": 99.0, "coverage": 98.0, "confidence_score": 1.0},
            {"sample_id": "S1", "tool": "amrfinder", "gene": "blaTEM-1", "identity": 98.0, "coverage": 97.0, "confidence_score": 1.0},
            {"sample_id": "S1", "tool": "resfinder", "gene": "tetA", "identity": 91.0, "coverage": 75.0, "confidence_score": 0.65},
        ]
    )

    g = build_gene_summary(df)
    assert len(g) == 2

    bla = g[g["gene"] == "blaTEM-1"].iloc[0]
    assert bla["tool_count"] == 2
    assert bla["consensus_level"] == "multi-tool"

    d = build_disagreement_table(g)
    assert len(d) == 1
    assert d.iloc[0]["gene"] == "tetA"
