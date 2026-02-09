"""Pydantic models for request validation."""

from typing import Optional
from pydantic import BaseModel, Field


class PhaseCreate(BaseModel):
    type: str
    duration_minutes: int = Field(ge=1)
    notes: str = ""


class ClimbCreate(BaseModel):
    color: str
    grade_range: str
    perceived_grade: str = ""
    attempts: int = Field(default=1, ge=1)
    outcome: str
    felt_difficulty: str = ""
    terrain: list[str] = Field(default_factory=list)
    holds: list[str] = Field(default_factory=list)
    techniques: list[str] = Field(default_factory=list)
    phase: str = ""
    notes: str = ""


class SessionCreate(BaseModel):
    date: str
    time: str = ""
    gym: str
    duration_minutes: int = Field(ge=1)
    energy_level: int = Field(ge=1, le=5)
    body_notes: str = ""


class SessionUpdate(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    gym: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None, ge=1)
    energy_level: Optional[int] = Field(default=None, ge=1, le=5)
    body_notes: Optional[str] = None
