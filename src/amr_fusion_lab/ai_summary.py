from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import requests


SYSTEM_PROMPT = (
    "You are an AMR interpretation assistant for microbiology/public-health workflows. "
    "Be concise, evidence-aware, and cautious. Never invent genes or metrics. "
    "Return ONLY valid JSON matching the requested schema."
)


def generate_ai_summary(
    sample_id: str,
    scored_df: pd.DataFrame,
    gene_summary_df: pd.DataFrame,
    disagreements_df: pd.DataFrame,
    outdir: str,
    model: str,
    api_base: str | None = None,
    api_key: str | None = None,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    """Generate AI narrative summary from fused AMR evidence using OpenAI-compatible API."""
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing API key. Set OPENAI_API_KEY or pass --ai-api-key.")

    api_base = (api_base or os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1").rstrip("/")

    payload_data = {
        "sample_id": sample_id,
        "totals": {
            "tool_level_hits": int(len(scored_df)),
            "unique_genes": int(len(gene_summary_df)),
            "disagreement_candidates": int(len(disagreements_df)),
        },
        "top_gene_summary": gene_summary_df.head(25).to_dict(orient="records"),
        "top_scored_hits": scored_df.head(40).to_dict(orient="records"),
    }

    user_prompt = (
        "Analyze the following AMR fused evidence and produce a professional summary.\n"
        "Return STRICT JSON with exactly these keys:\n"
        "{\n"
        "  \"executive_summary\": string,\n"
        "  \"high_priority_genes\": [string],\n"
        "  \"disagreement_notes\": [string],\n"
        "  \"recommended_review_actions\": [string],\n"
        "  \"limitations\": [string]\n"
        "}\n\n"
        f"DATA:\n{json.dumps(payload_data, ensure_ascii=False)}"
    )

    body = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {"type": "json_object"},
    }

    r = requests.post(
        f"{api_base}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=timeout_seconds,
    )
    r.raise_for_status()
    data = r.json()

    content = data["choices"][0]["message"]["content"]
    parsed = _parse_ai_json(content)

    _write_ai_outputs(sample_id, outdir, parsed)
    return parsed


def _parse_ai_json(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI response was not valid JSON: {e}") from e

    required = [
        "executive_summary",
        "high_priority_genes",
        "disagreement_notes",
        "recommended_review_actions",
        "limitations",
    ]
    missing = [k for k in required if k not in parsed]
    if missing:
        raise ValueError(f"AI response missing keys: {missing}")

    return parsed


def _write_ai_outputs(sample_id: str, outdir: str, ai: dict[str, Any]) -> None:
    p = Path(outdir)
    p.mkdir(parents=True, exist_ok=True)

    (p / f"{sample_id}.ai_summary.json").write_text(
        json.dumps(ai, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md = [f"# AI Summary - {sample_id}", "", "## Executive summary", str(ai["executive_summary"]), ""]

    for section, key in [
        ("High priority genes", "high_priority_genes"),
        ("Disagreement notes", "disagreement_notes"),
        ("Recommended review actions", "recommended_review_actions"),
        ("Limitations", "limitations"),
    ]:
        md.append(f"## {section}")
        vals = ai.get(key, [])
        if vals:
            md.extend([f"- {v}" for v in vals])
        else:
            md.append("- None")
        md.append("")

    (p / f"{sample_id}.ai_summary.md").write_text("\n".join(md), encoding="utf-8")
