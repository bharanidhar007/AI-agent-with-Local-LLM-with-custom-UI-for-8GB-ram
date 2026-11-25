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

class ModelManager:

    def __init__(self):

        self.host = OLLAMA_HOST

        self.current_model = DEFAULT_MODEL

    # --------------------------------------------------
