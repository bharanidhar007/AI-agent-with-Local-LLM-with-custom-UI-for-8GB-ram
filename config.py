"""
====================================================
LocalGPT Configuration
====================================================
All application constants are stored here.
"""

from pathlib import Path

# ====================================================
# Application
# ====================================================

APP_NAME = "LocalGPT"

APP_VERSION = "1.0.0"

WINDOW_WIDTH = 1500

WINDOW_HEIGHT = 900

MIN_WIDTH = 1200

MIN_HEIGHT = 700


# ====================================================
# Appearance
# ====================================================

DEFAULT_THEME = "Dark"

DEFAULT_COLOR_THEME = "blue"

DEFAULT_FONT = "Inter"

DEFAULT_FONT_SIZE = 14

CODE_FONT = "JetBrains Mono"

CODE_FONT_SIZE = 13

DEFAULT_FONT_COLOR = "white"


# ====================================================
# Ollama
# ====================================================

OLLAMA_HOST = "http://localhost:11434"

CHAT_ENDPOINT = "/api/chat"

GENERATE_ENDPOINT = "/api/generate"

TAGS_ENDPOINT = "/api/tags"

DEFAULT_MODEL = "qwen2.5-coder:3b"


# ====================================================
# Directories
# ====================================================

ROOT_DIR = Path(__file__).resolve().parent

ASSETS_DIR = ROOT_DIR / "assets"

ICON_DIR = ASSETS_DIR / "icons"

FONT_DIR = ASSETS_DIR / "fonts"

BACKGROUND_DIR = ASSETS_DIR / "backgrounds"

CHAT_DIR = ROOT_DIR / "chats"

CACHE_DIR = ROOT_DIR / "cache"

LOG_DIR = ROOT_DIR / "logs"


# ====================================================
# Files
# ====================================================

CONFIG_FILE = ROOT_DIR / "config.json"

SETTINGS_FILE = ROOT_DIR / "settings.json"

CHAT_INDEX = CHAT_DIR / "index.json"

APP_LOG = LOG_DIR / "app.log"

DEFAULT_BACKGROUND = BACKGROUND_DIR / "default.jpg"


# ====================================================
# Sidebar
# ====================================================

SIDEBAR_WIDTH = 280


# ====================================================
# Header
# ====================================================

HEADER_HEIGHT = 60


# ====================================================
# Input Box
# ====================================================

INPUT_HEIGHT = 120

MAX_INPUT_LINES = 12


# ====================================================
# Chat Bubble
# ====================================================

MESSAGE_CORNER_RADIUS = 18

MESSAGE_PADDING = 12


# ====================================================
# Animation
# ====================================================

FADE_SPEED = 15

SCROLL_SPEED = 2

TYPING_SPEED = 15


# ====================================================
# Colors
# ====================================================

LIGHT_BACKGROUND = "#F7F7F8"

DARK_BACKGROUND = "#1E1E1E"

USER_BUBBLE = "#2563EB"

ASSISTANT_BUBBLE = "#2B2B2B"

TEXT_WHITE = "#FFFFFF"

TEXT_BLACK = "#000000"


# ====================================================
# Background Image
# ====================================================

BACKGROUND_OPACITY = 0.30

BACKGROUND_BLUR = 5

BACKGROUND_BRIGHTNESS = 0.85


# ====================================================
# Drag & Drop
# ====================================================

SUPPORTED_FILES = [

    ".txt",
    ".py",
    ".json",
    ".md",
    ".pdf",
    ".docx",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"

]