#!/usr/bin/env python3
"""Rock climbing session tracker for indoor bouldering."""

import json
import os
import sys
import uuid
from datetime import datetime, date

# ── Constants ────────────────────────────────────────────────────────────────

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions.json")

OUTCOMES = ["sent", "flashed", "failed", "working"]
FELT_DIFFICULTIES = ["sandbagged", "on-grade", "soft"]
PHASE_TYPES = ["warmup", "working", "projecting", "cooldown"]
TERRAIN_TAGS = ["overhang", "slab", "vertical", "roof"]
HOLD_TAGS = ["crimps", "jugs", "slopers", "pinches", "pockets"]
TECHNIQUE_TAGS = ["dyno", "heel hook", "knee bar", "compression"]

# ── Storage ──────────────────────────────────────────────────────────────────


def load_sessions():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_sessions(sessions):
    with open(DATA_FILE, "w") as f:
        json.dump(sessions, f, indent=2)


# ── Input helpers ────────────────────────────────────────────────────────────


def ask(prompt, default=None, required=True):
    """Prompt for text input."""
    suffix = f" [{default}]" if default else ""
    while True:
        val = input(f"{prompt}{suffix}: ").strip()
        if not val and default is not None:
            return default
        if val or not required:
            return val
        print("  Required field, please enter a value.")


def ask_int(prompt, default=None, min_val=None, max_val=None):
    """Prompt for an integer."""
    suffix = f" [{default}]" if default is not None else ""
    while True:
        val = input(f"{prompt}{suffix}: ").strip()
        if not val and default is not None:
            return default
        try:
            n = int(val)
            if min_val is not None and n < min_val:
                print(f"  Must be at least {min_val}.")
                continue
            if max_val is not None and n > max_val:
                print(f"  Must be at most {max_val}.")
                continue
            return n
        except ValueError:
            print("  Enter a number.")


def ask_choice(prompt, choices, default=None, allow_empty=False):
    """Prompt to pick from a list."""
    numbered = [f"  {i+1}. {c}" for i, c in enumerate(choices)]
    print(f"{prompt}")
    print("\n".join(numbered))
    suffix = f" [{default}]" if default else ""
    if allow_empty:
        suffix += " (Enter to skip)"
    while True:
        val = input(f"Choice{suffix}: ").strip()
        if not val and default:
            return default
        if not val and allow_empty:
            return None
        try:
            idx = int(val) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            # Allow typing the name directly
            lower = val.lower()
            for c in choices:
                if c.lower() == lower:
                    return c
        print(f"  Pick 1-{len(choices)} or type the name.")


def ask_tags(prompt, options):
    """Prompt for multiple tags from a list. Returns a list."""
    numbered = [f"  {i+1}. {t}" for i, t in enumerate(options)]
    print(f"{prompt} (comma-separated numbers or names, Enter to skip)")
    print("\n".join(numbered))
    val = input("Tags: ").strip()
    if not val:
        return []
    tags = []
    for part in val.split(","):
        part = part.strip()
        try:
            idx = int(part) - 1
            if 0 <= idx < len(options):
                tags.append(options[idx])
        except ValueError:
            lower = part.lower()
            for opt in options:
                if opt.lower() == lower:
                    tags.append(opt)
                    break
    return tags


def ask_choice_with_default(prompt, choices, current, allow_empty=False):
    """Prompt to pick from a list, highlighting the current value."""
    numbered = []
    for i, c in enumerate(choices):
        marker = " <--" if c == current else ""
        numbered.append(f"  {i+1}. {c}{marker}")
    print(f"{prompt}")
    print("\n".join(numbered))
    suffix = f" [{current}]" if current else ""
    if allow_empty:
        suffix += " (Enter to keep)"
    while True:
        val = input(f"Choice{suffix}: ").strip()
        if not val:
            return current
        try:
            idx = int(val) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            lower = val.lower()
            for c in choices:
                if c.lower() == lower:
                    return c
        print(f"  Pick 1-{len(choices)} or type the name.")


