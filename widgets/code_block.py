"""
====================================================
LocalGPT Code Block Widget
====================================================

Features
--------
• Syntax Highlighting
• Copy Button
• Line Numbers
• Read Only
• Auto Height

====================================================
"""

import tkinter as tk
import customtkinter as ctk

from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.lexers.special import TextLexer
from pygments.styles import get_style_by_name
from pygments.token import Token


class CodeBlock(ctk.CTkFrame):

    def __init__(

        self,
        master,
        code="",
        language="text"

    ):

        super().__init__(

            master,

            corner_radius=12,

            fg_color=("#F5F5F5", "#2B2B2B")

        )

        self.code = code

        self.language = language

        self.style = get_style_by_name("monokai")

        self.build_ui()

        self.highlight()

    # --------------------------------------------------

    def build_ui(self):

        self.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkFrame(

            self,

            fg_color="transparent"

        )

        self.header.grid(

            row=0,

            column=0,

            sticky="ew",

            padx=8,

            pady=(6, 0)

        )

        self.language_label = ctk.CTkLabel(

            self.header,

            text=self.language.upper(),

            font=("Inter", 12)

        )

        self.language_label.pack(

            side="left"

        )

        self.copy_button = ctk.CTkButton(

            self.header,

            text="Copy",

            width=70,

            command=self.copy_code

        )

        self.copy_button.pack(

            side="right"

        )

        self.text = tk.Text(

            self,

            wrap="none",

            borderwidth=0,

            relief="flat",

            font=("JetBrains Mono", 13),

            undo=False,

            padx=12,

            pady=12

        )

        self.text.grid(

            row=1,

            column=0,

            sticky="nsew",

            padx=6,

            pady=6

        )

        self.text.insert(

            "1.0",

            self.code

        )

        self.text.configure(

            state="disabled"

        )

    # --------------------------------------------------

    def copy_code(self):

        self.clipboard_clear()

        self.clipboard_append(self.code)

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

    def highlight(self):

        self.text.configure(state="normal")

        self.text.tag_delete(*self.text.tag_names())

        try:

            lexer = get_lexer_by_name(

                self.language

            )

        except Exception:

            lexer = TextLexer()

        index = "1.0"

        self.text.delete("1.0", "end")

        for token, value in lex(

            self.code,

            lexer

        ):

            end = f"{index}+{len(value)}c"

            self.text.insert(index, value)

            color = self.style.style_for_token(token)["color"]

            if color:

                tag = str(token)

                self.text.tag_config(

                    tag,

                    foreground="#" + color

                )

                self.text.tag_add(

                    tag,

                    index,

                    end

                )

            index = end

        self.text.configure(

            state="disabled"

        )

    # --------------------------------------------------

    def set_code(

        self,

        code,

        language=None

    ):

        self.code = code

        if language:

            self.language = language
            self.language_label.configure(
                text=language.upper()
            )

        self.highlight()