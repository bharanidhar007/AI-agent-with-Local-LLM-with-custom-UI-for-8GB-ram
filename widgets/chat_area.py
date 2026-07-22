"""
====================================================
LocalGPT Chat Area
====================================================

Scrollable container for chat messages.

Messages are added dynamically as MessageBubble widgets.

====================================================
"""

import customtkinter as ctk


class ChatArea(ctk.CTkScrollableFrame):

    def __init__(self, master):

        super().__init__(

            master,

            fg_color="transparent",

            corner_radius=0

        )

        self.grid_columnconfigure(

            0,

            weight=1

        )

        self.message_widgets = []

    # --------------------------------------------------

    def add_message(

        self,

        widget

    ):
        """
        Add an already-created message widget.
        """

        widget.grid(

            row=len(self.message_widgets),

            column=0,

            sticky="ew",

            padx=20,

            pady=8

        )

        self.message_widgets.append(widget)

        self.after(

            10,

            self.scroll_to_bottom

        )

    # --------------------------------------------------

    def remove_last_message(self):

        if not self.message_widgets:

            return

        widget = self.message_widgets.pop()

        widget.destroy()

    # --------------------------------------------------

    def clear(self):

        for widget in self.message_widgets:

            widget.destroy()

        self.message_widgets.clear()

    # --------------------------------------------------

    def scroll_to_bottom(self):

        self._parent_canvas.yview_moveto(1.0)

    # --------------------------------------------------

    def message_count(self):

        return len(

            self.message_widgets

        )