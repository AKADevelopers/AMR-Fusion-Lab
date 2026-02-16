from pydantic import BaseModel


class AMRHit(BaseModel):
    sample_id: str
    tool: str
    gene: str
    drug_class: str | None = None
    identity: float | None = None
    coverage: float | None = None


class ScoredAMRHit(AMRHit):
    confidence: str
    confidence_score: float
    rationale: str