def ask_tags_with_default(prompt, options, current):
    """Prompt for multiple tags, showing current selection."""
    numbered = []
    for i, t in enumerate(options):
        marker = " *" if t in current else ""
        numbered.append(f"  {i+1}. {t}{marker}")
    current_str = ", ".join(current) if current else "none"
    print(f"{prompt} (current: {current_str})")
    print("\n".join(numbered))
    print("  Comma-separated numbers/names, Enter to keep, 'clear' to remove all")
    val = input("Tags: ").strip()
    if not val:
        return current
    if val.lower() == "clear":
        return []
    tags = []
    for part in val.split(","):
        part = part.strip()
        try:
            idx = int(part) - 1
            if 0 <= idx < len(options):
                tags.append(options[idx])
        except ValueError:
            lower = part.lower()
            for opt in options:
                if opt.lower() == lower:
                    tags.append(opt)
                    break
    return tags


def confirm(prompt, default=True):
    """Yes/no prompt."""
    hint = "Y/n" if default else "y/N"
    val = input(f"{prompt} [{hint}]: ").strip().lower()
    if not val:
        return default
    return val in ("y", "yes")


# ── Session creation ─────────────────────────────────────────────────────────


def create_session():
    """Interactively create a new climbing session."""
    print("\n═══ New Climbing Session ═══\n")

    now = datetime.now()
    date_str = ask("Date", default=now.strftime("%Y-%m-%d"))
    time_str = ask("Start time", default=now.strftime("%H:%M"))
    gym = ask("Gym name")
    duration = ask_int("Total duration (minutes)", min_val=1)
    energy = ask_int("Energy level (1-5)", min_val=1, max_val=5)
    body_notes = ask("Body notes (injuries/soreness)", required=False)

    session = {
        "id": uuid.uuid4().hex[:8],
        "date": date_str,
        "time": time_str,
        "gym": gym,
        "duration_minutes": duration,
        "energy_level": energy,
        "body_notes": body_notes or "",
        "phases": [],
        "climbs": [],
    }

    # Phases
    if confirm("Add session phases?", default=False):
        add_phases(session)

    # Climbs
    if confirm("Add climbs now?", default=True):
        add_climbs_loop(session)

    sessions = load_sessions()
    sessions.append(session)
    save_sessions(sessions)
    print(f"\nSession saved! ({len(session['climbs'])} climbs logged)")
    return session


# ── Phases ───────────────────────────────────────────────────────────────────


def add_phases(session):
    """Add phases to a session."""
    while True:
        print(f"\n── Add Phase ({len(session['phases'])+1}) ──")
        phase_type = ask_choice("Phase type:", PHASE_TYPES)
        duration = ask_int("Duration (minutes)", min_val=1)
        notes = ask("Notes", required=False)
        session["phases"].append({
            "type": phase_type,
            "duration_minutes": duration,
            "notes": notes or "",
        })
        print(f"  Added {phase_type} phase.")
        if not confirm("Add another phase?", default=False):
            break


# ── Climbs ───────────────────────────────────────────────────────────────────


def add_climbs_loop(session):
    """Interactively add climbs to a session."""
    phase_names = [p["type"] for p in session["phases"]] if session["phases"] else []

    while True:
        print(f"\n── Add Climb ({len(session['climbs'])+1}) ──")
        climb = build_climb(phase_names)
        session["climbs"].append(climb)
        grade_display = climb["grade_range"]
        if climb.get("perceived_grade"):
            grade_display += f" (felt {climb['perceived_grade']})"
        print(f"  Logged: {climb['color']} {grade_display} — {climb['outcome']}")
        if not confirm("Add another climb?", default=True):
            break


def build_climb(phase_names):
    """Build a single climb dict from user input."""
    color = ask("Hold color")
    grade_range = ask("Grade range (e.g. V3-V4)")
    perceived = ask("Perceived grade (optional, e.g. V4)", required=False)
    attempts = ask_int("Attempts", default=1, min_val=1)
    outcome = ask_choice("Outcome:", OUTCOMES)
    felt = ask_choice("Felt difficulty:", FELT_DIFFICULTIES, allow_empty=True)
    terrain = ask_tags("Terrain:", TERRAIN_TAGS)
    holds = ask_tags("Holds:", HOLD_TAGS)
    techniques = ask_tags("Techniques:", TECHNIQUE_TAGS)

    phase = None
    if phase_names:
        phase = ask_choice("Phase:", phase_names, allow_empty=True)

    notes = ask("Notes", required=False)

    return {
        "color": color,
        "grade_range": grade_range,
        "perceived_grade": perceived or "",
        "attempts": attempts,
        "outcome": outcome,
        "felt_difficulty": felt or "",
        "terrain": terrain,
        "holds": holds,
        "techniques": techniques,
        "phase": phase or "",
        "notes": notes or "",
    }


