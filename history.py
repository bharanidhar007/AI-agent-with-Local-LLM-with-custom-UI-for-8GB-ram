"""
====================================================
LocalGPT History Manager
====================================================

Handles:
• New chats
• Save chats
• Load chats
• Delete chats
• Rename chats
• List chats

====================================================
"""

import json
import uuid
from pathlib import Path
from datetime import datetime

from config import CHAT_DIR


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

    def save_chat(

        self,

        chat_id,

        data

    ):

        data["updated"] = datetime.now().isoformat()

        with open(

            self.chat_file(chat_id),

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                data,

                f,

                indent=4,

                ensure_ascii=False

            )

    # --------------------------------------------------

    def load_chat(

        self,

        chat_id

    ):

        file = self.chat_file(chat_id)

        if not file.exists():

            return None

        with open(

            file,

            "r",

            encoding="utf-8"

        ) as f:

            return json.load(f)

    # --------------------------------------------------

    def delete_chat(

        self,

        chat_id

    ):

        file = self.chat_file(chat_id)

        if file.exists():

            file.unlink()

    # --------------------------------------------------

    def rename_chat(

        self,

        chat_id,

        title

    ):

        chat = self.load_chat(chat_id)

        if chat is None:

            return

        chat["title"] = title

        self.save_chat(

            chat_id,

            chat

        )

    # --------------------------------------------------

    
