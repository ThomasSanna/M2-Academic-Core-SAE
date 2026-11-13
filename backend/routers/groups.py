"""Groupes d'étudiants."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from db import query, query_one, transaction, update_row
from security import get_current_user, require_staff

router = APIRouter(tags=["Groupes"])


class GroupIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    group_type: str = Field(min_length=1, max_length=20, description="PROMO, TD, TP…")
    program_id: int
    academic_year_id: int
    parent_group_id: int | None = None


class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    group_type: str | None = Field(default=None, min_length=1, max_length=20)
    program_id: int | None = None
    academic_year_id: int | None = None
    parent_group_id: int | None = None  # null explicite => détache du parent


class StudentsIn(BaseModel):
    user_ids: list[int] = Field(min_length=1)


def _group_or_404(group_id: int, conn=None) -> dict:
    g = query_one("SELECT * FROM groups WHERE id = %s", (group_id,), conn)
    if not g:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Groupe introuvable")
    return g


def _check_refs(conn, data: dict, group_id: int | None = None) -> None:
    for key, table, label in (
        ("program_id", "programs", "Filière"),
        ("academic_year_id", "academic_years", "Année académique"),
        ("parent_group_id", "groups", "Groupe parent"),
    ):
        if data.get(key) is not None and not query_one(f"SELECT id FROM {table} WHERE id = %s", (data[key],), conn):
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"{label} introuvable")
    parent = data.get("parent_group_id")
    if parent is not None and group_id is not None:
        # interdit les cycles : le parent ne doit pas être le groupe lui-même ni un de ses descendants
        cycle = query_one(
            """
            WITH RECURSIVE descendants AS (
                SELECT id FROM groups WHERE id = %s
                UNION
                SELECT g.id FROM groups g JOIN descendants d ON g.parent_group_id = d.id
            )
            SELECT 1 FROM descendants WHERE id = %s
            """,
            (group_id, parent),
            conn,
        )
        if cycle:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "parent_group_id créerait un cycle")


@router.get("/groups")
def list_groups(
    program_id: int | None = None,
    academic_year_id: int | None = None,
    group_type: str | None = None,
    parent_group_id: int | None = None,
    _: dict = Depends(get_current_user),
):
    where, params = [], []
    for col, val in (
        ("program_id", program_id),
        ("academic_year_id", academic_year_id),
        ("group_type", group_type),
        ("parent_group_id", parent_group_id),
    ):
        if val is not None:
            where.append(f"g.{col} = %s")
            params.append(val)
    sql = """
        SELECT g.*, (SELECT count(*) FROM student_groups sg WHERE sg.group_id = g.id) AS student_count
        FROM groups g
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    return query(sql + " ORDER BY g.name", params)


@router.post("/groups", status_code=status.HTTP_201_CREATED)
def create_group(body: GroupIn, _: dict = Depends(require_staff)):
    with transaction() as conn:
        _check_refs(conn, body.model_dump())
        return query_one(
            """INSERT INTO groups (name, group_type, program_id, academic_year_id, parent_group_id)
               VALUES (%s, %s, %s, %s, %s) RETURNING *""",
            (body.name, body.group_type, body.program_id, body.academic_year_id, body.parent_group_id),
            conn,
        )


@router.get("/groups/{group_id}")
def get_group(group_id: int, _: dict = Depends(get_current_user)):
    g = _group_or_404(group_id)
    g["student_count"] = query_one(
        "SELECT count(*) AS n FROM student_groups WHERE group_id = %s", (group_id,)
    )["n"]
    return g


@router.put("/groups/{group_id}")
def update_group(group_id: int, body: GroupUpdate, _: dict = Depends(require_staff)):
    data = body.model_dump(exclude_unset=True)
    # les colonnes NOT NULL ne peuvent pas être mises à null
    for key in ("name", "group_type", "program_id", "academic_year_id"):
        if key in data and data[key] is None:
            del data[key]
    with transaction() as conn:
        _group_or_404(group_id, conn)
        _check_refs(conn, data, group_id)
        return update_row("groups", group_id, data, conn)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, _: dict = Depends(require_staff)):
    _group_or_404(group_id)
    query("DELETE FROM groups WHERE id = %s", (group_id,))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------
# Étudiants d'un groupe
# ---------------------------------------------------------------------
@router.get("/groups/{group_id}/students")
def list_students(group_id: int, _: dict = Depends(get_current_user)):
    _group_or_404(group_id)
    return query(
        """
        SELECT u.id, u.last_name, u.first_name, u.email, u.is_active
        FROM student_groups sg JOIN users u ON u.id = sg.user_id
        WHERE sg.group_id = %s ORDER BY u.last_name, u.first_name
        """,
        (group_id,),
    )


@router.post("/groups/{group_id}/students", status_code=status.HTTP_201_CREATED)
def add_students(group_id: int, body: StudentsIn, _: dict = Depends(require_staff)):
    ids = list(dict.fromkeys(body.user_ids))
    with transaction() as conn:
        _group_or_404(group_id, conn)
        students = query(
            """
            SELECT u.id FROM users u
            JOIN user_roles ur ON ur.user_id = u.id JOIN roles r ON r.id = ur.role_id
            WHERE u.id = ANY(%s) AND r.code = 'STUDENT'
            """,
            (ids,),
            conn,
        )
        invalid = set(ids) - {s["id"] for s in students}
        if invalid:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Utilisateurs inexistants ou sans rôle STUDENT : {sorted(invalid)}",
            )
        added = query(
            """
            INSERT INTO student_groups (user_id, group_id)
            SELECT unnest(%s::int[]), %s
            ON CONFLICT DO NOTHING RETURNING user_id
            """,
            (ids, group_id),
            conn,
        )
    return {"group_id": group_id, "added": [r["user_id"] for r in added]}


@router.delete("/groups/{group_id}/students", status_code=status.HTTP_204_NO_CONTENT)
def remove_students(
    group_id: int,
    user_id: list[int] = Query(..., description="Un ou plusieurs ids : ?user_id=1&user_id=2"),
    _: dict = Depends(require_staff),
):
    with transaction() as conn:
        _group_or_404(group_id, conn)
        query(
            "DELETE FROM student_groups WHERE group_id = %s AND user_id = ANY(%s)",
            (group_id, user_id),
            conn,
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
