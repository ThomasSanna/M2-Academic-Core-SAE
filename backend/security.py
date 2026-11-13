"""JWT (access + refresh), hash de mot de passe et dépendances d'autorisation."""
import os
import time
import uuid

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db import query_one

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TTL = int(os.getenv("ACCESS_TOKEN_MINUTES", "30")) * 60
REFRESH_TTL = int(os.getenv("REFRESH_TOKEN_DAYS", "7")) * 86400

bearer = HTTPBearer(auto_error=False)

# Jetons révoqués (logout / rotation du refresh) : {jti: expiration}.
# En mémoire => perdu au redémarrage et non partagé entre workers.
_revoked: dict[str, int] = {}


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except ValueError:
        return False


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _make_token(user_id: int, kind: str, ttl: int) -> tuple[str, str, int]:
    jti = uuid.uuid4().hex
    exp = int(time.time()) + ttl
    token = jwt.encode(
        {"sub": str(user_id), "type": kind, "jti": jti, "exp": exp},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return token, jti, exp


def create_token_pair(user_id: int) -> dict:
    access, _, _ = _make_token(user_id, "access", ACCESS_TTL)
    refresh, _, _ = _make_token(user_id, "refresh", REFRESH_TTL)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "expires_in": ACCESS_TTL,
    }


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalide ou expiré")
    if payload.get("type") != expected_type or is_revoked(payload["jti"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token invalide ou révoqué")
    return payload


def revoke(payload: dict) -> None:
    now = int(time.time())
    for jti in [j for j, exp in _revoked.items() if exp < now]:
        del _revoked[jti]
    _revoked[payload["jti"]] = payload["exp"]


def is_revoked(jti: str) -> bool:
    return jti in _revoked


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> dict:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentification requise")
    payload = decode_token(creds.credentials, "access")
    user = query_one(
        """
        SELECT u.id, u.last_name, u.first_name, u.email, u.is_active, u.created_at,
               COALESCE(array_agg(r.code ORDER BY r.code) FILTER (WHERE r.code IS NOT NULL), '{}') AS roles
        FROM users u
        LEFT JOIN user_roles ur ON ur.user_id = u.id
        LEFT JOIN roles r ON r.id = ur.role_id
        WHERE u.id = %s
        GROUP BY u.id
        """,
        (int(payload["sub"]),),
    )
    if not user or not user["is_active"]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Utilisateur inconnu ou désactivé")
    user["_jwt"] = payload
    return user


def require_roles(*codes: str):
    """Dépendance : exige au moins un des rôles donnés."""

    def checker(user: dict = Depends(get_current_user)) -> dict:
        if not set(codes) & set(user["roles"]):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Droits insuffisants")
        return user

    return checker


require_admin = require_roles("ADMIN")
require_staff = require_roles("ADMIN", "MANAGER")  # écriture sur la structure pédagogique
