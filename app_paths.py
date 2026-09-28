"""Locate bundled resources and per-user data files for source, PyInstaller and py2app builds."""

import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))


def resource_path(relative_path):
    """Absolute path to a bundled resource such as 'assets/mermaid/mermaid.min.js'."""
    base_path = getattr(sys, "_MEIPASS", None)  # PyInstaller (Windows)
    if not base_path:
        base_path = os.environ.get("RESOURCEPATH")  # py2app (macOS)
    if not base_path or not os.path.exists(os.path.join(base_path, relative_path)):
        base_path = APP_DIR
    return os.path.join(base_path, relative_path)


def user_file(name):
    """Path for a per-user dotfile. Inside the macOS sandbox, ~ resolves to the app container."""
    return os.path.join(os.path.expanduser("~"), name)
