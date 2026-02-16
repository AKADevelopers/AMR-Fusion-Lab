from __future__ import annotations

import pandas as pd


def score_hits(df: pd.DataFrame) -> pd.DataFrame:
    """Rule-based confidence scoring (transparent baseline)."""
    out = df.copy()

    def _score(row):
        ident = row.get("identity")
        cov = row.get("coverage")
        score = 0.0
        reasons = []

        if ident is not None and pd.notna(ident):
            if ident >= 95:
                score += 0.5
                reasons.append("identity>=95")
            elif ident >= 90:
                score += 0.35
                reasons.append("identity>=90")
            else:
                reasons.append("identity<90")

        if cov is not None and pd.notna(cov):
            if cov >= 90:
                score += 0.5
                reasons.append("coverage>=90")
            elif cov >= 70:
                score += 0.3
                reasons.append("coverage>=70")
            else:
                reasons.append("coverage<70")

        if score >= 0.85:
            conf = "high"
        elif score >= 0.6:
            conf = "medium"
        else:
            conf = "low"

        return pd.Series({
            "confidence_score": round(float(score), 3),
            "confidence": conf,
            "rationale": "; ".join(reasons) if reasons else "insufficient metrics",
        })

    scored = out.apply(_score, axis=1)
    return pd.concat([out, scored], axis=1)
