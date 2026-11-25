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

    
    def configure_app():
    """
    Configure global appearance settings.
    """