# ── Add climbs to existing session ──────────────────────────────────────────


def add_to_session():
    """Add climbs to the most recent session (or pick one)."""
    sessions = load_sessions()
    if not sessions:
        print("No sessions found. Create one first with 'new'.")
        return

    session = sessions[-1]
    print(f"\nAdding climbs to session: {session['date']} at {session['gym']}")
    if not confirm("Is this the right session?"):
        session = pick_session(sessions)
        if not session:
            return

    phase_names = [p["type"] for p in session["phases"]] if session["phases"] else []
    add_climbs_inner(session, phase_names)
    save_sessions(sessions)
    print(f"\nSession updated! ({len(session['climbs'])} total climbs)")


def add_climbs_inner(session, phase_names):
    """Add climbs in a loop."""
    while True:
        print(f"\n── Add Climb ({len(session['climbs'])+1}) ──")
        climb = build_climb(phase_names)
        session["climbs"].append(climb)
        grade_display = climb["grade_range"]
        if climb.get("perceived_grade"):
            grade_display += f" (felt {climb['perceived_grade']})"
        print(f"  Logged: {climb['color']} {grade_display} — {climb['outcome']}")
        if not confirm("Add another climb?", default=True):
            break


def pick_session(sessions):
    """Let user pick from recent sessions."""
    recent = sessions[-10:]
    recent.reverse()
    print("\nRecent sessions:")
    for i, s in enumerate(recent):
        n_climbs = len(s.get("climbs", []))
        print(f"  {i+1}. {s['date']} at {s['gym']} ({n_climbs} climbs)")
    while True:
        val = input("Pick a session (number): ").strip()
        try:
            idx = int(val) - 1
            if 0 <= idx < len(recent):
                # Find the original session in the list
                picked_id = recent[idx]["id"]
                for s in sessions:
                    if s["id"] == picked_id:
                        return s
        except ValueError:
            pass
        print(f"  Pick 1-{len(recent)}.")


# ── Viewing sessions ─────────────────────────────────────────────────────────


def view_sessions(args):
    """View past sessions with optional filters."""
    sessions = load_sessions()
    if not sessions:
        print("No sessions found.")
        return

    # Parse filters from args
    gym_filter = None
    date_filter = None
    grade_filter = None
    last_n = None

    i = 0
    while i < len(args):
        if args[i] in ("--gym", "-g") and i + 1 < len(args):
            gym_filter = args[i + 1].lower()
            i += 2
        elif args[i] in ("--date", "-d") and i + 1 < len(args):
            date_filter = args[i + 1]
            i += 2
        elif args[i] in ("--grade", "-r") and i + 1 < len(args):
            grade_filter = args[i + 1].upper()
            if not grade_filter.startswith("V"):
                grade_filter = "V" + grade_filter
            i += 2
        elif args[i] in ("--last", "-n") and i + 1 < len(args):
            try:
                last_n = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    filtered = sessions

    if gym_filter:
        filtered = [s for s in filtered if gym_filter in s["gym"].lower()]

    if date_filter:
        filtered = [s for s in filtered if s["date"].startswith(date_filter)]

    if grade_filter:
        filtered = [
            s for s in filtered
            if any(grade_filter in c.get("grade_range", "").upper() for c in s.get("climbs", []))
        ]

    if last_n:
        filtered = filtered[-last_n:]

    if not filtered:
        print("No sessions match your filters.")
        return

    for s in filtered:
        print_session_summary(s)


