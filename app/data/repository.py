"""Abstract repository interface for session storage."""

from abc import ABC, abstractmethod
from typing import Optional


class SessionRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[dict]:
        """Return all sessions ordered by date descending."""

    @abstractmethod
    def get_by_id(self, session_id: str) -> Optional[dict]:
        """Return a single session by ID."""

    @abstractmethod
    def create(self, session: dict) -> dict:
        """Create a new session. Returns created session with ID."""

    @abstractmethod
    def update(self, session_id: str, data: dict) -> Optional[dict]:
        """Update session fields. Returns updated session."""

    @abstractmethod
    def delete(self, session_id: str) -> bool:
        """Delete a session. Returns True if deleted."""

    @abstractmethod
    def filter(self, gym: str = None, date_prefix: str = None,
               grade: str = None, limit: int = None) -> list[dict]:
        """Return sessions matching filters."""

    @abstractmethod
    def add_climb(self, session_id: str, climb: dict) -> Optional[dict]:
        """Add a climb to a session."""

    @abstractmethod
    def update_climb(self, session_id: str, climb_index: int, data: dict) -> Optional[dict]:
        """Update a climb within a session."""

    @abstractmethod
    def delete_climb(self, session_id: str, climb_index: int) -> Optional[dict]:
        """Delete a climb from a session."""

    @abstractmethod
    def add_phase(self, session_id: str, phase: dict) -> Optional[dict]:
        """Add a phase to a session."""

    @abstractmethod
    def update_phase(self, session_id: str, phase_index: int, data: dict) -> Optional[dict]:
        """Update a phase within a session."""

    @abstractmethod
    def delete_phase(self, session_id: str, phase_index: int) -> Optional[dict]:
        """Delete a phase from a session."""

    @abstractmethod
    def get_all_gyms(self) -> list[str]:
        """Return distinct gym names from all sessions."""
