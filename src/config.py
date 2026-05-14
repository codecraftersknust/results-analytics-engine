import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


def _parse_csv_env(value: str, default: List[str]) -> List[str]:
    if not value:
        return default
    parsed = [item.strip() for item in value.split(",") if item.strip()]
    return parsed or default


@dataclass(frozen=True)
class Settings:
    environment: str
    cors_origins: List[str]
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    database_url: str
    upload_dir: str
    normalized_file: str
    max_upload_size_mb: int


settings = Settings(
    environment=os.getenv("APP_ENV", "development"),
    cors_origins=_parse_csv_env(
        os.getenv("CORS_ORIGINS", "http://localhost:3000"),
        ["http://localhost:3000"],
    ),
    jwt_secret=os.getenv("JWT_SECRET", ""),
    jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080")),
    database_url=os.getenv("DATABASE_URL", ""),
    upload_dir=os.getenv("UPLOAD_DIR", "data/uploads"),
    normalized_file=os.getenv("NORMALIZED_FILE", "normalized_results.csv"),
    max_upload_size_mb=int(os.getenv("MAX_UPLOAD_SIZE_MB", "10")),
)
