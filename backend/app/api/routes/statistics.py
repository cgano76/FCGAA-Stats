from fastapi import APIRouter, Query

router = APIRouter()


@router.get("")
def search_statistics(
    cloture: int | None = Query(default=None),
    recolte: int | None = Query(default=None),
    profession: str | None = Query(default=None),
    espace: str | None = Query(default=None, pattern="^(CONVENTIONNEL|BIO)$"),
    zone: str | None = Query(default=None),
    quartile: str | None = Query(default=None),
    indicateur: str | None = Query(default=None),
) -> dict:
    return {
        "filters": {
            "cloture": cloture,
            "recolte": recolte,
            "profession": profession,
            "espace": espace,
            "zone": zone,
            "quartile": quartile,
            "indicateur": indicateur,
        },
        "values": [],
        "message": "Donnee non disponible tant qu'aucune valeur validee n'est en base.",
    }


@router.get("/comparison/2025-vs-2024")
def comparison_2025_vs_2024(
    profession: str | None = None,
    espace: str | None = Query(default=None, pattern="^(CONVENTIONNEL|BIO)$"),
) -> dict[str, str | list]:
    return {
        "profession": profession or "Donnée non disponible",
        "espace": espace or "Donnée non disponible",
        "items": [],
        "message": "Comparaison impossible sans valeurs 2024 et 2025 validees et sourcees.",
    }