def print_session_summary(session):
    """Print a formatted summary of a session."""
    climbs = session.get("climbs", [])
    phases = session.get("phases", [])

    print(f"\n{'═' * 50}")
    print(f"  {session['date']} {session.get('time', '')}  —  {session['gym']}")
    print(f"  Duration: {session['duration_minutes']}min  |  Energy: {'*' * session['energy_level']}{'.' * (5 - session['energy_level'])}")
    if session.get("body_notes"):
        print(f"  Body: {session['body_notes']}")
    print(f"{'─' * 50}")

    if phases:
        phase_str = " → ".join(f"{p['type']}({p['duration_minutes']}m)" for p in phases)
        print(f"  Phases: {phase_str}")

    if not climbs:
        print("  No climbs logged.")
        return

    # Stats
    outcomes = {}
    grades = []
    for c in climbs:
        out = c.get("outcome", "?")
        outcomes[out] = outcomes.get(out, 0) + 1
        grades.append(c.get("grade_range", "?"))

    outcome_str = "  ".join(f"{k}: {v}" for k, v in sorted(outcomes.items()))
    print(f"  Climbs: {len(climbs)}  |  {outcome_str}")
    print()

    for i, c in enumerate(climbs, 1):
        grade_display = c["grade_range"]
        if c.get("perceived_grade"):
            grade_display += f" (felt {c['perceived_grade']})"
        felt = f" [{c['felt_difficulty']}]" if c.get("felt_difficulty") else ""
        phase_str = f" ({c['phase']})" if c.get("phase") else ""

        line = f"  {i:2}. {c['color']:10} {grade_display:12} {c['outcome']:8}{felt}"
        if c.get("attempts", 1) > 1:
            line += f"  {c['attempts']} attempts"
        line += phase_str
        print(line)

        tags = []
        if c.get("terrain"):
            tags.extend(c["terrain"])
        if c.get("holds"):
            tags.extend(c["holds"])
        if c.get("techniques"):
            tags.extend(c["techniques"])
        if tags:
            print(f"      tags: {', '.join(tags)}")
        if c.get("notes"):
            print(f"      note: {c['notes']}")


def view_detail(args):
    """View a single session in detail by date or index."""
    sessions = load_sessions()
    if not sessions:
        print("No sessions found.")
        return

    if not args:
        # Show the most recent session
        print_session_summary(sessions[-1])
        return

    query = args[0]

    # Try matching by date
    matches = [s for s in sessions if s["date"].startswith(query)]
    if matches:
        for s in matches:
            print_session_summary(s)
        return

    # Try matching by index (1-based, most recent first)
    try:
        idx = int(query)
        if 1 <= idx <= len(sessions):
            print_session_summary(sessions[-idx])
            return
    except ValueError:
        pass

    print(f"No session found matching '{query}'.")


# ── Editing sessions ─────────────────────────────────────────────────────


def edit_session_cmd(args):
    """Edit a previously created session."""
    sessions = load_sessions()
    if not sessions:
        print("No sessions found.")
        return

    # If a date/index was passed, try to find it directly
    if args:
        session = find_session(sessions, args[0])
    else:
        session = sessions[-1]
        print(f"\nMost recent session: {session['date']} at {session['gym']}")
        if not confirm("Edit this session?"):
            session = pick_session(sessions)
            if not session:
                return

    if not session:
        print(f"No session found matching '{args[0]}'.")
        return

    edit_session_menu(session, sessions)


def find_session(sessions, query):
    """Find a session by date prefix or 1-based reverse index."""
    matches = [s for s in sessions if s["date"].startswith(query)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"\nMultiple sessions match '{query}':")
        for i, s in enumerate(matches):
            print(f"  {i+1}. {s['date']} at {s['gym']}")
        while True:
            val = input("Pick one (number): ").strip()
            try:
                idx = int(val) - 1
                if 0 <= idx < len(matches):
                    return matches[idx]
            except ValueError:
                pass
            print(f"  Pick 1-{len(matches)}.")
    try:
        idx = int(query)
        if 1 <= idx <= len(sessions):
            return sessions[-idx]
    except ValueError:
        pass
    return None


