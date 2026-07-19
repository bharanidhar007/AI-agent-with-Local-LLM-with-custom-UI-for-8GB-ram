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

    def clear_chat(self):

        self.messages = []

    # --------------------------------------------------

    def add_user_message(self, text):

        self.messages.append(
            {
                "role": "user",
                "content": text
            }
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

    def _worker(

        self,

        on_chunk,

        on_complete,

        on_error

    ):

        try:

            response = requests.post(

                OLLAMA_HOST + CHAT_ENDPOINT,

                json={

                    "model": self.model,

                    "messages": self.messages,

                    "stream": True

                },

                stream=True,

                timeout=300

            )

            response.raise_for_status()

            assistant_text = ""

            for line in response.iter_lines():

                if self.stop_requested:

                    break

                if not line:

                    continue

                data = json.loads(line)

                if "message" in data:

                    chunk = data["message"]["content"]

                    assistant_text += chunk

                    if on_chunk:

                        on_chunk(chunk)

                if data.get("done", False):

                    break

            self.add_assistant_message(

                assistant_text

            )

            if on_complete:

                on_complete(

                    assistant_text

                )

        except Exception as e:

            if on_error:

                on_error(str(e))