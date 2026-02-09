"""FastAPI application for the climbing session tracker."""

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .data.json_store import JSONSessionRepository
from .models.constants import (
    OUTCOMES, FELT_DIFFICULTIES, PHASE_TYPES,
    TERRAIN_TAGS, HOLD_TAGS, TECHNIQUE_TAGS, V_GRADES, OUTCOME_COLORS,
)

# Data file — same location as the CLI uses
DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(DATA_DIR, "sessions.json")

repo = JSONSessionRepository(DATA_FILE)

app = FastAPI(title="Climbing Tracker")

# Static files and templates
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Make constants available in all templates
TEMPLATE_GLOBALS = {
    "OUTCOMES": OUTCOMES,
    "FELT_DIFFICULTIES": FELT_DIFFICULTIES,
    "PHASE_TYPES": PHASE_TYPES,
    "TERRAIN_TAGS": TERRAIN_TAGS,
    "HOLD_TAGS": HOLD_TAGS,
    "TECHNIQUE_TAGS": TECHNIQUE_TAGS,
    "V_GRADES": V_GRADES,
    "OUTCOME_COLORS": OUTCOME_COLORS,
}


def render(request: Request, template: str, context: dict = None, partial: str = None):
    """Render a full page or HTMX partial based on request type."""
    ctx = {"request": request, **TEMPLATE_GLOBALS, **(context or {})}
    if request.headers.get("HX-Request") and partial:
        return templates.TemplateResponse(partial, ctx)
    return templates.TemplateResponse(template, ctx)


# Import and register routes
from .routes import sessions, climbs  # noqa: E402

app.include_router(sessions.router)
app.include_router(climbs.router)
