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


REQUIRED_KEYS = [
    "executive_summary",
    "high_priority_genes",
    "disagreement_notes",
    "recommended_review_actions",
    "limitations",
]


def generate_ai_summary(
    sample_id: str,
    scored_df: pd.DataFrame,
    gene_summary_df: pd.DataFrame,
    disagreements_df: pd.DataFrame,
    outdir: str,
    model: str,
    provider: str = "openai_compatible",
    api_base: str | None = None,
    api_key: str | None = None,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    """
    Generate AI narrative summary from fused AMR evidence.

    Supported providers:
      - openai_compatible (OpenAI/OpenRouter/Groq/Together/vLLM endpoints exposing /chat/completions)
      - anthropic
      - ollama (no API key required by default)
    """
    payload_data = _build_payload_data(sample_id, scored_df, gene_summary_df, disagreements_df)
    user_prompt = _build_user_prompt(payload_data)

    provider = provider.lower().strip()

    if provider == "openai_compatible":
        content = _call_openai_compatible(model, user_prompt, api_base, api_key, timeout_seconds)
    elif provider == "anthropic":
        content = _call_anthropic(model, user_prompt, api_base, api_key, timeout_seconds)
    elif provider == "ollama":
        content = _call_ollama(model, user_prompt, api_base, timeout_seconds)
    else:
        raise ValueError(
            "Unsupported provider. Use one of: openai_compatible, anthropic, ollama"
        )

    parsed = _parse_ai_json(content)
    _write_ai_outputs(sample_id, outdir, parsed)
    return parsed


def _build_payload_data(
    sample_id: str,
    scored_df: pd.DataFrame,
    gene_summary_df: pd.DataFrame,
    disagreements_df: pd.DataFrame,
) -> dict[str, Any]:
    return {
        "sample_id": sample_id,
        "totals": {
            "tool_level_hits": int(len(scored_df)),
            "unique_genes": int(len(gene_summary_df)),
            "disagreement_candidates": int(len(disagreements_df)),
        },
        "top_gene_summary": gene_summary_df.head(25).to_dict(orient="records"),
        "top_scored_hits": scored_df.head(40).to_dict(orient="records"),
    }


def _build_user_prompt(payload_data: dict[str, Any]) -> str:
    return (
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


def _call_openai_compatible(
    model: str,
    user_prompt: str,
    api_base: str | None,
    api_key: str | None,
    timeout_seconds: int,
) -> str:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("Missing API key. Set OPENAI_API_KEY or pass --ai-api-key.")

    base = (api_base or os.getenv("OPENAI_API_BASE") or "https://api.openai.com/v1").rstrip("/")

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
        f"{base}/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=timeout_seconds,
    )
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


def _call_anthropic(
    model: str,
    user_prompt: str,
    api_base: str | None,
    api_key: str | None,
    timeout_seconds: int,
) -> str:
    key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("Missing Anthropic API key. Set ANTHROPIC_API_KEY or pass --ai-api-key.")

    base = (api_base or os.getenv("ANTHROPIC_API_BASE") or "https://api.anthropic.com").rstrip("/")

    body = {
        "model": model,
        "max_tokens": 1000,
        "temperature": 0.1,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    r = requests.post(
        f"{base}/v1/messages",
        headers={
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=timeout_seconds,
    )
    r.raise_for_status()
    data = r.json()

    parts = data.get("content", [])
    text = "\n".join([p.get("text", "") for p in parts if p.get("type") == "text"]).strip()
    return text


def _call_ollama(
    model: str,
    user_prompt: str,
    api_base: str | None,
    timeout_seconds: int,
) -> str:
    base = (api_base or os.getenv("OLLAMA_API_BASE") or "http://localhost:11434").rstrip("/")

    prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
    body = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1},
    }

    r = requests.post(
        f"{base}/api/generate",
        headers={"Content-Type": "application/json"},
        json=body,
        timeout=timeout_seconds,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("response", "")


def _parse_ai_json(content: str) -> dict[str, Any]:
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI response was not valid JSON: {e}") from e

    missing = [k for k in REQUIRED_KEYS if k not in parsed]
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
