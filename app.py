"""
====================================================
 LocalGPT
----------------------------------------------------
Main entry point of the application.
Starts the CustomTkinter UI.
====================================================
"""


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

  

    # ------------------------------------------------

    def reset(self):

        self.settings = DEFAULT_SETTINGS.copy()

        self.save()



class HistoryManager:

    def __init__(self):

        self.chat_dir = Path(CHAT_DIR)

        self.chat_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # --------------------------------------------------

        self.save_chat(chat_id, data)

        return chat_id

    # --------------------------------------------------

    def chat_file(self, chat_id):

        return self.chat_dir / f"{chat_id}.json"

    # --------------------------------------------------

    
