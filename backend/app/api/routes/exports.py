from fastapi import APIRouter

router = APIRouter()


@router.get("/formats")
def export_formats() -> dict[str, list[str]]:
    return {"formats": ["xlsx", "csv", "pdf", "png"]}


@router.post("")
def request_export() -> dict[str, str]:
    return {
        "status": "non_genere",
        "message": "Export bloque tant qu'aucune donnee validee et sourcee n'est selectionnee.",
    }

