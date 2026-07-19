"""
====================================================
LocalGPT Main Window
====================================================
"""

import customtkinter as ctk

from widgets.sidebar import Sidebar
from widgets.header import Header
from widgets.chat_area import ChatArea
from widgets.input_box import InputBox
from widgets.statusbar import StatusBar


class LocalGPTApp(ctk.CTk):
    """
    Main Application Window
    """

    def __init__(self):
        super().__init__()

        # ------------------------------------------------
        # Window
        # ------------------------------------------------

        self.title("LocalGPT")

        self.geometry("1500x900")

        self.minsize(1200, 700)

        # ------------------------------------------------
        # Grid
        # ------------------------------------------------

        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(1, weight=1)

        # ------------------------------------------------
        # Widgets
        # ------------------------------------------------

        self.sidebar = Sidebar(self)
        self.sidebar.grid(
            row=0,
            column=0,
            rowspan=3,
            sticky="ns"
        )

        self.header = Header(self)
        self.header.grid(
            row=0,
            column=1,
            sticky="ew"
        )

        self.chat_area = ChatArea(self)
        self.chat_area.grid(
            row=1,
            column=1,
            sticky="nsew"
        )

        self.input_box = InputBox(self)
        self.input_box.grid(
            row=2,
            column=1,
            sticky="ew"
        )

        self.status = StatusBar(self)
        self.status.place(
            relx=1.0,
            rely=1.0,
            anchor="se"
        )