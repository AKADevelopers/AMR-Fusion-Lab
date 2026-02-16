from __future__ import annotations

import pandas as pd
import typer
from rich import print

from .parsers import parse_resfinder, parse_amrfinder, parse_rgi
from .scoring import score_hits
from .fusion import build_gene_summary, build_disagreement_table
from .quality import normalize_and_filter_hits
from .ontology import harmonize_drug_classes
from .reporting import write_outputs
from .ai_summary import generate_ai_summary

app = typer.Typer(help="AMR Fusion Lab CLI")


@app.command()
def run(
    sample_id: str = typer.Option(..., help="Sample identifier"),
    outdir: str = typer.Option("outputs", help="Output directory"),
    resfinder: str | None = typer.Option(None, help="Path to ResFinder output (tsv/csv)"),
    amrfinder: str | None = typer.Option(None, help="Path to AMRFinder output (tsv/csv)"),
    rgi: str | None = typer.Option(None, help="Path to RGI output (tsv/csv)"),
    ai_enable: bool = typer.Option(False, help="Enable AI interpretation summary"),
    ai_provider: str = typer.Option(
        "openai_compatible",
        help="AI provider: openai_compatible | anthropic | ollama",
    ),
    ai_model: str = typer.Option("gpt-4o-mini", help="Model name (e.g., claude-3-5-sonnet-latest)"),
    ai_api_base: str | None = typer.Option(None, help="Provider API base URL override"),
    ai_api_key: str | None = typer.Option(None, help="Provider API key override"),
    min_identity: float = typer.Option(0.0, help="Minimum identity threshold (0-100)"),
    min_coverage: float = typer.Option(0.0, help="Minimum coverage threshold (0-100)"),
    deduplicate: bool = typer.Option(True, help="Drop duplicate tool-level hits"),
):
    """Fuse AMR hits from supported tools and generate report files."""
    frames: list[pd.DataFrame] = []

    if resfinder:
        frames.append(parse_resfinder(resfinder, sample_id))
    if amrfinder:
        frames.append(parse_amrfinder(amrfinder, sample_id))
    if rgi:
        frames.append(parse_rgi(rgi, sample_id))

    if not frames:
        raise typer.BadParameter("Provide at least one input: --resfinder, --amrfinder, or --rgi")

    if min_identity < 0 or min_identity > 100:
        raise typer.BadParameter("--min-identity must be between 0 and 100")
    if min_coverage < 0 or min_coverage > 100:
        raise typer.BadParameter("--min-coverage must be between 0 and 100")

    fused = pd.concat(frames, ignore_index=True)
    fused = normalize_and_filter_hits(
        fused,
        min_identity=min_identity,
        min_coverage=min_coverage,
        deduplicate=deduplicate,
    )
    fused = harmonize_drug_classes(fused)

    scored = score_hits(fused)
    gene_summary = build_gene_summary(scored)
    disagreements = build_disagreement_table(gene_summary)

    run_meta = {
        "quality_filters": {
            "min_identity": min_identity,
            "min_coverage": min_coverage,
            "deduplicate": deduplicate,
        },
        "ai": {
            "enabled": ai_enable,
            "provider": ai_provider,
            "model": ai_model,
        },
    }

    write_outputs(
        scored,
        outdir=outdir,
        sample_id=sample_id,
        gene_summary=gene_summary,
        disagreements=disagreements,
        run_meta=run_meta,
    )

    if ai_enable:
        ai = generate_ai_summary(
            sample_id=sample_id,
            scored_df=scored,
            gene_summary_df=gene_summary,
            disagreements_df=disagreements,
            outdir=outdir,
            model=ai_model,
            provider=ai_provider,
            api_base=ai_api_base,
            api_key=ai_api_key,
        )
        print("[cyan]AI summary generated[/cyan]")
        print(f"[dim]{ai.get('executive_summary', '')}[/dim]")

    print(f"[green]Done[/green] -> outputs written to [bold]{outdir}[/bold]")


if __name__ == "__main__":
    app()
