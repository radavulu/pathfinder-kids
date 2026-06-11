"""Request/response models for the JSON API."""
from __future__ import annotations

from pydantic import BaseModel


class AnswerIn(BaseModel):
    problem_id: int
    answer: str = ""
    attempt: int = 1


class LevelAdjustIn(BaseModel):
    subject: str
    delta: int = 0


class SettingsIn(BaseModel):
    name: str | None = None
    palette: str | None = None
    time_targets: dict[str, int] | None = None
    levels: dict[str, int] | None = None


class LMStudioIn(BaseModel):
    url: str | None = None
    model: str | None = None


class MascotIn(BaseModel):
    name: str
