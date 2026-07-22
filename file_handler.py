"""
====================================================
LocalGPT File Handler
====================================================

Handles:
• File Picker
• Drag & Drop Validation
• Reading Supported Files
• Image Selection
• Folder Selection

====================================================
"""

from pathlib import Path
from tkinter import filedialog

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document
except ImportError:
    Document = None


SUPPORTED_TEXT_FILES = {
    ".txt",
    ".md",
    ".py",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".html",
    ".css",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".c",
    ".cs",
    ".go",
    ".rs",
    ".php",
    ".sql",
    ".sh",
    ".bat"
}

SUPPORTED_IMAGES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp"
}

SUPPORTED_DOCUMENTS = {
    ".pdf",
    ".docx"
}


class FileHandler:

    def __init__(self):

        self.selected_files = []

    # --------------------------------------------------
    # File Dialog
    # --------------------------------------------------

    def select_files(self):

        files = filedialog.askopenfilenames()

        self.selected_files = list(files)

        return self.selected_files

    # --------------------------------------------------
    # Folder Dialog
    # --------------------------------------------------

    def select_folder(self):

        return filedialog.askdirectory()

    # --------------------------------------------------
    # Image Dialog
    # --------------------------------------------------

    def select_image(self):

        return filedialog.askopenfilename(

            filetypes=[

                ("Images", "*.png *.jpg *.jpeg *.webp *.bmp")

            ]

        )

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def is_supported(self, path):

        suffix = Path(path).suffix.lower()

        return (

            suffix in SUPPORTED_TEXT_FILES

            or suffix in SUPPORTED_IMAGES

            or suffix in SUPPORTED_DOCUMENTS

        )

    # --------------------------------------------------
    # Read File
    # --------------------------------------------------

    def read(self, path):

        suffix = Path(path).suffix.lower()

        if suffix in SUPPORTED_TEXT_FILES:

            return self._read_text(path)

        if suffix == ".pdf":

            return self._read_pdf(path)

        if suffix == ".docx":

            return self._read_docx(path)

        return None

    # --------------------------------------------------
    # Text
    # --------------------------------------------------

    def _read_text(self, path):

        with open(

            path,

            "r",

            encoding="utf-8",

            errors="ignore"

        ) as f:

            return f.read()

    # --------------------------------------------------
    # PDF
    # --------------------------------------------------

    def _read_pdf(self, path):

        if fitz is None:

            return "PyMuPDF is not installed."

        document = fitz.open(path)

        text = ""

        for page in document:

            text += page.get_text()

        document.close()

        return text

    # --------------------------------------------------
    # DOCX
    # --------------------------------------------------

    def _read_docx(self, path):

        if Document is None:

            return "python-docx is not installed."

        doc = Document(path)

        return "\n".join(

            paragraph.text

            for paragraph in doc.paragraphs

        )

    # --------------------------------------------------
    # Image
    # --------------------------------------------------

    def is_image(self, path):

        return Path(path).suffix.lower() in SUPPORTED_IMAGES

    # --------------------------------------------------
    # Extension
    # --------------------------------------------------

    def extension(self, path):

        return Path(path).suffix.lower()

    # --------------------------------------------------
    # Filename
    # --------------------------------------------------

    def filename(self, path):

        return Path(path).name

    # --------------------------------------------------
    # File Size
    # --------------------------------------------------

    def size(self, path):

        return Path(path).stat().st_size