from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, EmailStr, Field

from db import query, query_one, transaction
from security import get_current_user, hash_password, require_admin

router = APIRouter(tags=["Users"])

USER_SELECT = """
    SELECT u.id, u.last_name, u.first_name, u.email, u.is_active, u.created_at,
           COALESCE(array_agg(r.code ORDER BY r.code) FILTER (WHERE r.code IS NOT NULL), '{}') AS roles
    FROM users u
    LEFT JOIN user_roles ur ON ur.user_id = u.id
    LEFT JOIN roles r ON r.id = ur.role_id
"""


class UserOut(BaseModel):
    id: int
    last_name: str
    first_name: str
    email: str
    is_active: bool
    created_at: datetime
    roles: list[str]


class UserCreate(BaseModel):
    last_name: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)
    is_active: bool = True
    roles: list[str] = []  # codes de rôles (ADMIN, MANAGER, TEACHER, STUDENT)


class UserUpdate(BaseModel):
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None


class RolesIn(BaseModel):
    roles: list[str]  # remplace l'ensemble des rôles de l'utilisateur


def _get_user(user_id: int, conn=None) -> dict:
    user = query_one(USER_SELECT + " WHERE u.id = %s GROUP BY u.id", (user_id,), conn)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur introuvable")
    return user


def _set_roles(conn, user_id: int, codes: list[str]) -> None:
    codes = list(dict.fromkeys(codes))
    found = query("SELECT id, code FROM roles WHERE code = ANY(%s)", (codes,), conn)
    unknown = set(codes) - {r["code"] for r in found}
    if unknown:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Rôles inconnus : {sorted(unknown)}")
    query("DELETE FROM user_roles WHERE user_id = %s", (user_id,), conn)
    for r in found:
        query("INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)", (user_id, r["id"]), conn)


@router.get("/users/me", response_model=UserOut)
def me(user: dict = Depends(get_current_user)):
    return user


@router.get("/roles")
def list_roles(_: dict = Depends(get_current_user)):
    return query("SELECT id, code, label FROM roles ORDER BY id")


@router.get("/users", response_model=list[UserOut])
def list_users(
    role: str | None = None,
    is_active: bool | None = None,
    q: str | None = Query(None, description="Recherche sur nom, prénom, email"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    _: dict = Depends(require_admin),
):
    where, params = [], []
    if is_active is not None:
        where.append("u.is_active = %s")
        params.append(is_active)
    if q:
        where.append("(u.last_name ILIKE %s OR u.first_name ILIKE %s OR u.email ILIKE %s)")
        params += [f"%{q}%"] * 3
    if role:
        where.append(
            "EXISTS (SELECT 1 FROM user_roles x JOIN roles xr ON xr.id = x.role_id "
            "WHERE x.user_id = u.id AND xr.code = %s)"
        )
        params.append(role)
    sql = USER_SELECT + (" WHERE " + " AND ".join(where) if where else "")
    sql += " GROUP BY u.id ORDER BY u.last_name, u.first_name LIMIT %s OFFSET %s"
    return query(sql, (*params, limit, offset))


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(body: UserCreate, _: dict = Depends(require_admin)):
    with transaction() as conn:
        row = query_one(
            """INSERT INTO users (last_name, first_name, email, password_hash, is_active)
               VALUES (%s, %s, %s, %s, %s) RETURNING id""",
            (body.last_name, body.first_name, body.email, hash_password(body.password), body.is_active),
            conn,
        )
        _set_roles(conn, row["id"], body.roles)
        return _get_user(row["id"], conn)


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, body: UserUpdate, admin: dict = Depends(require_admin)):
    data = body.model_dump(exclude_unset=True, exclude_none=True)
    if "password" in data:
        data["password_hash"] = hash_password(data.pop("password"))
    if data.get("is_active") is False and user_id == admin["id"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Vous ne pouvez pas désactiver votre propre compte")
    with transaction() as conn:
        _get_user(user_id, conn)
        if data:
            sets = ", ".join(f"{c} = %s" for c in data)
            query(f"UPDATE users SET {sets} WHERE id = %s", (*data.values(), user_id), conn)
        return _get_user(user_id, conn)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, admin: dict = Depends(require_admin)):
    if user_id == admin["id"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Vous ne pouvez pas supprimer votre propre compte")
    if not query("DELETE FROM users WHERE id = %s RETURNING id", (user_id,)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur introuvable")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/users/{user_id}/roles", response_model=UserOut)
def set_user_roles(user_id: int, body: RolesIn, admin: dict = Depends(require_admin)):
    if user_id == admin["id"] and "ADMIN" not in body.roles:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Vous ne pouvez pas retirer votre propre rôle ADMIN")
    with transaction() as conn:
        _get_user(user_id, conn)
        _set_roles(conn, user_id, body.roles)
        return _get_user(user_id, conn)
