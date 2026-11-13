from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from db import query, query_one
from security import (
    create_token_pair, decode_token, get_current_user, revoke, verify_password,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginIn(BaseModel):
    email: str
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    refresh_token: str | None = None


def _audit(user_id: int | None, action: str) -> None:
    query(
        "INSERT INTO audit_logs (actor_user_id, action, entity, entity_id) VALUES (%s, %s, 'user', %s)",
        (user_id, action, user_id),
    )


@router.post("/login")
def login(body: LoginIn):
    user = query_one(
        "SELECT id, password_hash, is_active FROM users WHERE lower(email) = lower(%s)",
        (body.email,),
    )
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Identifiants incorrects")
    if not user["is_active"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Compte désactivé")
    _audit(user["id"], "LOGIN")
    return create_token_pair(user["id"])


@router.post("/refresh")
def refresh(body: RefreshIn):
    payload = decode_token(body.refresh_token, "refresh")
    user = query_one("SELECT id, is_active FROM users WHERE id = %s", (int(payload["sub"]),))
    if not user or not user["is_active"]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur inconnu ou désactivé")
    revoke(payload)  # rotation : l'ancien refresh ne sert qu'une fois
    return create_token_pair(user["id"])


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(body: LogoutIn | None = None, user: dict = Depends(get_current_user)):
    """Révoque l'access token courant et, si fourni, le refresh token."""
    revoke(user["_jwt"])
    if body and body.refresh_token:
        try:
            refresh_payload = decode_token(body.refresh_token, "refresh")
            if refresh_payload["sub"] == str(user["id"]):
                revoke(refresh_payload)
        except HTTPException:
            pass
    _audit(user["id"], "LOGOUT")
