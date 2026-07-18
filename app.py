"""
====================================================
 LocalGPT
----------------------------------------------------
Main entry point of the application.
Starts the CustomTkinter UI.
====================================================
"""

import customtkinter as ctk

from ui import LocalGPTApp


def configure_app():
    """
    Configure global appearance settings.
    """

    # Modes:
    # "System"
    # "Dark"
    # "Light"
    ctk.set_appearance_mode("Dark")

    # Themes:
    # "blue"
    # "green"
    # "dark-blue"
    ctk.set_default_color_theme("blue")


def main():
    """
    Application Entry Point
    """

    configure_app()

    app = LocalGPTApp()

    app.mainloop()


if __name__ == "__main__":
    main()