"""Constants for climbing session data."""

OUTCOMES = ["sent", "flashed", "failed", "working"]
FELT_DIFFICULTIES = ["sandbagged", "on-grade", "soft"]
PHASE_TYPES = ["warmup", "working", "projecting", "cooldown"]
TERRAIN_TAGS = ["overhang", "slab", "vertical", "roof"]
HOLD_TAGS = ["crimps", "jugs", "slopers", "pinches", "pockets"]
TECHNIQUE_TAGS = ["dyno", "heel hook", "knee bar", "compression"]

V_GRADES = [f"V{i}" for i in range(13)]  # V0 through V12

OUTCOME_COLORS = {
    "sent": "#22c55e",
    "flashed": "#eab308",
    "failed": "#ef4444",
    "working": "#3b82f6",
}
