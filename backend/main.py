"""API FastAPI — point de départ à compléter (voir docs/infos.md pour les routes).

Doc interactive : http://localhost:8000/docs
"""
import os

import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sae:sae@localhost:5432/sae")

app = FastAPI(title="SAE - API")

# Autorise n'importe quel front à appeler l'API (à restreindre si besoin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def query(sql: str, params: tuple = ()) -> list[dict]:
    """Exécute une requête SQL et renvoie les lignes sous forme de dicts."""
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        cur = conn.execute(sql, params)
        return cur.fetchall() if cur.description else []


@app.get("/health")
def health():
    query("SELECT 1")
    return {"status": "ok"}


# Exemple de route : à dupliquer pour les autres ressources
@app.get("/roles")
def list_roles():
    return query("SELECT id, code, label FROM roles ORDER BY id")
