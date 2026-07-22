"""
====================================================
LocalGPT Theme Manager
====================================================

Handles

• Appearance Mode
• Font Colors
• Background Images
• Blur
• Brightness
• Opacity
• Theme Events

====================================================
"""

from pathlib import Path

import customtkinter as ctk

from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter

from settings import SettingsManager


class ThemeManager:

    def __init__(self, settings):

        self.settings = settings

        self.callbacks = []

    # ------------------------------------------------
    # Theme Callbacks
    # ------------------------------------------------

    def register(self, callback):

        if callback not in self.callbacks:

            self.callbacks.append(callback)

    def unregister(self, callback):

        if callback in self.callbacks:

            self.callbacks.remove(callback)

    def notify(self):

        for callback in self.callbacks:

            try:

                callback()

            except Exception:

                pass

    # ------------------------------------------------
    # Appearance
    # ------------------------------------------------

    @property
    def appearance(self):

        return self.settings.get(

            "appearance_mode",

            "Dark"

        )

    def apply(self):

        ctk.set_appearance_mode(

            self.appearance

        )

    def set_appearance(

        self,

        mode

    ):

        self.settings.set(

            "appearance_mode",

            mode

        )

        self.apply()

        self.notify()

    # ------------------------------------------------
    # Font
    # ------------------------------------------------

    @property
    def font_color(self):

        return self.settings.get(

            "font_color",

            "white"

        )

    def set_font_color(

        self,

        color

    ):

        self.settings.set(

            "font_color",

            color

        )

        self.notify()

    # ------------------------------------------------
    # Background
    # ------------------------------------------------

    @property
    def background(self):

        return self.settings.get(

            "background_image",

            ""

        )

    def set_background(

        self,

        image_path

    ):

        self.settings.set(

            "background_image",

            image_path

        )

        self.notify()

    # ------------------------------------------------
    # Blur
    # ------------------------------------------------

    @property
    def blur(self):

        return self.settings.get(

            "background_blur",

            5

        )

    def set_blur(

        self,

        value

    ):

        self.settings.set(

            "background_blur",

            value

        )

        self.notify()

    # ------------------------------------------------
    # Brightness
    # ------------------------------------------------

    @property
    def brightness(self):

        return self.settings.get(

            "background_brightness",

            0.85

        )

    def set_brightness(

        self,

        value

    ):

        self.settings.set(

            "background_brightness",

            value

        )

        self.notify()

    # ------------------------------------------------
    # Opacity
    # ------------------------------------------------

    @property
    def opacity(self):

        return self.settings.get(

            "background_opacity",

            0.30

        )

    def set_opacity(

        self,

        value

    ):

        self.settings.set(

            "background_opacity",

            value

        )

        self.notify()

    # ------------------------------------------------
    # Image Processing
    # ------------------------------------------------

    def load_background(

        self,

        size=None

    ):

        path = self.background

        if not path:

            return None

        file = Path(path)

        if not file.exists():

            return None

        image = Image.open(file).convert("RGBA")

        if size:

            image = image.resize(

                size,

                Image.LANCZOS

            )

        if self.blur > 0:

            image = image.filter(

                ImageFilter.GaussianBlur(

                    radius=self.blur

                )

            )

        enhancer = ImageEnhance.Brightness(

            image

        )

        image = enhancer.enhance(

            self.brightness

        )

        alpha = image.getchannel("A")

        alpha = alpha.point(

            lambda p: int(

                p * self.opacity

            )

        )

        image.putalpha(alpha)

        return ctk.CTkImage(

            light_image=image,

            dark_image=image,

            size=image.size

        )