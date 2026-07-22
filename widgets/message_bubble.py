"""
====================================================
LocalGPT Message Bubble
====================================================

ChatGPT / Claude inspired message widget.

Supports

✔ User messages
✔ Assistant messages
✔ Markdown
✔ Code blocks
✔ Streaming
✔ Copy response
✔ Future image support

====================================================
"""

import re

import customtkinter as ctk

from widgets.code_block import CodeBlock


class MessageBubble(ctk.CTkFrame):
    """
    One complete chat message.
    """

    def __init__(
        self,
        master,
        role="assistant",
        text="",
        max_width=850
    ):

        super().__init__(
            master,
            fg_color="transparent"
        )

        self.role = role

        self.text = text

        self.max_width = max_width

        self.code_blocks = []

        self.text_widgets = []

        self.build_ui()

        self.render(text)
    
        # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def build_ui(self):

        if self.role == "user":

            bubble_color = ("#D9FDD3", "#2D6A4F")
            anchor = "e"

        else:

            bubble_color = ("#FFFFFF", "#343541")
            anchor = "w"

        self.grid_columnconfigure(0, weight=1)

        self.container = ctk.CTkFrame(
            self,
            fg_color=bubble_color,
            corner_radius=16
        )

        self.container.grid(
            row=0,
            column=0,
            sticky=anchor,
            padx=12,
            pady=4
        )

        self.body = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.body.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=14
        )

        self.footer = ctk.CTkFrame(
            self.container,
            fg_color="transparent"
        )

        self.footer.pack(
            fill="x",
            padx=12,
            pady=(0, 10)
        )

        if self.role == "assistant":

            self.copy_button = ctk.CTkButton(
                self.footer,
                text="Copy",
                width=70,
                height=28,
                command=self.copy_response
            )

            self.copy_button.pack(
                side="right"
            )
    
        # --------------------------------------------------
    # Clipboard
    # --------------------------------------------------

    def copy_response(self):

        self.clipboard_clear()

        self.clipboard_append(self.text)

        if self.role == "assistant":

            self.copy_button.configure(
                text="Copied!"
            )

            self.after(
                1500,
                lambda: self.copy_button.configure(
                    text="Copy"
                )
            )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def clear(self):

        for widget in self.body.winfo_children():

            widget.destroy()

        self.text_widgets.clear()

        self.code_blocks.clear()

        # --------------------------------------------------
    # Rendering
    # --------------------------------------------------

    def render(self, text):

        """
        Render markdown text into widgets.
        """

        self.text = text

        self.clear()

        if not text:

            return

        lines = text.splitlines()

        paragraph = []

        inside_code = False

        code_language = "text"

        code_buffer = []

        for line in lines:

            # ------------------------------------------
            # Code Block Start / End
            # ------------------------------------------

            if line.strip().startswith("```"):

                if not inside_code:

                    inside_code = True

                    lang = line.strip()[3:].strip()

                    code_language = lang if lang else "text"

                    code_buffer = []

                else:

                    inside_code = False

                    self.add_code_block(

                        "\n".join(code_buffer),

                        code_language

                    )

                    code_buffer = []

                continue

            if inside_code:

                code_buffer.append(line)

                continue

            # ------------------------------------------
            # Empty Line
            # ------------------------------------------

            if line.strip() == "":

                if paragraph:

                    self.add_paragraph(

                        "\n".join(paragraph)

                    )

                    paragraph = []

                continue

            paragraph.append(line)

        if paragraph:

            self.add_paragraph(

                "\n".join(paragraph)

            )

    # --------------------------------------------------
    # Paragraph
    # --------------------------------------------------

    def add_paragraph(self, text):

        """
        Add a normal markdown paragraph.
        """

        label = ctk.CTkLabel(

            self.body,

            text=text,

            justify="left",

            anchor="w",

            wraplength=self.max_width,

            font=("Inter", 14)

        )

        label.pack(

            fill="x",

            anchor="w",

            pady=3

        )

        self.text_widgets.append(label)

    # --------------------------------------------------
    # Code Block
    # --------------------------------------------------

    def add_code_block(

        self,

        code,

        language

    ):

        widget = CodeBlock(

            self.body,

            code=code,

            language=language

        )

        widget.pack(

            fill="x",

            pady=8

        )

        self.code_blocks.append(widget)