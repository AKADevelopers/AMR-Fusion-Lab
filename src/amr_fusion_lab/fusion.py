from __future__ import annotations

import pandas as pd


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

    g = (
        scored_df.groupby(["sample_id", "gene"], dropna=False)
        .agg(
            tools_detected=("tool", lambda x: ",".join(sorted(set(map(str, x))))),
            tool_count=("tool", "nunique"),
            best_identity=("identity", "max"),
            best_coverage=("coverage", "max"),
            max_confidence_score=("confidence_score", "max"),
        )
        .reset_index()
    )

    def _consensus(n: int) -> str:
        if n >= 2:
            return "multi-tool"
        return "single-tool"

    g["consensus_level"] = g["tool_count"].apply(_consensus)
    return g


def build_disagreement_table(gene_summary: pd.DataFrame) -> pd.DataFrame:
    """Return genes detected by only one tool for quick manual review."""
    if gene_summary.empty:
        return gene_summary.copy()
    return gene_summary[gene_summary["tool_count"] == 1].copy()
