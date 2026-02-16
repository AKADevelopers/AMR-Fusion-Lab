from __future__ import annotations

import pandas as pd
import typer
from rich import print

from .parsers import parse_resfinder, parse_amrfinder
from .scoring import score_hits
from .fusion import build_gene_summary, build_disagreement_table
from .reporting import write_outputs
from .ai_summary import generate_ai_summary

app = typer.Typer(help="AMR Fusion Lab CLI")


@app.command()
def run(
    sample_id: str = typer.Option(..., help="Sample identifier"),
    outdir: str = typer.Option("outputs", help="Output directory"),
    resfinder: str | None = typer.Option(None, help="Path to ResFinder output (tsv/csv)"),
    amrfinder: str | None = typer.Option(None, help="Path to AMRFinder output (tsv/csv)"),
    ai_enable: bool = typer.Option(False, help="Enable AI interpretation summary"),
    ai_model: str = typer.Option("gpt-4o-mini", help="OpenAI-compatible model for AI summary"),
    ai_api_base: str | None = typer.Option(None, help="OpenAI-compatible API base URL"),
    ai_api_key: str | None = typer.Option(None, help="API key (or set OPENAI_API_KEY)"),
):
    """Fuse AMR hits from supported tools and generate report files."""
    frames: list[pd.DataFrame] = []

    if resfinder:
        frames.append(parse_resfinder(resfinder, sample_id))
    if amrfinder:
        frames.append(parse_amrfinder(amrfinder, sample_id))

    if not frames:
        raise typer.BadParameter("Provide at least one input: --resfinder or --amrfinder")

    fused = pd.concat(frames, ignore_index=True)
    scored = score_hits(fused)
    gene_summary = build_gene_summary(scored)
    disagreements = build_disagreement_table(gene_summary)

    write_outputs(
        scored,
        outdir=outdir,
        sample_id=sample_id,
        gene_summary=gene_summary,
        disagreements=disagreements,
    )

    if ai_enable:
        ai = generate_ai_summary(
            sample_id=sample_id,
            scored_df=scored,
            gene_summary_df=gene_summary,
            disagreements_df=disagreements,
            outdir=outdir,
            model=ai_model,
            api_base=ai_api_base,
            api_key=ai_api_key,
        )
        print("[cyan]AI summary generated[/cyan]")
        print(f"[dim]{ai.get('executive_summary', '')}[/dim]")

    print(f"[green]Done[/green] -> outputs written to [bold]{outdir}[/bold]")


if __name__ == "__main__":
    app()
