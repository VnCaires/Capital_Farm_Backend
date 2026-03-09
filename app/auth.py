import os
import uuid
from datetime import datetime, timedelta
from typing import Annotated
from typing import Any

from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import database, models

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class OAuth2IdentifierRequestForm:
    def __init__(
        self,
        grant_type: Annotated[str | None, Form(pattern="^password$")] = None,
        identifier: Annotated[str | None, Form()] = None,
        username: Annotated[str | None, Form(include_in_schema=False)] = None,
        password: Annotated[str, Form()] = "",
        scope: Annotated[str, Form()] = "",
        client_id: Annotated[str | None, Form()] = None,
        client_secret: Annotated[str | None, Form()] = None,
    ) -> None:
        resolved_identifier = identifier or username or ""
        self.grant_type = grant_type
        self.username = resolved_identifier
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _utcnow() -> datetime:
    return datetime.utcnow()


def _timestamp_to_datetime(timestamp: int | float) -> datetime:
    return datetime.utcfromtimestamp(float(timestamp))


def _extract_claim_str(payload: dict[str, Any], claim: str) -> str:
    value = payload.get(claim)
    if not isinstance(value, str) or not value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return value


def create_access_token(data: dict[str, Any]) -> tuple[str, str, datetime]:
    to_encode = data.copy()
    expire = _utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "type": "access", "jti": jti})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, expire


def create_refresh_token(data: dict[str, Any]) -> tuple[str, str, datetime]:
    to_encode = data.copy()
    expire = _utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    jti = str(uuid.uuid4())
    to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token, jti, expire


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    try:
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = _extract_claim_str(payload, "type")
        _extract_claim_str(payload, "sub")
        _extract_claim_str(payload, "jti")

        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


def get_auth_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def store_refresh_session(db: Session, player_id: int, jti: str, expires_at: datetime) -> None:
    db.add(models.RefreshSession(player_id=player_id, jti=jti, expires_at=expires_at))
    db.commit()


def rotate_refresh_session(
    db: Session,
    player_id: int,
    old_jti: str,
    new_jti: str,
    new_expires_at: datetime,
) -> None:
    db_session = (
        db.query(models.RefreshSession)
        .filter(models.RefreshSession.player_id == player_id, models.RefreshSession.jti == old_jti)
        .first()
    )
    if db_session is None or db_session.revoked_at is not None or db_session.expires_at <= _utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db_session.revoked_at = _utcnow()
    db.add(models.RefreshSession(player_id=player_id, jti=new_jti, expires_at=new_expires_at))
    db.commit()


def revoke_refresh_session(db: Session, player_id: int, refresh_jti: str) -> None:
    db_session = (
        db.query(models.RefreshSession)
        .filter(models.RefreshSession.player_id == player_id, models.RefreshSession.jti == refresh_jti)
        .first()
    )
    if db_session is None:
        return
    db_session.revoked_at = _utcnow()
    db.commit()


def revoke_access_token(db: Session, access_jti: str, expires_at: datetime) -> None:
    already_revoked = (
        db.query(models.RevokedAccessToken)
        .filter(models.RevokedAccessToken.jti == access_jti)
        .first()
    )
    if already_revoked is not None:
        return
    db.add(models.RevokedAccessToken(jti=access_jti, expires_at=expires_at))
    db.commit()


def is_access_token_revoked(db: Session, access_jti: str) -> bool:
    return (
        db.query(models.RevokedAccessToken)
        .filter(models.RevokedAccessToken.jti == access_jti)
        .first()
        is not None
    )


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_auth_db),
) -> dict[str, Any]:
    payload = decode_token(token, expected_type="access")
    jti = _extract_claim_str(payload, "jti")
    if is_access_token_revoked(db, jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload


def get_current_username(payload: dict[str, Any] = Depends(get_current_token_payload)) -> str:
    return _extract_claim_str(payload, "sub")


def get_current_token_jti(payload: dict[str, Any] = Depends(get_current_token_payload)) -> str:
    return _extract_claim_str(payload, "jti")


def get_token_expiry(payload: dict[str, Any]) -> datetime:
    exp = payload.get("exp")
    if not isinstance(exp, (int, float)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return _timestamp_to_datetime(exp)
