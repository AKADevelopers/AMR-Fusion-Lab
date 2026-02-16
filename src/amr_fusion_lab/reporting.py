from __future__ import annotations

from pathlib import Path
import pandas as pd


def write_outputs(df: pd.DataFrame, outdir: str, sample_id: str) -> None:
    p = Path(outdir)
    p.mkdir(parents=True, exist_ok=True)

    df.to_csv(p / f"{sample_id}.amr_fused.csv", index=False)
    df.to_json(p / f"{sample_id}.amr_fused.json", orient="records", indent=2)

    summary = _markdown_summary(df, sample_id)
    (p / f"{sample_id}.report.md").write_text(summary, encoding="utf-8")


def _markdown_summary(df: pd.DataFrame, sample_id: str) -> str:
    total = len(df)
    by_conf = df["confidence"].value_counts(dropna=False).to_dict() if "confidence" in df.columns else {}
    top_genes = ", ".join(df["gene"].dropna().astype(str).head(10).tolist())

    lines = [
        f"# AMR Fusion Report - {sample_id}",
        "",
        f"- Total hits: **{total}**",
        f"- Confidence counts: **{by_conf}**",
        f"- Top genes (first 10): {top_genes if top_genes else 'N/A'}",
        "",
        "## Notes",
        "- This is a baseline rule-based report.",
        "- Use raw fused CSV/JSON for auditability.",
    ]
    return "\n".join(lines)
