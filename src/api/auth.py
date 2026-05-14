from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Generator, Optional, List

import bcrypt
import psycopg
from psycopg import errors as pg_errors
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from src.config import settings

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

if not SECRET_KEY and settings.environment != "development":
    raise RuntimeError("JWT_SECRET must be set outside development.")

if not settings.database_url:
    raise RuntimeError("DATABASE_URL must be set (Supabase session pooler URI).")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class UserInDB(BaseModel):
    id: int
    email: str
    password_hash: str
    name: str
    role: str
    subjects: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    subjects: List[str]


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(settings.database_url) as conn:
        yield conn


def init_db() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id BIGSERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    subjects TEXT NOT NULL DEFAULT ''
                )
                """
            )
        conn.commit()


def reset_users_table() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS users")
            cur.execute(
                """
                CREATE TABLE users (
                    id BIGSERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    subjects TEXT NOT NULL DEFAULT ''
                )
                """
            )
        conn.commit()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8"),
        )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_email(email: str) -> Optional[UserInDB]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, email, password_hash, name, role, subjects
                FROM users
                WHERE email = %s
                """,
                (email,),
            )
            row = cur.fetchone()

    if not row:
        return None

    return UserInDB(
        id=row[0],
        email=row[1],
        password_hash=row[2],
        name=row[3],
        role=row[4],
        subjects=row[5],
    )


def create_user(
    email: str,
    password: str,
    name: str,
    role: str,
    subjects: str = "",
) -> bool:
    hashed_pw = get_password_hash(password)
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, password_hash, name, role, subjects)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (email, hashed_pw, name, role, subjects),
                )
            conn.commit()
        return True
    except pg_errors.UniqueViolation:
        return False


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_email(email)
    if user is None:
        raise credentials_exception

    subjects_list = [s.strip() for s in user.subjects.split(",")] if user.subjects else []

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        subjects=subjects_list,
    )


init_db()