def edit_session_menu(session, sessions):
    """Main edit menu for a session."""
    while True:
        print(f"\n{'═' * 50}")
        print(f"  Editing: {session['date']} at {session['gym']}")
        print(f"{'─' * 50}")
        print("  1. Edit session info (date, gym, duration, etc.)")
        print(f"  2. Edit a climb ({len(session.get('climbs', []))} climbs)")
        print(f"  3. Delete a climb")
        print(f"  4. Edit phases ({len(session.get('phases', []))} phases)")
        print("  5. Done")
        val = input("\nChoice [5]: ").strip()
        if not val or val == "5":
            save_sessions(sessions)
            print("Changes saved.")
            return
        elif val == "1":
            edit_session_info(session)
        elif val == "2":
            edit_climb_in_session(session)
        elif val == "3":
            delete_climb_in_session(session)
        elif val == "4":
            edit_phases_in_session(session)
        else:
            print("  Pick 1-5.")


def edit_session_info(session):
    """Edit session-level metadata."""
    print("\n── Edit Session Info ──")
    print("  Press Enter to keep current value.\n")
    session["date"] = ask("Date", default=session["date"])
    session["time"] = ask("Start time", default=session.get("time", ""))
    session["gym"] = ask("Gym name", default=session["gym"])
    session["duration_minutes"] = ask_int(
        "Duration (minutes)", default=session["duration_minutes"], min_val=1
    )
    session["energy_level"] = ask_int(
        "Energy level (1-5)", default=session["energy_level"], min_val=1, max_val=5
    )
    session["body_notes"] = ask(
        "Body notes", default=session.get("body_notes", "") or "(empty)", required=False
    )
    if session["body_notes"] == "(empty)":
        session["body_notes"] = ""
    print("  Session info updated.")


def edit_climb_in_session(session):
    """Pick and edit a single climb."""
    climbs = session.get("climbs", [])
    if not climbs:
        print("  No climbs to edit.")
        return

    print("\n── Pick a climb to edit ──")
    for i, c in enumerate(climbs, 1):
        grade = c["grade_range"]
        if c.get("perceived_grade"):
            grade += f" (felt {c['perceived_grade']})"
        print(f"  {i}. {c['color']} {grade} — {c['outcome']}")

    while True:
        val = input(f"Climb number (1-{len(climbs)}): ").strip()
        try:
            idx = int(val) - 1
            if 0 <= idx < len(climbs):
                break
        except ValueError:
            pass
        print(f"  Pick 1-{len(climbs)}.")

    climb = climbs[idx]
    edit_climb(climb, session)
    print(f"  Climb {idx+1} updated.")


def edit_climb(climb, session):
    """Edit all fields of a climb, showing current values as defaults."""
    print("\n── Edit Climb ──")
    print("  Press Enter to keep current value.\n")

    climb["color"] = ask("Hold color", default=climb["color"])
    climb["grade_range"] = ask("Grade range", default=climb["grade_range"])
    climb["perceived_grade"] = ask(
        "Perceived grade", default=climb.get("perceived_grade", "") or "(empty)", required=False
    )
    if climb["perceived_grade"] == "(empty)":
        climb["perceived_grade"] = ""
    climb["attempts"] = ask_int("Attempts", default=climb.get("attempts", 1), min_val=1)
    climb["outcome"] = ask_choice_with_default("Outcome:", OUTCOMES, climb.get("outcome", "sent"))
    climb["felt_difficulty"] = ask_choice_with_default(
        "Felt difficulty:", FELT_DIFFICULTIES, climb.get("felt_difficulty", ""), allow_empty=True
    ) or ""
    climb["terrain"] = ask_tags_with_default("Terrain:", TERRAIN_TAGS, climb.get("terrain", []))
    climb["holds"] = ask_tags_with_default("Holds:", HOLD_TAGS, climb.get("holds", []))
    climb["techniques"] = ask_tags_with_default(
        "Techniques:", TECHNIQUE_TAGS, climb.get("techniques", [])
    )

    phase_names = [p["type"] for p in session.get("phases", [])]
    if phase_names:
        climb["phase"] = ask_choice_with_default(
            "Phase:", phase_names, climb.get("phase", ""), allow_empty=True
        ) or ""

    climb["notes"] = ask(
        "Notes", default=climb.get("notes", "") or "(empty)", required=False
    )
    if climb["notes"] == "(empty)":
        climb["notes"] = ""


