from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings

router = APIRouter()


@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)) -> dict[str, str | int]:
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Seuls les PDF sont acceptes.")

    # Le stockage et l'extraction seront branches dans le service d'import.
    return {
        "filename": file.filename or "document.pdf",
        "status": "brouillon",
        "message": "PDF recu. Extraction automatique a lancer puis validation humaine obligatoire.",
        "max_upload_mb": settings.max_upload_mb,
    }


@router.get("/rules")
def import_rules() -> dict[str, list[str]]:
    return {
        "bloquant": [
            "annee de cloture non detectee",
            "profession ou code nomenclature non detecte",
            "structure de tableau non reconnue",
            "indicateur obligatoire absent",
        ],
        "a_valider": [
            "seuil exact de confiance",
            "tolerance de cellules non reconnues",
            "liste finale des indicateurs obligatoires par tableau",
        ],
    }

