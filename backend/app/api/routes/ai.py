from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class AnalysisRequest(BaseModel):
    profession_code: str | None = None
    cloture: int | None = None
    espace: str | None = None
    analysis_type: str = "synthese_courte"


@router.post("/analyses")
def create_analysis(payload: AnalysisRequest) -> dict[str, str | bool | dict]:
    return {
        "status": "non_generee",
        "provider": "mistral",
        "model": settings.mistral_model,
        "external_research_enabled": settings.ai_external_research_enabled,
        "message": (
            "Analyse non generee : aucune donnee validee n'a ete fournie au moteur IA. "
            "L'IA ne doit pas inventer de chiffres."
        ),
        "request": payload.model_dump(),
    }

