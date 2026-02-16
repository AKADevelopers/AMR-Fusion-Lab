from __future__ import annotations

import pandas as pd

# Baseline reliability priors (tunable with validation studies)
TOOL_RELIABILITY = {
    "amrfinder": 1.00,
    "rgi": 0.95,
    "resfinder": 0.92,
}


def build_gene_summary(scored_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate row-level hits into gene-level fused evidence."""
    if scored_df.empty:
        return pd.DataFrame(
            columns=[
                "sample_id",
                "gene",
                "tools_detected",
                "tool_count",
                "best_identity",
                "best_coverage",
                "max_confidence_score",
                "consensus_level",
            ]
        )

    work = scored_df.copy()
    work["tool_reliability"] = work["tool"].map(lambda t: TOOL_RELIABILITY.get(str(t), 0.85))
    work["weighted_row_score"] = work["confidence_score"].fillna(0.0) * work["tool_reliability"]

    g = (
        work.groupby(["sample_id", "gene"], dropna=False)
        .agg(
            tools_detected=("tool", lambda x: ",".join(sorted(set(map(str, x))))),
            tool_count=("tool", "nunique"),
            normalized_drug_classes=(
                "drug_class_normalized",
                lambda x: ",".join(sorted({str(v) for v in x if pd.notna(v)})) if len(x) else "",
            ),
            best_identity=("identity", "max"),
            best_coverage=("coverage", "max"),
            max_confidence_score=("confidence_score", "max"),
            weighted_consensus_score=("weighted_row_score", "max"),
        )
        .reset_index()
    )

    def _consensus(n: int) -> str:
        if n >= 2:
            return "multi-tool"
        return "single-tool"

    def _tier(score: float) -> str:
        if score >= 0.90:
            return "very-high"
        if score >= 0.75:
            return "high"
        if score >= 0.55:
            return "moderate"
        return "low"

    g["consensus_level"] = g["tool_count"].apply(_consensus)
    g["consensus_tier"] = g["weighted_consensus_score"].apply(lambda x: _tier(float(x)))
    g["weighted_consensus_score"] = g["weighted_consensus_score"].round(3)
    return g


def build_disagreement_table(gene_summary: pd.DataFrame) -> pd.DataFrame:
    """Return genes detected by only one tool for quick manual review."""
    if gene_summary.empty:
        return gene_summary.copy()
    return gene_summary[gene_summary["tool_count"] == 1].copy()
