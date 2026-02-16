# amr-fusion-lab

Unified AMR interpretation toolkit for microbiology/public-health workflows.

## Vision
`amr-fusion-lab` combines outputs from common AMR tools (e.g., ResFinder, AMRFinderPlus, RGI), harmonizes findings, and produces clear lab-ready reports with confidence tiers and disagreement flags.

## MVP (v0.1)
- Parse tool outputs (starting with ResFinder + AMRFinder TSV/CSV)
- Normalize schema to one canonical table
- Score confidence with transparent rules
- Generate:
  - JSON merged evidence
  - CSV summary
  - Markdown report
- Optional AI report summary (pluggable)

## Quick start
```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .
amr-fusion --help
```

## Example
```bash
amr-fusion run \
  --resfinder examples/resfinder_sample.tsv \
  --amrfinder examples/amrfinder_sample.tsv \
  --sample-id SAMPLE_001 \
  --outdir outputs/SAMPLE_001
```

## Why this is different
- Multi-tool fusion + disagreement analysis
- Public-health friendly output (not just raw hits)
- Reproducible and auditable confidence logic

## Roadmap
- [ ] Add RGI parser
- [ ] Add ontology mapping layer (drug class harmonization)
- [ ] Add HTML/PDF report
- [ ] Add AI narrative summarizer with strict JSON guardrails
- [ ] Add Docker image + CI pipeline
