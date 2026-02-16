from __future__ import annotations

from pathlib import Path
import pandas as pd


def write_outputs(
    df: pd.DataFrame,
    outdir: str,
    sample_id: str,
    gene_summary: pd.DataFrame | None = None,
    disagreements: pd.DataFrame | None = None,
) -> None:
    p = Path(outdir)
    p.mkdir(parents=True, exist_ok=True)

    df.to_csv(p / f"{sample_id}.amr_fused.csv", index=False)
    df.to_json(p / f"{sample_id}.amr_fused.json", orient="records", indent=2)

    if gene_summary is not None:
        gene_summary.to_csv(p / f"{sample_id}.gene_summary.csv", index=False)
        gene_summary.to_json(p / f"{sample_id}.gene_summary.json", orient="records", indent=2)

    if disagreements is not None:
        disagreements.to_csv(p / f"{sample_id}.disagreements.csv", index=False)

    summary = _markdown_summary(df, sample_id, gene_summary, disagreements)
    (p / f"{sample_id}.report.md").write_text(summary, encoding="utf-8")


def _markdown_summary(
    df: pd.DataFrame,
    sample_id: str,
    gene_summary: pd.DataFrame | None,
    disagreements: pd.DataFrame | None,
) -> str:
    total = len(df)
    by_conf = df["confidence"].value_counts(dropna=False).to_dict() if "confidence" in df.columns else {}
    top_genes = ", ".join(df["gene"].dropna().astype(str).head(10).tolist())

    unique_genes = len(gene_summary) if gene_summary is not None else "N/A"
    disagreement_count = len(disagreements) if disagreements is not None else "N/A"

    lines = [
        f"# AMR Fusion Report - {sample_id}",
        "",
        f"- Total tool-level hits: **{total}**",
        f"- Unique genes: **{unique_genes}**",
        f"- Confidence counts: **{by_conf}**",
        f"- Single-tool disagreement candidates: **{disagreement_count}**",
        f"- Top genes (first 10): {top_genes if top_genes else 'N/A'}",
        "",
        "## Notes",
        "- This is a baseline rule-based report.",
        "- Review `*.disagreements.csv` for single-tool detections.",
        "- Use fused CSV/JSON for auditability.",
    ]
    return "\n".join(lines)
