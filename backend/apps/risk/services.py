from dataclasses import dataclass

from apps.clinical.models import ClinicalIntake
from apps.risk.models import RiskAssessment


@dataclass(frozen=True)
class ScoreResult:
    score: int
    tier: str
    explanation: dict[str, int]
    model_version: str = "rules-v0"


class RuleBasedRiskScorer:
    """Initial transparent scorer until enough validated data exists for ML."""

    weights = {
        "hiv_positive": 30,
        "household_tb_contact": 25,
        "has_who_tb_symptom": 25,
        "pregnant": 10,
        "postpartum": 15,
        "diabetes": 10,
        "sle_or_autoimmune": 15,
        "ckd": 10,
        "on_immunosuppressants": 20,
        "previous_tb": 15,
        "crowded_housing": 10,
        "poor_ventilation": 5,
    }

    def score(self, intake: ClinicalIntake) -> ScoreResult:
        explanation: dict[str, int] = {}
        total = 0

        for field, weight in self.weights.items():
            value = getattr(intake, field)
            if callable(value):
                value = value()
            if value:
                explanation[field] = weight
                total += weight

        return ScoreResult(
            score=min(total, 100),
            tier=self._tier(total),
            explanation=explanation,
        )

    def create_assessment(self, intake: ClinicalIntake) -> RiskAssessment:
        result = self.score(intake)
        return RiskAssessment.objects.create(
            patient=intake.encounter.patient,
            encounter=intake.encounter,
            score=result.score,
            tier=result.tier,
            explanation=result.explanation,
            model_version=result.model_version,
        )

    def _tier(self, score: int) -> str:
        if score >= 75:
            return RiskAssessment.RiskTier.CRITICAL
        if score >= 50:
            return RiskAssessment.RiskTier.HIGH
        if score >= 25:
            return RiskAssessment.RiskTier.MODERATE
        return RiskAssessment.RiskTier.LOW

