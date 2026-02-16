import pandas as pd

from amr_fusion_lab.fusion import build_gene_summary, build_disagreement_table


def test_gene_summary_and_disagreements():
    df = pd.DataFrame(
        [
            {"sample_id": "S1", "tool": "resfinder", "gene": "blaTEM-1", "drug_class_normalized": "beta-lactam", "identity": 99.0, "coverage": 98.0, "confidence_score": 1.0},
            {"sample_id": "S1", "tool": "amrfinder", "gene": "blaTEM-1", "drug_class_normalized": "beta-lactam", "identity": 98.0, "coverage": 97.0, "confidence_score": 1.0},
            {"sample_id": "S1", "tool": "resfinder", "gene": "tetA", "drug_class_normalized": "tetracycline", "identity": 91.0, "coverage": 75.0, "confidence_score": 0.65},
        ]
    )

    g = build_gene_summary(df)
    assert len(g) == 2

    bla = g[g["gene"] == "blaTEM-1"].iloc[0]
    assert bla["tool_count"] == 2
    assert bla["consensus_level"] == "multi-tool"
    assert bla["normalized_drug_classes"] == "beta-lactam"
    assert bla["weighted_consensus_score"] >= 0.95
    assert bla["consensus_tier"] in {"high", "very-high"}

    d = build_disagreement_table(g)
    assert len(d) == 1
    assert d.iloc[0]["gene"] == "tetA"
