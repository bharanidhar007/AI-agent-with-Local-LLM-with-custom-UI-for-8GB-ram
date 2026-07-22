"""
====================================================
LocalGPT Application Context
====================================================
Creates ONE shared instance of all managers.
Every widget receives this context.
====================================================
"""

from settings import SettingsManager
from theme import ThemeManager
from history import HistoryManager
from chat import ChatEngine
from model_manager import ModelManager


class AppContext:

    def __init__(self):

        self.settings = SettingsManager()

        self.history = HistoryManager()

        self.models = ModelManager()

        self.chat = ChatEngine()

        self.theme = ThemeManager(self.settings)