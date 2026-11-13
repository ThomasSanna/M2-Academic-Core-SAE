"""Accès PostgreSQL (psycopg 3, SQL brut)."""
import os
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sae:sae@localhost:5432/sae")


@contextmanager
def transaction():
    """Connexion avec commit à la sortie (rollback si exception)."""
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        yield conn


def query(sql: str, params: tuple | list = (), conn=None) -> list[dict]:
    """Exécute une requête SQL et renvoie les lignes sous forme de dicts."""
    if conn is not None:
        cur = conn.execute(sql, params)
        return cur.fetchall() if cur.description else []
    with transaction() as c:
        cur = c.execute(sql, params)
        return cur.fetchall() if cur.description else []


def query_one(sql: str, params: tuple | list = (), conn=None) -> dict | None:
    rows = query(sql, params, conn)
    return rows[0] if rows else None


def update_row(table: str, row_id: int, data: dict, conn=None) -> dict | None:
    """UPDATE partiel. Les noms de colonnes viennent des schémas Pydantic (jamais du client)."""
    if not data:
        return query_one(f"SELECT * FROM {table} WHERE id = %s", (row_id,), conn)
    sets = ", ".join(f"{col} = %s" for col in data)
    return query_one(
        f"UPDATE {table} SET {sets} WHERE id = %s RETURNING *",
        (*data.values(), row_id),
        conn,
    )
