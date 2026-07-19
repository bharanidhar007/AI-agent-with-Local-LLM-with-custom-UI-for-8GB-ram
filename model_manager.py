"""
====================================================
LocalGPT Model Manager
====================================================
Handles:

• Detecting Ollama
• Listing installed models
• Switching models
====================================================
"""

import requests

from config import (
    OLLAMA_HOST,
    TAGS_ENDPOINT,
    DEFAULT_MODEL
)


class ModelManager:

    def __init__(self):

        self.host = OLLAMA_HOST

        self.current_model = DEFAULT_MODEL

    # --------------------------------------------------

    @property
    def url(self):

        return self.host + TAGS_ENDPOINT

    # --------------------------------------------------

    def ollama_running(self):

        try:

            requests.get(self.url, timeout=2)

            return True

        except Exception:

            return False

    # --------------------------------------------------

    def get_models(self):

        if not self.ollama_running():

            return []

        try:

            response = requests.get(self.url)

            data = response.json()

            models = []

            for model in data.get("models", []):

                models.append(model["name"])

            return models

        except Exception:

            return []

    # --------------------------------------------------

    def set_model(self, model_name):

        self.current_model = model_name

    # --------------------------------------------------

    def get_model(self):

        return self.current_model

    # --------------------------------------------------

    def has_model(self, model_name):

        return model_name in self.get_models()

    # --------------------------------------------------

    def refresh(self):

        return self.get_models()