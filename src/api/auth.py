import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# DB Config
DB_FILE = "data/users.db"
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# Auth Config
SECRET_KEY = "super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# --- Models ---
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

# --- DB Setup ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            subjects TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- Auth Utils ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- DB Operations ---
def get_user_by_email(email: str) -> Optional[UserInDB]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, email, password_hash, name, role, subjects FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    if row:
        return UserInDB(
            id=row[0], email=row[1], password_hash=row[2], 
            name=row[3], role=row[4], subjects=row[5]
        )
    return None

def create_user(email: str, password: str, name: str, role: str, subjects: str=""):
    hashed_pw = get_password_hash(password)
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password_hash, name, role, subjects) VALUES (?, ?, ?, ?, ?)",
                  (email, hashed_pw, name, role, subjects))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False # Email exists

# --- Dependency ---
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
        subjects=subjects_list
    )

# Initialize DB on load
init_db()
