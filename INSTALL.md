# INSTALL.md — AMR-Fusion-Lab Quick Setup

This guide is the fastest way to install and run **AMR-Fusion-Lab**.

---

## 1) Requirements

- Python 3.10+
- Git
- (Optional) Docker Desktop
- (Optional) API key for AI features

---

## 2) Clone the repository

```bash
git clone https://github.com/AKADevelopers/AMR-Fusion-Lab.git
cd AMR-Fusion-Lab
```

---

## 3) Create virtual environment

### Windows (PowerShell/cmd)
```bash
python -m venv .venv
. .venv/Scripts/activate
```

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 4) Install package

```bash
pip install -e .
```

Check CLI:
```bash
amr-fusion --help
```

---

## 5) First run (recommended smoke test)

```bash
amr-fusion run \
  --resfinder examples/resfinder_sample.tsv \
  --amrfinder examples/amrfinder_sample.tsv \
  --rgi examples/rgi_sample.tsv \
  --sample-id SAMPLE_001 \
  --outdir outputs/SAMPLE_001
```

Expected output files include:
- `SAMPLE_001.amr_fused.csv`
- `SAMPLE_001.gene_summary.csv`
- `SAMPLE_001.report.md`
- `SAMPLE_001.report.html`
- `SAMPLE_001.run_manifest.json`

---

## 6) Team mode (config-driven, best practice)

Generate starter config:
```bash
amr-fusion init-config --output amr_fusion.yaml
```

Run from config:
```bash
amr-fusion run-config --config amr_fusion.yaml
```

---

## 7) Optional AI setup

### A) OpenAI-compatible
```bash
# Windows cmd
set OPENAI_API_KEY=YOUR_KEY

# optional
set OPENAI_API_BASE=https://openrouter.ai/api/v1
```

Run:
```bash
amr-fusion run \
  --resfinder examples/resfinder_sample.tsv \
  --amrfinder examples/amrfinder_sample.tsv \
  --sample-id SAMPLE_AI \
  --outdir outputs/SAMPLE_AI \
  --ai-enable \
  --ai-provider openai_compatible \
  --ai-model gpt-4o-mini
```

### B) Claude (Anthropic)
```bash
set ANTHROPIC_API_KEY=YOUR_KEY
```

Run:
```bash
amr-fusion run \
  --resfinder examples/resfinder_sample.tsv \
  --amrfinder examples/amrfinder_sample.tsv \
  --sample-id SAMPLE_CLAUDE \
  --outdir outputs/SAMPLE_CLAUDE \
  --ai-enable \
  --ai-provider anthropic \
  --ai-model claude-3-5-sonnet-latest
```

### C) Local open-source (Ollama)
Start Ollama model first, then:
```bash
amr-fusion run \
  --resfinder examples/resfinder_sample.tsv \
  --amrfinder examples/amrfinder_sample.tsv \
  --sample-id SAMPLE_OLLAMA \
  --outdir outputs/SAMPLE_OLLAMA \
  --ai-enable \
  --ai-provider ollama \
  --ai-model llama3.1
```

---

## 8) Optional quality controls

```bash
amr-fusion run \
  --resfinder examples/resfinder_sample.tsv \
  --sample-id SAMPLE_QC \
  --outdir outputs/SAMPLE_QC \
  --min-identity 90 \
  --min-coverage 70 \
  --deduplicate \
  --strict-validation
```

---

## 9) Optional Docker

Build:
```bash
docker build -t amr-fusion-lab:0.2 .
```

Run:
```bash
docker run --rm -v ${PWD}:/data -w /data amr-fusion-lab:0.2 run \
  --resfinder examples/resfinder_sample.tsv \
  --amrfinder examples/amrfinder_sample.tsv \
  --rgi examples/rgi_sample.tsv \
  --sample-id SAMPLE_DOCKER \
  --outdir outputs/SAMPLE_DOCKER
```

---

## 10) Troubleshooting

- **`amr-fusion: command not found`**
  - Virtual env not activated, or package not installed with `pip install -e .`

- **AI key errors**
  - Ensure correct env var is set (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`)

- **No PDF output**
  - Tool continues gracefully even if PDF backend is unavailable; check manifest for status

- **Docker not recognized**
  - Install Docker Desktop and restart terminal

---

If needed, open a GitHub issue with:
- OS
- Python version
- command used
- full error text
