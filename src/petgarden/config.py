from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PETGARDEN_")

    data_dir: Path = BASE_DIR / "data"
    version: str = "0.1.0"
    build_time: str = "2026-10-25"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "petgarden.db"

    @property

    def backups_dir(self) -> Path:
        return self.data_dir / "backups"

    @property
    def frontend_dist(self) -> Path:
        return BASE_DIR / "frontend" / "dist"


def get_settings() -> Settings:
    return Settings()