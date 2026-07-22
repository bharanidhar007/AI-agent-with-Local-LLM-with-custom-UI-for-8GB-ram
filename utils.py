"""
====================================================
LocalGPT Utility Functions
====================================================

Common helper functions used throughout the application.

====================================================
"""

import json
import re
from pathlib import Path
from datetime import datetime
from tkinter import filedialog


# --------------------------------------------------
# Directory
# --------------------------------------------------

def ensure_directory(path):

    """
    Create directory if it doesn't exist.
    """

    Path(path).mkdir(
        parents=True,
        exist_ok=True
    )


# --------------------------------------------------
# JSON
# --------------------------------------------------

def load_json(file_path, default=None):

    """
    Load JSON file safely.
    """

    file = Path(file_path)

    if not file.exists():
        return default

    try:

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception:

        return default


def save_json(file_path, data):

    """
    Save JSON safely.
    """

    file = Path(file_path)

    ensure_directory(file.parent)

    with open(
        file,
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
# File Dialog
# --------------------------------------------------

def open_file_dialog(filetypes=None):

    """
    Open file picker.
    """

    if filetypes is None:

        filetypes = [

            ("All Files", "*.*")

        ]

    return filedialog.askopenfilename(

        filetypes=filetypes

    )


# --------------------------------------------------
# Filename
# --------------------------------------------------

def sanitize_filename(name):

    """
    Remove invalid filename characters.
    """

    return re.sub(

        r'[<>:"/\\\\|?*]',

        "_",

        name

    )


# --------------------------------------------------
# File Size
# --------------------------------------------------

def human_file_size(size):

    """
    Convert bytes into readable string.
    """

    units = [

        "B",

        "KB",

        "MB",

        "GB",

        "TB"

    ]

    size = float(size)

    for unit in units:

        if size < 1024:

            return f"{size:.1f} {unit}"

        size /= 1024

    return f"{size:.1f} PB"


# --------------------------------------------------
# Time
# --------------------------------------------------

def format_timestamp(timestamp):

    """
    Convert ISO timestamp into readable format.
    """

    try:

        dt = datetime.fromisoformat(timestamp)

        return dt.strftime(

            "%d %b %Y %I:%M %p"

        )

    except Exception:

        return timestamp


# --------------------------------------------------
# Chat Titles
# --------------------------------------------------

def generate_chat_title(text, max_length=40):

    """
    Generate a chat title from the first user message.
    """

    title = " ".join(

        text.strip().split()

    )

    if len(title) > max_length:

        title = title[:max_length].rstrip()

        title += "..."

    return title or "New Chat"


# --------------------------------------------------
# Text
# --------------------------------------------------

def truncate(text, length=100):

    """
    Truncate long text.
    """

    if len(text) <= length:

        return text

    return text[:length] + "..."