def delete_climb_in_session(session):
    """Delete a climb from the session."""
    climbs = session.get("climbs", [])
    if not climbs:
        print("  No climbs to delete.")
        return

    print("\n── Delete a climb ──")
    for i, c in enumerate(climbs, 1):
        grade = c["grade_range"]
        print(f"  {i}. {c['color']} {grade} — {c['outcome']}")

    while True:
        val = input(f"Climb number to delete (1-{len(climbs)}): ").strip()
        try:
            idx = int(val) - 1
            if 0 <= idx < len(climbs):
                break
        except ValueError:
            pass
        print(f"  Pick 1-{len(climbs)}.")

    removed = climbs.pop(idx)
    print(f"  Deleted: {removed['color']} {removed['grade_range']} — {removed['outcome']}")


def edit_phases_in_session(session):
    """Edit or add/remove phases."""
    phases = session.get("phases", [])

    while True:
        print("\n── Phases ──")
        if phases:
            for i, p in enumerate(phases, 1):
                print(f"  {i}. {p['type']} ({p['duration_minutes']}min)")
        else:
            print("  No phases.")

        print(f"\n  a. Add a phase")
        if phases:
            print(f"  e. Edit a phase")
            print(f"  d. Delete a phase")
        print(f"  q. Done with phases")

        val = input("Choice: ").strip().lower()
        if val == "q" or not val:
            break
        elif val == "a":
            phase_type = ask_choice("Phase type:", PHASE_TYPES)
            duration = ask_int("Duration (minutes)", min_val=1)
            notes = ask("Notes", required=False)
            phases.append({"type": phase_type, "duration_minutes": duration, "notes": notes or ""})
            print(f"  Added {phase_type} phase.")
        elif val == "e" and phases:
            idx = _pick_phase_index(phases)
            if idx is not None:
                p = phases[idx]
                p["type"] = ask_choice_with_default("Phase type:", PHASE_TYPES, p["type"])
                p["duration_minutes"] = ask_int("Duration (minutes)", default=p["duration_minutes"], min_val=1)
                p["notes"] = ask("Notes", default=p.get("notes", "") or "(empty)", required=False)
                if p["notes"] == "(empty)":
                    p["notes"] = ""
                print(f"  Phase updated.")
        elif val == "d" and phases:
            idx = _pick_phase_index(phases)
            if idx is not None:
                removed = phases.pop(idx)
                print(f"  Deleted {removed['type']} phase.")

    session["phases"] = phases


def _pick_phase_index(phases):
    """Helper to pick a phase by number."""
    while True:
        val = input(f"Phase number (1-{len(phases)}): ").strip()
        try:
            idx = int(val) - 1
            if 0 <= idx < len(phases):
                return idx
        except ValueError:
            pass
        print(f"  Pick 1-{len(phases)}.")


# ── Main ─────────────────────────────────────────────────────────────────────


USAGE = """\
climb.py — Rock climbing session tracker

Commands:
  new               Create a new climbing session
  add               Add climbs to the most recent session
  edit [DATE|N]     Edit a session (metadata, climbs, phases)
  view [filters]    View past sessions
    --gym, -g NAME      Filter by gym name
    --date, -d DATE     Filter by date (prefix match, e.g. 2026-02)
    --grade, -r GRADE   Filter sessions containing a grade (e.g. V4)
    --last, -n N        Show only last N sessions
  show [DATE|N]     Show detail for a session (by date or Nth most recent)
  help              Show this help message

Examples:
  python climb.py new
  python climb.py add
  python climb.py edit              # edit most recent session
  python climb.py edit 2026-02-08   # edit by date
  python climb.py edit 1            # edit most recent (by index)
  python climb.py view --last 5
  python climb.py view --gym "Movement" --grade V5
  python climb.py show 2026-02-08
"""


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "--help", "-h"):
        print(USAGE)
        return

    cmd = args[0]

    if cmd == "new":
        create_session()
    elif cmd == "add":
        add_to_session()
    elif cmd == "edit":
        edit_session_cmd(args[1:])
    elif cmd == "view":
        view_sessions(args[1:])
    elif cmd == "show":
        view_detail(args[1:])
    else:
        print(f"Unknown command: {cmd}")
        print(USAGE)


if __name__ == "__main__":
    main()
