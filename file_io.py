"""User-file I/O routed through Qt.

In the macOS App Sandbox, Qt (6.8+) takes over the security-scoped access that file dialogs and
Finder "Open With" grant, keeps persistent bookmarks for it, and only re-grants access to I/O done
through Qt's file engine. Python's built-in open()/os.stat() on those paths fail with EPERM, so every
read/write of a user-chosen file goes through these helpers. Outside the sandbox they behave like
normal file I/O. App-private files (config, snippets, backups) can keep using open().
"""

from PyQt6.QtCore import QFile, QFileInfo, QIODevice, QSaveFile


class FileAccessError(OSError):
    """Raised when Qt cannot open a file; permission_denied tells sandbox denials apart."""

    def __init__(self, path, message, permission_denied=False):
        super().__init__(message)
        self.path = path
        self.permission_denied = permission_denied


def _raise_for(device, path):
    error = device.error()
    denied = error in (QFile.FileError.PermissionsError, QFile.FileError.OpenError) and QFileInfo(path).exists()
    raise FileAccessError(path, f"{device.errorString()}: {path}", permission_denied=denied)


def exists(path):
    return bool(path) and QFileInfo(path).exists()


def is_file(path):
    return bool(path) and QFileInfo(path).isFile()


def file_state(path):
    """(modified-time ms, size) for external change detection, or None if unavailable."""
    info = QFileInfo(path)
    if not info.exists():
        return None
    return (info.lastModified().toMSecsSinceEpoch(), info.size())


def read_bytes(path):
    device = QFile(path)
    if not device.open(QIODevice.OpenModeFlag.ReadOnly):
        _raise_for(device, path)
    try:
        return bytes(device.readAll())
    finally:
        device.close()


def read_text(path):
    """Read UTF-8 text (a leading BOM is dropped). Raises UnicodeDecodeError for non-UTF-8 files."""
    return read_bytes(path).decode("utf-8-sig")


def write_bytes(path, data):
    device = QSaveFile(path)
    # Sandboxed apps usually may not create temp files next to a single granted file,
    # so fall back to writing the target directly when an atomic save isn't possible.
    device.setDirectWriteFallback(True)
    if not device.open(QIODevice.OpenModeFlag.WriteOnly):
        _raise_for(device, path)
    if device.write(data) != len(data):
        message = device.errorString()
        device.cancelWriting()
        raise FileAccessError(path, f"{message}: {path}")
    if not device.commit():
        raise FileAccessError(path, f"{device.errorString()}: {path}")


def write_text(path, text):
    write_bytes(path, text.encode("utf-8"))
