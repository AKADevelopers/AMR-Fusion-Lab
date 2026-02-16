# AMR-Fusion-Lab v0.2.0

**Release date:** 2026-02-16

## Highlights
- Multi-tool AMR fusion: ResFinder + AMRFinder + RGI
- Drug-class ontology harmonization for cross-tool consistency
- Weighted consensus scoring tiers with tool reliability priors
- AI interpretation layer with provider support:
  - OpenAI-compatible endpoints
  - Anthropic Claude (including Sonnet 3.5 family)
  - Ollama local open-source models
- Professional outputs:
  - fused evidence (CSV/JSON)
  - gene summary (CSV/JSON)
  - disagreement table (CSV)
  - report (Markdown + HTML)
  - run manifest (JSON)
- Docker packaging and CI improvements

## Verification and quality
- Unit test suite passing
- CI matrix on Python 3.10, 3.11, 3.12
- CLI smoke test in CI
- Docker build check in CI

## Upgrade notes
- New CLI options for quality gates:
  - `--min-identity`
  - `--min-coverage`
  - `--deduplicate`
- New AI configuration options:
  - `--ai-provider`
  - `--ai-model`
  - `--ai-api-base`
  - `--ai-api-key`
