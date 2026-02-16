from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd


def write_outputs(
    df: pd.DataFrame,
    outdir: str,
    sample_id: str,
    gene_summary: pd.DataFrame | None = None,
    disagreements: pd.DataFrame | None = None,
    run_meta: dict | None = None,
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

    report_html = _to_basic_html(summary)
    (p / f"{sample_id}.report.html").write_text(report_html, encoding="utf-8")

    pdf_written = _write_simple_pdf(summary, p / f"{sample_id}.report.pdf")

    output_files = [
        f"{sample_id}.amr_fused.csv",
        f"{sample_id}.amr_fused.json",
        f"{sample_id}.gene_summary.csv",
        f"{sample_id}.gene_summary.json",
        f"{sample_id}.disagreements.csv",
        f"{sample_id}.report.md",
        f"{sample_id}.report.html",
    ]
    if pdf_written:
        output_files.append(f"{sample_id}.report.pdf")

    manifest = {
        "sample_id": sample_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "output_files": output_files,
        "run_meta": run_meta or {},
        "pdf_export": "enabled" if pdf_written else "skipped_reportlab_missing",
    }
    (p / f"{sample_id}.run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


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
    consensus_tiers = (
        gene_summary["consensus_tier"].value_counts(dropna=False).to_dict()
        if gene_summary is not None and "consensus_tier" in gene_summary.columns
        else {}
    )

    lines = [
        f"# AMR Fusion Report - {sample_id}",
        "",
        f"- Total tool-level hits: **{total}**",
        f"- Unique genes: **{unique_genes}**",
        f"- Confidence counts: **{by_conf}**",
        f"- Single-tool disagreement candidates: **{disagreement_count}**",
        f"- Consensus tiers: **{consensus_tiers}**",
        f"- Top genes (first 10): {top_genes if top_genes else 'N/A'}",
        "",
        "## Notes",
        "- This is a baseline rule-based report.",
        "- Review `*.disagreements.csv` for single-tool detections.",
        "- Use fused CSV/JSON for auditability.",
    ]
    return "\n".join(lines)


def _to_basic_html(markdown_text: str) -> str:
    escaped = markdown_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    body = escaped.replace("\n", "<br>\n")
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>AMR Fusion Report</title>"
        "<style>body{font-family:Arial,sans-serif;max-width:1000px;margin:40px auto;line-height:1.5;}"
        "code{background:#f4f4f4;padding:2px 4px;border-radius:4px;}</style>"
        "</head><body>"
        f"{body}"
        "</body></html>"
    )


def _write_simple_pdf(text: str, path: Path) -> bool:
    """Write a simple text PDF report; return False if reportlab missing."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception:
        return False

    c = canvas.Canvas(str(path), pagesize=A4)
    _, height = A4
    y = height - 40
    line_height = 14

    for raw in text.splitlines():
        line = raw[:140]
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line)
        y -= line_height

    c.save()
    return True
