"""Layout constants, rank definitions, and font discovery."""

import os

# --- Package paths ---
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(PACKAGE_DIR, os.pardir, "images")
IMAGES_DIR = os.path.normpath(IMAGES_DIR)

# --- Layout constants ---
WIDTH, HEIGHT = 1920, 1080
BG_COLOR = (26, 26, 46)  # dark navy
BAR_HEIGHT = 15
HEADER_AREA_TOP = BAR_HEIGHT + 20
HEADER_AREA_HEIGHT = 140
BODY_TOP = HEADER_AREA_TOP + HEADER_AREA_HEIGHT
BODY_BOTTOM = HEIGHT - BAR_HEIGHT - 20
BODY_HEIGHT = BODY_BOTTOM - BODY_TOP
SIDE_MARGIN = 80

# --- Rank definitions ---
RANK_COLORS = {
    "lions":   {"primary": (255, 199, 44),  "accent": (0, 63, 135),  "bg": (51, 40, 9),  "logo": "rank_lion.png"},
    "tigers":  {"primary": (252, 106, 33),  "accent": (0, 63, 135),  "bg": (50, 21, 7),  "logo": "rank_tiger.png"},
    "wolves":  {"primary": (188, 208, 54),  "accent": (0, 63, 135),  "bg": (30, 33, 9),  "logo": "rank_wolf.png"},
    "bears":   {"primary": (0, 174, 239),   "accent": (0, 63, 135),  "bg": (0, 28, 38),  "logo": "rank_bear.png"},
    "webelos": {"primary": (0, 132, 61),    "accent": (0, 63, 135),  "bg": (0, 26, 12),  "logo": "rank_webelos.png"},
    "aol":     {"primary": (0, 132, 61),    "accent": (0, 63, 135),  "bg": (0, 26, 12),  "logo": "rank_webelos.png"},
}

RANK_DISPLAY = {
    "lions": "Lion",
    "tigers": "Tiger",
    "wolves": "Wolf",
    "bears": "Bear",
    "webelos": "Webelos",
    "aol": "Arrow of Light",
}

RANK_ORDER = ["lions", "tigers", "wolves", "bears", "webelos", "aol"]

# --- Font discovery ---
FONT_SEARCH_PATHS = [
    # msttcorefonts (Debian/Ubuntu: sudo apt install ttf-mscorefonts-installer)
    "/usr/share/fonts/truetype/msttcorefonts",
    # Common Linux paths
    "/usr/share/fonts/truetype",
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    # macOS
    "/Library/Fonts",
    "/System/Library/Fonts",
    os.path.expanduser("~/Library/Fonts"),
    # Windows
    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts"),
]


def _find_font(names):
    """Search for a font file by trying multiple names across system font dirs."""
    for directory in FONT_SEARCH_PATHS:
        for name in names:
            path = os.path.join(directory, name)
            if os.path.exists(path):
                return path
    return None


FONT_IMPACT = _find_font([
    "Impact.ttf", "impact.ttf",
]) or _find_font([
    "Arial_Bold.ttf", "Arial Bold.ttf", "arialbd.ttf",
    "DejaVuSans-Bold.ttf",
])

FONT_BOLD = _find_font([
    "Arial_Bold.ttf", "Arial Bold.ttf", "arialbd.ttf",
    "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf",
])

FONT_REGULAR = _find_font([
    "Arial.ttf", "arial.ttf",
    "DejaVuSans.ttf", "LiberationSans-Regular.ttf",
])

if not FONT_BOLD:
    FONT_BOLD = ""
if not FONT_IMPACT:
    FONT_IMPACT = FONT_BOLD
if not FONT_REGULAR:
    FONT_REGULAR = FONT_BOLD


def clean_award_name(name):
    """Clean up award names for display."""
    if name.endswith(" Adventure"):
        name = name[:-10]
    if name.endswith(" Emblem"):
        name = name[:-7]
    return name
