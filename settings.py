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
    # UI
    # -------------------------

    "window_width": 1500,

    "window_height": 900,

    "sidebar_width": 280,

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

        try:

            with open(self.file, "r", encoding="utf-8") as f:

                loaded = json.load(f)

                self.settings.update(loaded)

        except Exception:

            self.settings = DEFAULT_SETTINGS.copy()

            self.save()

    # ------------------------------------------------

    def save(self):

        self.file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.file, "w", encoding="utf-8") as f:

            json.dump(

                self.settings,

                f,

                indent=4

            )

    # ------------------------------------------------

    def get(self, key, default=None):

        return self.settings.get(key, default)

    # ------------------------------------------------

    def set(self, key, value):

        self.settings[key] = value

        self.save()

    # ------------------------------------------------

    def reset(self):

        self.settings = DEFAULT_SETTINGS.copy()

        self.save()