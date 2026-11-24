from datetime import datetime, timedelta, timezone
from typing import Optional, List
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.exceptions import UnauthorizedException, ForbiddenException
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise UnauthorizedException("Could not validate credentials")


def mask_licence_number(licence_no: Optional[str]) -> Optional[str]:
    if not licence_no:
        return None
    cleaned = licence_no.strip()
    if len(cleaned) <= 6:
        return "XX****" + cleaned[-2:]
    return cleaned[:2] + "****" + cleaned[-4:]


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.repositories.user_repo import UserRepository
    payload = decode_access_token(token)
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise UnauthorizedException("Invalid token payload")
    
    user = UserRepository.get_by_id(db, int(user_id))
    if user is None:
        raise UnauthorizedException("User not found")
    if not user.is_active:
        raise ForbiddenException("User account is inactive")
    return user


def require_roles(allowed_roles: List[str]):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise ForbiddenException(f"Access denied: requires one of {allowed_roles}")
        return current_user
    return role_checker


def require_role(allowed_role: str):
    return require_roles([allowed_role])
