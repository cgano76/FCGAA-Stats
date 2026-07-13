from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ai, exports, health, imports, referentials, statistics
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API FCGAA Stats - donnees statistiques agricoles validees et sourcees.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(imports.router, prefix="/imports", tags=["imports"])
app.include_router(referentials.router, prefix="/referentials", tags=["referentials"])
app.include_router(statistics.router, prefix="/statistics", tags=["statistics"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(exports.router, prefix="/exports", tags=["exports"])


@app.get("/")
def root() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "status": "pret",
        "regle": "Aucun chiffre ne doit etre affiche sans source validee.",
    }

