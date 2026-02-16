from __future__ import annotations

import pandas as pd


def normalize_and_filter_hits(
    df: pd.DataFrame,
    min_identity: float = 0.0,
    min_coverage: float = 0.0,
    deduplicate: bool = True,
) -> pd.DataFrame:
    """Normalize numeric fields and apply transparent quality filters."""
    out = df.copy()

    for col in ["identity", "coverage"]:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    # keep rows that pass provided thresholds when values exist
    if "identity" in out.columns and min_identity > 0:
        out = out[(out["identity"].isna()) | (out["identity"] >= min_identity)]

    if "coverage" in out.columns and min_coverage > 0:
        out = out[(out["coverage"].isna()) | (out["coverage"] >= min_coverage)]

    if deduplicate:
        dedupe_cols = [c for c in ["sample_id", "tool", "gene", "drug_class", "identity", "coverage"] if c in out.columns]
        out = out.drop_duplicates(subset=dedupe_cols)

    out = out.reset_index(drop=True)
    return out
