"""Session routes."""

from datetime import datetime
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse

from ..main import repo, render, templates, TEMPLATE_GLOBALS

router = APIRouter()


@router.get("/")
async def session_list(request: Request, gym: str = "", date: str = "", grade: str = ""):
    filters = {"gym": gym, "date": date, "grade": grade}
    active_filters = any(filters.values())

    if active_filters:
        sessions = repo.filter(
            gym=gym or None,
            date_prefix=date or None,
            grade=grade or None,
        )
    else:
        sessions = repo.get_all()

    gyms = repo.get_all_gyms()
    return render(request, "index.html", {
        "sessions": sessions,
        "gyms": gyms,
        "filters": filters,
        "active_filters": active_filters,
    })


@router.get("/sessions/new")
async def new_session_form(request: Request):
    now = datetime.now()
    gyms = repo.get_all_gyms()
    return render(request, "sessions/new.html", {
        "today": now.strftime("%Y-%m-%d"),
        "now_time": now.strftime("%H:%M"),
        "gyms": gyms,
    })


@router.post("/sessions")
async def create_session(
    request: Request,
    date: str = Form(...),
    time: str = Form(""),
    gym: str = Form(...),
    duration_minutes: int = Form(...),
    energy_level: int = Form(3),
    body_notes: str = Form(""),
):
    session = repo.create({
        "date": date,
        "time": time,
        "gym": gym.strip(),
        "duration_minutes": duration_minutes,
        "energy_level": energy_level,
        "body_notes": body_notes.strip(),
    })
    return RedirectResponse(f"/sessions/{session['id']}", status_code=303)


@router.get("/sessions/{session_id}")
async def session_detail(request: Request, session_id: str):
    session = repo.get_by_id(session_id)
    if not session:
        return RedirectResponse("/", status_code=303)
    return render(request, "sessions/detail.html", {"session": session})


@router.get("/sessions/{session_id}/edit")
async def edit_session_form(request: Request, session_id: str):
    session = repo.get_by_id(session_id)
    if not session:
        return RedirectResponse("/", status_code=303)
    gyms = repo.get_all_gyms()
    return render(request, "sessions/edit.html", {"session": session, "gyms": gyms})


@router.post("/sessions/{session_id}/edit")
async def update_session(
    request: Request,
    session_id: str,
    date: str = Form(...),
    time: str = Form(""),
    gym: str = Form(...),
    duration_minutes: int = Form(...),
    energy_level: int = Form(3),
    body_notes: str = Form(""),
):
    repo.update(session_id, {
        "date": date,
        "time": time,
        "gym": gym.strip(),
        "duration_minutes": duration_minutes,
        "energy_level": energy_level,
        "body_notes": body_notes.strip(),
    })
    return RedirectResponse(f"/sessions/{session_id}", status_code=303)


@router.delete("/sessions/{session_id}")
async def delete_session(request: Request, session_id: str):
    repo.delete(session_id)
    return RedirectResponse("/", status_code=303)
