"""
====================================================
LocalGPT
Main Entry Point
====================================================
"""

import customtkinter as ctk

from app_context import AppContext
from ui import LocalGPTApp


def configure():

    ctk.set_appearance_mode("Dark")

    ctk.set_default_color_theme("blue")


def main():

    configure()

    context = AppContext()

    app = LocalGPTApp(context)

    app.mainloop()


if __name__ == "__main__":

    main()