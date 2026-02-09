"""Climb and phase routes."""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from typing import Optional

from ..main import repo, templates, TEMPLATE_GLOBALS

router = APIRouter()


def _climb_list_html(request, session):
    """Render the climb list partial."""
    ctx = {"request": request, "session": session, **TEMPLATE_GLOBALS}
    return templates.TemplateResponse("climbs/list.html", ctx)


def _phase_section_html(request, session):
    """Render the phase section partial."""
    ctx = {"request": request, "session": session, **TEMPLATE_GLOBALS}
    return templates.TemplateResponse("partials/phase_list.html", ctx)


# ── Climb routes ─────────────────────────────────────────────────────────


@router.get("/sessions/{session_id}/climbs/new")
async def new_climb_form(request: Request, session_id: str):
    session = repo.get_by_id(session_id)
    if not session:
        return HTMLResponse("Session not found", status_code=404)
    phases = [p["type"] for p in session.get("phases", [])]
    ctx = {
        "request": request,
        "session_id": session_id,
        "phases": phases,
        **TEMPLATE_GLOBALS,
    }
    return templates.TemplateResponse("climbs/form.html", ctx)


@router.post("/sessions/{session_id}/climbs")
async def add_climb(
    request: Request,
    session_id: str,
    color: str = Form(...),
    grade_low: str = Form("V0"),
    grade_high: str = Form(""),
    perceived_grade: str = Form(""),
    attempts: int = Form(1),
    outcome: str = Form("sent"),
    felt_difficulty: str = Form(""),
    terrain: Optional[list[str]] = Form(None),
    holds: Optional[list[str]] = Form(None),
    techniques: Optional[list[str]] = Form(None),
    phase: str = Form(""),
    notes: str = Form(""),
    add_another: str = Form(""),
):
    grade_range = grade_low
    if grade_high and grade_high != grade_low:
        grade_range = f"{grade_low}-{grade_high}"

    climb = {
        "color": color.strip(),
        "grade_range": grade_range,
        "perceived_grade": perceived_grade,
        "attempts": attempts,
        "outcome": outcome,
        "felt_difficulty": felt_difficulty,
        "terrain": terrain or [],
        "holds": holds or [],
        "techniques": techniques or [],
        "phase": phase,
        "notes": notes.strip(),
    }

    session = repo.add_climb(session_id, climb)
    if not session:
        return HTMLResponse("Session not found", status_code=404)

    response = _climb_list_html(request, session)

    # If "Save & Add Another", re-open the form via HX-Trigger
    if add_another:
        response.headers["HX-Trigger"] = "climbAdded"

    return response


@router.get("/sessions/{session_id}/climbs/{climb_index}/edit")
async def edit_climb_form(request: Request, session_id: str, climb_index: int):
    session = repo.get_by_id(session_id)
    if not session:
        return HTMLResponse("Session not found", status_code=404)
    climbs = session.get("climbs", [])
    if climb_index < 0 or climb_index >= len(climbs):
        return HTMLResponse("Climb not found", status_code=404)

    phases = [p["type"] for p in session.get("phases", [])]
    ctx = {
        "request": request,
        "session_id": session_id,
        "climb": climbs[climb_index],
        "climb_index": climb_index,
        "phases": phases,
        **TEMPLATE_GLOBALS,
    }
    return templates.TemplateResponse("climbs/form.html", ctx)


@router.post("/sessions/{session_id}/climbs/{climb_index}/edit")
async def update_climb(
    request: Request,
    session_id: str,
    climb_index: int,
    color: str = Form(...),
    grade_low: str = Form("V0"),
    grade_high: str = Form(""),
    perceived_grade: str = Form(""),
    attempts: int = Form(1),
    outcome: str = Form("sent"),
    felt_difficulty: str = Form(""),
    terrain: Optional[list[str]] = Form(None),
    holds: Optional[list[str]] = Form(None),
    techniques: Optional[list[str]] = Form(None),
    phase: str = Form(""),
    notes: str = Form(""),
):
    grade_range = grade_low
    if grade_high and grade_high != grade_low:
        grade_range = f"{grade_low}-{grade_high}"

    climb_data = {
        "color": color.strip(),
        "grade_range": grade_range,
        "perceived_grade": perceived_grade,
        "attempts": attempts,
        "outcome": outcome,
        "felt_difficulty": felt_difficulty,
        "terrain": terrain or [],
        "holds": holds or [],
        "techniques": techniques or [],
        "phase": phase,
        "notes": notes.strip(),
    }

    session = repo.update_climb(session_id, climb_index, climb_data)
    if not session:
        return HTMLResponse("Not found", status_code=404)

    return _climb_list_html(request, session)


@router.delete("/sessions/{session_id}/climbs/{climb_index}")
async def delete_climb(request: Request, session_id: str, climb_index: int):
    session = repo.delete_climb(session_id, climb_index)
    if not session:
        return HTMLResponse("Not found", status_code=404)
    return _climb_list_html(request, session)


# ── Phase routes ─────────────────────────────────────────────────────────


@router.get("/sessions/{session_id}/phases/new")
async def new_phase_form(request: Request, session_id: str):
    ctx = {"request": request, "session_id": session_id, **TEMPLATE_GLOBALS}
    return templates.TemplateResponse("partials/phase_form.html", ctx)


@router.post("/sessions/{session_id}/phases")
async def add_phase(
    request: Request,
    session_id: str,
    type: str = Form(...),
    duration_minutes: int = Form(15),
    notes: str = Form(""),
):
    phase = {"type": type, "duration_minutes": duration_minutes, "notes": notes.strip()}
    session = repo.add_phase(session_id, phase)
    if not session:
        return HTMLResponse("Session not found", status_code=404)
    return _phase_section_html(request, session)


@router.get("/sessions/{session_id}/phases/{phase_index}/edit")
async def edit_phase_form(request: Request, session_id: str, phase_index: int):
    session = repo.get_by_id(session_id)
    if not session:
        return HTMLResponse("Session not found", status_code=404)
    phases = session.get("phases", [])
    if phase_index < 0 or phase_index >= len(phases):
        return HTMLResponse("Phase not found", status_code=404)

    ctx = {
        "request": request,
        "session_id": session_id,
        "phase": phases[phase_index],
        "phase_index": phase_index,
        **TEMPLATE_GLOBALS,
    }
    return templates.TemplateResponse("partials/phase_form.html", ctx)


@router.post("/sessions/{session_id}/phases/{phase_index}/edit")
async def update_phase(
    request: Request,
    session_id: str,
    phase_index: int,
    type: str = Form(...),
    duration_minutes: int = Form(15),
    notes: str = Form(""),
):
    phase_data = {"type": type, "duration_minutes": duration_minutes, "notes": notes.strip()}
    session = repo.update_phase(session_id, phase_index, phase_data)
    if not session:
        return HTMLResponse("Not found", status_code=404)
    return _phase_section_html(request, session)


@router.delete("/sessions/{session_id}/phases/{phase_index}")
async def delete_phase(request: Request, session_id: str, phase_index: int):
    session = repo.delete_phase(session_id, phase_index)
    if not session:
        return HTMLResponse("Not found", status_code=404)
    return _phase_section_html(request, session)
