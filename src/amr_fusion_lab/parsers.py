from __future__ import annotations

import pandas as pd


def parse_resfinder(path: str, sample_id: str) -> pd.DataFrame:
    """Parse a simplified ResFinder TSV/CSV export into canonical schema."""
    df = _read_any(path)
    mapping = {
        "Gene": "gene",
        "Resistance gene": "gene",
        "%Identity": "identity",
        "Identity": "identity",
        "%Coverage": "coverage",
        "Coverage": "coverage",
        "Phenotype": "drug_class",
    }
    out = _canonicalize(df, mapping)
    out["sample_id"] = sample_id
    out["tool"] = "resfinder"
    return out


def parse_amrfinder(path: str, sample_id: str) -> pd.DataFrame:
    """Parse a simplified AMRFinder TSV/CSV export into canonical schema."""
    df = _read_any(path)
    mapping = {
        "Gene symbol": "gene",
        "Gene": "gene",
        "% Identity to reference sequence": "identity",
        "% Coverage of reference sequence": "coverage",
        "Class": "drug_class",
        "Subclass": "drug_class",
    }
    out = _canonicalize(df, mapping)
    out["sample_id"] = sample_id
    out["tool"] = "amrfinder"
    return out


def parse_rgi(path: str, sample_id: str) -> pd.DataFrame:
    """Parse a simplified RGI TSV export into canonical schema."""
    df = _read_any(path)
    mapping = {
        "Best_Hit_ARO": "gene",
        "Best Hit ARO": "gene",
        "Drug Class": "drug_class",
        "% Identity": "identity",
        "% Length of Reference Sequence": "coverage",
    }
    out = _canonicalize(df, mapping)

    # RGI Best_Hit_ARO may look like 'ARO:3000001|blaTEM-1'
    out["gene"] = out["gene"].astype(str).str.split("|").str[-1]

    out["sample_id"] = sample_id
    out["tool"] = "rgi"
    return out


def _read_any(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    return pd.read_csv(path, sep=None, engine="python")


def _canonicalize(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    renamed = {}
    for col in df.columns:
        if col in mapping:
            renamed[col] = mapping[col]
    out = df.rename(columns=renamed).copy()

    for c in ["gene", "drug_class", "identity", "coverage"]:
        if c not in out.columns:
            out[c] = None

    # keep only canonical columns
    out = out[["gene", "drug_class", "identity", "coverage"]]
    return out
