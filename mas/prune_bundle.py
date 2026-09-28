"""Strip the py2app bundle down to the Qt pieces Nebula Note actually uses.

PyQt6 wheels ship every Qt module (Quick, 3D, Multimedia, Bluetooth, Positioning, WebEngine...).
Unused binaries bloat the download and make App Store review flag APIs we never call
(e.g. Bluetooth/location usage descriptions), so everything outside the keep-lists is removed.
The script then verifies that every @rpath dependency of the remaining Qt binaries still exists.

Usage: python mas/prune_bundle.py "dist/Nebula Note.app"
"""

import glob
import os
import shutil
import subprocess
import sys

KEEP_PYQT_MODULES = {"QtCore", "QtGui", "QtWidgets", "QtPrintSupport", "sip"}
KEEP_FRAMEWORKS = {"QtCore", "QtGui", "QtWidgets", "QtPrintSupport", "QtDBus"}
KEEP_PLUGINS = {
    "platforms": {"libqcocoa.dylib"},
    "styles": {"libqmacstyle.dylib"},
    "imageformats": {"libqgif.dylib", "libqico.dylib", "libqjpeg.dylib", "libqicns.dylib"},
}
KEEP_TRANSLATIONS = {"qtbase_en.qm", "qtbase_ko.qm", "qtbase_ja.qm", "qtbase_zh_CN.qm"}


def remove(path):
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path)
    elif os.path.lexists(path):
        os.remove(path)


def prune(app_path):
    site = glob.glob(os.path.join(app_path, "Contents/Resources/lib/python3.*"))[0]
    pyqt = os.path.join(site, "PyQt6")
    qt = os.path.join(pyqt, "Qt6")

    for entry in os.listdir(pyqt):
        full = os.path.join(pyqt, entry)
        if entry.endswith((".so", ".pyi")):
            if entry.split(".")[0] not in KEEP_PYQT_MODULES:
                remove(full)
        elif entry in ("bindings", "lupdate", "uic", "py.typed"):
            remove(full)

    for entry in os.listdir(qt):
        if entry not in ("lib", "plugins", "translations"):
            remove(os.path.join(qt, entry))

    lib = os.path.join(qt, "lib")
    for entry in os.listdir(lib):
        if not (entry.endswith(".framework") and entry[: -len(".framework")] in KEEP_FRAMEWORKS):
            remove(os.path.join(lib, entry))

    plugins = os.path.join(qt, "plugins")
    for category in os.listdir(plugins):
        keep = KEEP_PLUGINS.get(category)
        category_path = os.path.join(plugins, category)
        if keep is None:
            remove(category_path)
            continue
        for entry in os.listdir(category_path):
            if entry not in keep:
                remove(os.path.join(category_path, entry))

    translations = os.path.join(qt, "translations")
    for entry in os.listdir(translations):
        if entry not in KEEP_TRANSLATIONS:
            remove(os.path.join(translations, entry))

    # Framework bundles carry headers and other build-time files the App Store rejects or ignores.
    for framework in glob.glob(os.path.join(lib, "*.framework")):
        for pattern in ("Headers", "Versions/*/Headers", "*.prl", "Versions/*/*.prl"):
            for path in glob.glob(os.path.join(framework, pattern)):
                remove(path)

    # Static libraries / build metadata anywhere in the bundle are dead weight.
    for pattern in ("**/*.a", "**/*.prl", "**/*.pyi", "**/__pycache__"):
        for path in glob.glob(os.path.join(app_path, pattern), recursive=True):
            remove(path)

    verify(qt, lib)


def verify(qt, lib):
    binaries = glob.glob(os.path.join(qt, "..", "*.so")) + glob.glob(os.path.join(qt, "plugins/*/*.dylib"))
    binaries += glob.glob(os.path.join(lib, "*.framework/Versions/A/*"))
    missing = set()
    for binary in binaries:
        if not os.path.isfile(binary):
            continue
        output = subprocess.run(["otool", "-L", binary], capture_output=True, text=True).stdout
        for line in output.splitlines()[1:]:
            dep = line.strip().split(" ")[0]
            if dep.startswith("@rpath/Qt") and ".framework/" in dep:
                name = dep.split("/")[1][: -len(".framework")]
                if name not in KEEP_FRAMEWORKS:
                    missing.add(f"{os.path.basename(binary)} -> {name}")
    if missing:
        sys.exit("Pruned Qt frameworks are still referenced:\n  " + "\n  ".join(sorted(missing)))


if __name__ == "__main__":
    prune(sys.argv[1])
    print("Bundle pruned.")
