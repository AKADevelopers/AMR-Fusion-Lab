from __future__ import annotations

import re
import pandas as pd

# Lightweight harmonization dictionary (extend over time)
_DRUG_CLASS_SYNONYMS = {
    "beta-lactam": ["beta-lactam", "beta lactam", "betalactam", "β-lactam"],
    "fluoroquinolone": ["fluoroquinolone", "quinolone", "fluoroquinolones"],
    "tetracycline": ["tetracycline", "tetracyclines"],
    "aminoglycoside": ["aminoglycoside", "aminoglycosides"],
    "macrolide": ["macrolide", "macrolides"],
    "sulfonamide": ["sulfonamide", "sulfonamides", "sulfa"],
    "glycopeptide": ["glycopeptide", "glycopeptides"],
    "polymyxin": ["polymyxin", "polymyxins", "colistin"],
    "rifamycin": ["rifamycin", "rifampicin", "rifampin"],
    "phenicol": ["phenicol", "chloramphenicol"],
}


def harmonize_drug_classes(df: pd.DataFrame) -> pd.DataFrame:
    """Add standardized drug class column for cross-tool comparability."""
    out = df.copy()
    if "drug_class" not in out.columns:
        out["drug_class"] = None

    out["drug_class_normalized"] = out["drug_class"].apply(_normalize_single)
    return out


def _normalize_single(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None

    # normalize separators
    text = re.sub(r"[_/]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    for canonical, variants in _DRUG_CLASS_SYNONYMS.items():
        if text == canonical:
            return canonical
        if any(v in text for v in variants):
            return canonical

    # fallback: keep cleaned string for traceability
    return text
