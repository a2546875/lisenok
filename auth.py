import base64
import hashlib
import hmac
import json
import time

from fastapi import Depends, Header, HTTPException

from config import settings

TOKEN_TTL = 60 * 60 * 24 * 14


def _secret() -> bytes:
    return (settings.secret_key or "lisenok-dev-secret").encode()


def is_admin_email(email: str) -> bool:
    admin = (settings.admin_email or "").strip().lower()
    return bool(admin) and email.strip().lower() == admin


def check_admin_password(password: str) -> bool:
    expected = settings.admin_password or ""
    return bool(expected) and hmac.compare_digest(password, expected)


def make_token(email: str, is_admin: bool) -> str:
    payload = {"email": email, "is_admin": is_admin, "exp": int(time.time()) + TOKEN_TTL}
    raw = json.dumps(payload, separators=(",", ":")).encode()
    sig = hmac.new(_secret(), raw, hashlib.sha256).hexdigest()
    return base64.urlsafe_b64encode(raw).decode() + "." + sig


def read_token(token: str) -> dict:
    try:
        raw_b64, sig = token.split(".", 1)
        raw = base64.urlsafe_b64decode(raw_b64.encode())
        expected = hmac.new(_secret(), raw, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            raise ValueError("bad sig")
        payload = json.loads(raw)
        if payload.get("exp", 0) < time.time():
            raise ValueError("expired")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Нужна авторизация") from exc


def optional_user(authorization: str | None = Header(default=None)) -> dict | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        return read_token(authorization.removeprefix("Bearer ").strip())
    except HTTPException:
        return None


def current_user(authorization: str | None = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Нужна авторизация")
    return read_token(authorization.removeprefix("Bearer ").strip())


def get_admin(user: dict = Depends(current_user)) -> dict:
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Нужны права администратора")
    return user
