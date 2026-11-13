"""API FastAPI — SAE (voir docs/infos.md pour les routes).

Doc interactive : http://localhost:8000/docs
"""
import psycopg.errors as pgerr
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from db import query
from routers import academic, auth, groups, users

app = FastAPI(title="SAE - API")

# Autorise n'importe quel front à appeler l'API (à restreindre si besoin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(academic.router)
app.include_router(groups.router)


# Contraintes PostgreSQL -> codes HTTP lisibles
@app.exception_handler(pgerr.UniqueViolation)
async def _unique(_: Request, exc: pgerr.UniqueViolation):
    return JSONResponse({"detail": "Cette valeur existe déjà (contrainte d'unicité)"}, status_code=409)


@app.exception_handler(pgerr.ForeignKeyViolation)
async def _fk(_: Request, exc: pgerr.ForeignKeyViolation):
    # RESTRICT à la suppression, ou référence inexistante à l'insertion
    msg = "Élément encore référencé ailleurs" if "still referenced" in str(exc) else "Référence inexistante"
    return JSONResponse({"detail": msg}, status_code=409 if "still referenced" in str(exc) else 422)


@app.exception_handler(pgerr.CheckViolation)
async def _check(_: Request, exc: pgerr.CheckViolation):
    return JSONResponse({"detail": "Valeurs invalides (contrainte de validation)"}, status_code=422)


@app.get("/health")
def health():
    query("SELECT 1")
    return {"status": "ok"}
