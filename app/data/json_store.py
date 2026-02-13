"""JSON file-based session repository."""

import json
import os
import uuid
from typing import Optional
from filelock import FileLock
from .repository import SessionRepository


class JSONSessionRepository(SessionRepository):
    def __init__(self, data_file: str):
        self.data_file = data_file
        self.lock = FileLock(data_file + ".lock")

    def _load(self) -> list[dict]:
        if not os.path.exists(self.data_file):
            return []
        with open(self.data_file, "r") as f:
            return json.load(f)

    def _save(self, sessions: list[dict]):
        with open(self.data_file, "w") as f:
            json.dump(sessions, f, indent=2)

    def _find(self, sessions: list[dict], session_id: str) -> Optional[dict]:
        for s in sessions:
            if s["id"] == session_id:
                return s
        return None

    def get_all(self) -> list[dict]:
        with self.lock:
            sessions = self._load()
        sessions.sort(key=lambda s: s.get("date", ""), reverse=True)
        return sessions

    def get_by_id(self, session_id: str) -> Optional[dict]:
        with self.lock:
            sessions = self._load()
        return self._find(sessions, session_id)

    def create(self, session: dict) -> dict:
        session["id"] = uuid.uuid4().hex[:8]
        session.setdefault("phases", [])
        session.setdefault("climbs", [])
        with self.lock:
            sessions = self._load()
            sessions.append(session)
            self._save(sessions)
        return session

    def update(self, session_id: str, data: dict) -> Optional[dict]:
        with self.lock:
            sessions = self._load()
            session = self._find(sessions, session_id)
            if not session:
                return None
            for key, val in data.items():
                if val is not None and key != "id":
                    session[key] = val
            self._save(sessions)
        return session

    def delete(self, session_id: str) -> bool:
        with self.lock:
            sessions = self._load()
            original_len = len(sessions)
            sessions = [s for s in sessions if s["id"] != session_id]
            if len(sessions) == original_len:
                return False
            self._save(sessions)
        return True

    def filter(self, gym: str = None, date_prefix: str = None,
               grade: str = None, limit: int = None) -> list[dict]:
        with self.lock:
            sessions = self._load()
        sessions.sort(key=lambda s: s.get("date", ""), reverse=True)

        if gym:
            gym_lower = gym.lower()
            sessions = [s for s in sessions if gym_lower in s.get("gym", "").lower()]

        if date_prefix:
            sessions = [s for s in sessions if s.get("date", "").startswith(date_prefix)]

        if grade:
            grade_upper = grade.upper()
            if not grade_upper.startswith("V"):
                grade_upper = "V" + grade_upper
            sessions = [
                s for s in sessions
                if any(grade_upper in c.get("grade_range", "").upper()
                       for c in s.get("climbs", []))
            ]

        if limit:
            sessions = sessions[:limit]

        return sessions

    def add_climb(self, session_id: str, climb: dict) -> Optional[dict]:
        with self.lock:
            sessions = self._load()
            session = self._find(sessions, session_id)
            if not session:
                return None
            session.setdefault("climbs", []).append(climb)
            self._save(sessions)
        return session

    def update_climb(self, session_id: str, climb_index: int, data: dict) -> Optional[dict]:
        with self.lock:
            sessions = self._load()
            session = self._find(sessions, session_id)
            if not session:
                return None
            climbs = session.get("climbs", [])
            if climb_index < 0 or climb_index >= len(climbs):
                return None
            climbs[climb_index] = data
            self._save(sessions)
        return session

    def delete_climb(self, session_id: str, climb_index: int) -> Optional[dict]:
        with self.lock:
            sessions = self._load()
            session = self._find(sessions, session_id)
            if not session:
                return None
            climbs = session.get("climbs", [])
            if climb_index < 0 or climb_index >= len(climbs):
                return None
            climbs.pop(climb_index)
            self._save(sessions)
        return session

    def add_phase(self, session_id: str, phase: dict) -> Optional[dict]:
        with self.lock:
            sessions = self._load()
            session = self._find(sessions, session_id)
            if not session:
                return None
            session.setdefault("phases", []).append(phase)
            self._save(sessions)
        return session

    def update_phase(self, session_id: str, phase_index: int, data: dict) -> Optional[dict]:
        with self.lock:
            sessions = self._load()
            session = self._find(sessions, session_id)
            if not session:
                return None
            phases = session.get("phases", [])
            if phase_index < 0 or phase_index >= len(phases):
                return None
            phases[phase_index] = data
            self._save(sessions)
        return session

    def delete_phase(self, session_id: str, phase_index: int) -> Optional[dict]:
        with self.lock:
            sessions = self._load()
            session = self._find(sessions, session_id)
            if not session:
                return None
            phases = session.get("phases", [])
            if phase_index < 0 or phase_index >= len(phases):
                return None
            phases.pop(phase_index)
            self._save(sessions)
        return session

    def get_all_gyms(self) -> list[str]:
        with self.lock:
            sessions = self._load()
        gyms = sorted(set(s.get("gym", "") for s in sessions if s.get("gym")))
        return gyms

    def reorder_climbs(self, session_id: str, order: list[int]) -> Optional[dict]:
        with self.lock:
            sessions = self._load()
            session = self._find(sessions, session_id)
            if not session:
                return None
            climbs = session.get("climbs", [])
            if sorted(order) != list(range(len(climbs))):
                return None
            session["climbs"] = [climbs[i] for i in order]
            self._save(sessions)
        return session

    def reorder_phases(self, session_id: str, order: list[int]) -> Optional[dict]:
        with self.lock:
            sessions = self._load()
            session = self._find(sessions, session_id)
            if not session:
                return None
            phases = session.get("phases", [])
            if sorted(order) != list(range(len(phases))):
                return None
            session["phases"] = [phases[i] for i in order]
            self._save(sessions)
        return session
