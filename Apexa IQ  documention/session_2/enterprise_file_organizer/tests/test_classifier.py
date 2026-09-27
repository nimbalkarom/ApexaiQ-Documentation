"""
Unit tests for FileClassifier component.
Tests default classifications, case insensitivity, compound extensions,
and custom overrides.
"""

from organizer.classifier import FileClassifier


def test_default_classification():
    classifier = FileClassifier()

    # Documents
    assert classifier.classify(".pdf") == "Documents"
    assert classifier.classify(".doc") == "Documents"
    assert classifier.classify(".docx") == "Documents"

    # Images
    assert classifier.classify(".jpg") == "Images"
    assert classifier.classify(".PNG") == "Images"

    # Code
    assert classifier.classify(".py") == "Code"
    assert classifier.classify(".java") == "Code"
    assert classifier.classify(".cpp") == "Code"

    # Audio & Video
    assert classifier.classify(".mp3") == "Audio"
    assert classifier.classify(".mp4") == "Videos"

    # Spreadsheets & Presentations
    assert classifier.classify(".xlsx") == "Spreadsheets"
    assert classifier.classify(".pptx") == "Presentations"

    # Unknown
    assert classifier.classify(".xyz123") == "Others"
    assert classifier.classify("") == "Others"


def test_classify_filename_and_compound_extensions():
    classifier = FileClassifier()

    assert classifier.classify_filename("archive.tar.gz") == "Archives"
    assert classifier.classify_filename("source.tar.bz2") == "Archives"
    assert classifier.classify_filename("notes.txt") == "Text"
    assert classifier.classify_filename("LICENSE") == "Others"
    assert classifier.classify_filename("script.min.js") == "Code"


def test_extension_without_dot():
    classifier = FileClassifier()
    assert classifier.classify("pdf") == "Documents"
    assert classifier.classify("zip") == "Archives"


def test_custom_categories_and_helpers():
    custom = {
        "3D_Models": [".obj", ".stl", ".fbx"],
        "Documents": [".custom_doc"],
    }
    classifier = FileClassifier(custom_categories=custom)

    assert classifier.classify(".obj") == "3D_Models"
    assert classifier.classify(".stl") == "3D_Models"
    assert classifier.classify(".custom_doc") == "Documents"
    assert classifier.classify(".pdf") == "Documents"  # Retains base mappings

    categories = classifier.get_all_categories()
    assert "3D_Models" in categories
    assert "Documents" in categories

    exts = classifier.get_extensions_for_category("3D_Models")
    assert ".obj" in exts
    assert ".stl" in exts
