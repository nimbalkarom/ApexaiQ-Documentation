"""
classifier.py
=============
File classification engine based on extensions, compound extensions,
and customizable user mappings.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("EnterpriseOrganizer.Classifier")

DEFAULT_CATEGORIES: Dict[str, List[str]] = {
    "Documents": [".pdf", ".doc", ".docx", ".odt", ".rtf"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff"],
    "Videos": [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Archives": [
        ".tar.gz", ".tar.bz2", ".tar.xz",
        ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"
    ],
    "Code": [
        ".py", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".js", ".ts",
        ".html", ".css", ".go", ".rs", ".php", ".rb", ".swift", ".kt"
    ],
    "Data": [".csv", ".json", ".xml", ".yaml", ".yml", ".sql", ".sqlite", ".db"],
    "Spreadsheets": [".xlsx", ".xls", ".ods"],
    "Presentations": [".pptx", ".ppt", ".odp"],
    "Text": [".txt", ".md", ".log"],
    "Executables": [".exe", ".msi", ".bin", ".sh", ".bat", ".cmd"],
    "Others": [],
}


class FileClassifier:
    """
    Classifies files into standardized or custom categories based on extensions
    and compound file extensions (.tar.gz).
    """

    def __init__(self, custom_categories: Optional[Dict[str, List[str]]] = None):
        self.category_map: Dict[str, str] = {}
        self.categories: Dict[str, List[str]] = {}
        self._load_categories(custom_categories)

    def _load_categories(self, custom_categories: Optional[Dict[str, List[str]]] = None) -> None:
        """Merge default categories with any user overrides."""
        # Deep copy defaults
        merged: Dict[str, List[str]] = {
            cat: list(exts) for cat, exts in DEFAULT_CATEGORIES.items()
        }

        if custom_categories:
            for cat, exts in custom_categories.items():
                norm_exts = [
                    e.lower() if e.startswith(".") else f".{e.lower()}"
                    for e in exts
                ]
                if cat in merged:
                    for e in norm_exts:
                        if e not in merged[cat]:
                            merged[cat].append(e)
                else:
                    merged[cat] = norm_exts

        self.categories = merged
        self.category_map.clear()

        # Build reverse lookup map
        for cat_name, extensions in self.categories.items():
            for ext in extensions:
                self.category_map[ext.lower()] = cat_name

    def classify_filename(self, filename: str) -> str:
        """
        Classify a file name, checking for multi-part compound extensions first
        (e.g., '.tar.gz') before single extensions (e.g., '.pdf').
        """
        lower_name = filename.lower()

        # Check multi-part extensions (ordered longest first)
        compound_exts = sorted(
            [ext for ext in self.category_map if ext.count(".") > 1],
            key=len,
            reverse=True,
        )
        for compound in compound_exts:
            if lower_name.endswith(compound):
                return self.category_map[compound]

        # Check single extension
        suffix = Path(filename).suffix.lower()
        if suffix:
            return self.category_map.get(suffix, "Others")

        return "Others"

    def classify(self, extension: str) -> str:
        """Return category name for the given file extension, or 'Others'."""
        ext = extension.lower().strip()
        if not ext:
            return "Others"
        if not ext.startswith("."):
            ext = f".{ext}"
        return self.category_map.get(ext, "Others")

    def get_all_categories(self) -> List[str]:
        """Return sorted list of all active category names."""
        return sorted(self.categories.keys())

    def get_extensions_for_category(self, category: str) -> List[str]:
        """Return all registered extensions for a category."""
        return list(self.categories.get(category, []))
