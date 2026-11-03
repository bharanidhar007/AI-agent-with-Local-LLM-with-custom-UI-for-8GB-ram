"""
====================================================
LocalGPT Chat Engine
====================================================

Handles:
• Chat History
• Streaming Responses
• Ollama Communication
• Stop Generation

====================================================
"""

import json
import requests
import threading

from config import (
    OLLAMA_HOST,
    CHAT_ENDPOINT,
    DEFAULT_MODEL
)


class ChatEngine:

    def __init__(self):

        self.model = DEFAULT_MODEL

        self.messages = []

        self.stop_requested = False

    # --------------------------------------------------

    def set_model(self, model):

        self.model = model

    # --------------------------------------------------

   
        )

    # --------------------------------------------------

    def add_assistant_message(self, text):

        self.messages.append(
            {
                "role": "assistant",
                "content": text
            }
        )

    # --------------------------------------------------

    def stop(self):

        self.stop_requested = True

    # --------------------------------------------------

    def stream_chat(
        self,
        prompt,
        on_chunk,
        on_complete,
        on_error=None
    ):

        self.stop_requested = False

        self.add_user_message(prompt)

        thread = threading.Thread(

            target=self._worker,

            args=(
                on_chunk,
                on_complete,
                on_error
            ),

            daemon=True

        )

        thread.start()

    # --------------------------------------------------

  
      
