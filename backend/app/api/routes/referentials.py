from fastapi import APIRouter

router = APIRouter()


@router.get("/sources")
def sources() -> dict[str, list[dict[str, str]]]:
    return {
        "documents": [
            {
                "name": "Statistiques FCGAA 2026 - Exercices 2025_compressed.pdf",
                "role": "recueil statistique cloture 2025",
            },
            {
                "name": "Statistiques FCGAA 2025 - Exercices 2024_compressed.pdf",
                "role": "recueil statistique cloture 2024",
            },
            {"name": "Dico Calculs.pdf", "role": "referentiel des formules"},
            {"name": "Dico Importation.pdf", "role": "referentiel des traces NBA/SBA"},
            {"name": "NOMENCLATURES.pdf", "role": "referentiel professions FCGAA"},
        ]
    }


@router.get("/filters")
def filters() -> dict[str, list[str]]:
    return {
        "clotures": [],
        "recoltes": [],
        "professions": [],
        "espaces": ["CONVENTIONNEL", "BIO"],
        "zones": ["Z1", "Z2", "Z3", "Toutes"],
        "quartiles": ["1/4 inferieur", "Median", "1/4 superieur"],
        "indicateurs": [],
    }

