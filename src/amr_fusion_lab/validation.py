from __future__ import annotations

import pandas as pd


def validate_canonical_hits(df: pd.DataFrame, strict: bool = False) -> list[str]:
    """Validate canonical AMR hit table and return warnings/errors."""
    messages: list[str] = []

    required_cols = ["sample_id", "tool", "gene"]
    for c in required_cols:
        if c not in df.columns:
            messages.append(f"ERROR: missing required column '{c}'")

    if "gene" in df.columns:
        missing_gene = int(df["gene"].isna().sum())
        if missing_gene > 0:
            messages.append(f"WARN: {missing_gene} rows have empty gene values")

    if "identity" in df.columns:
        bad_identity = int(df["identity"].dropna().map(lambda x: x < 0 or x > 100).sum())
        if bad_identity > 0:
            messages.append(f"WARN: {bad_identity} rows have identity outside 0-100")

    if "coverage" in df.columns:
        bad_cov = int(df["coverage"].dropna().map(lambda x: x < 0 or x > 100).sum())
        if bad_cov > 0:
            messages.append(f"WARN: {bad_cov} rows have coverage outside 0-100")

    if strict and any(m.startswith("WARN:") for m in messages):
        messages.append("ERROR: strict mode enabled; warnings treated as failures")

    return messages
