"""
====================================================
LocalGPT Settings Manager
====================================================
Handles loading and saving user settings.
====================================================
"""

import json
from pathlib import Path

from config import SETTINGS_FILE


DEFAULT_SETTINGS = {

    # -------------------------
    # Appearance
    # -------------------------

    "appearance_mode": "Dark",

    "color_theme": "blue",

    "font_color": "white",

    "font_size": 14,

    # -------------------------
    # Background
    # -------------------------

    "background_image": "",

    "background_opacity": 0.30,

    "background_blur": 5,

    "background_brightness": 0.85,

    # -------------------------
    # Chat
    # -------------------------

    "model": "qwen2.5-coder:3b",

    "stream_response": True,

    "save_history": True,

    "auto_scroll": True,

    # -------------------------
    # Misc
    # -------------------------

    "animations": True,

    "typing_indicator": True

}


class SettingsManager:
    """
    Handles application settings.
    """

    def __init__(self):

        self.file = Path(SETTINGS_FILE)

        self.settings = DEFAULT_SETTINGS.copy()

        self.load()

    # ------------------------------------------------

    def load(self):

        if not self.file.exists():

            self.save()

            return
