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

    def new_chat(self):

        chat_id = str(uuid.uuid4())

        data = {

            "id": chat_id,

            "title": "New Chat",

            "created": datetime.now().isoformat(),

            "updated": datetime.now().isoformat(),

            "messages": []

        }

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

    def add_message(

        self,

        chat_id,

        role,

        content

    ):

        chat = self.load_chat(chat_id)

        if chat is None:

            return

        chat["messages"].append(

            {

                "role": role,

                "content": content

            }

        )

        self.save_chat(

            chat_id,

            chat

        )

    # --------------------------------------------------

    def list_chats(self):

        chats = []

        for file in self.chat_dir.glob("*.json"):

            try:

                with open(

                    file,

                    "r",

                    encoding="utf-8"

                ) as f:

                    data = json.load(f)

                    chats.append(data)

            except Exception:

                pass

        chats.sort(

            key=lambda x: x["updated"],

            reverse=True

        )

        return chats