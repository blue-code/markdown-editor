"""Print the highest deployment target (LC_BUILD_VERSION minos) among a bundle's Mach-O files.

The App Store rejects apps whose LSMinimumSystemVersion is lower than what a bundled binary needs.
Usage: python mas/min_macos.py "dist/Nebula Note.app" [floor]
"""

import os
import re
import subprocess
import sys


def version_key(text):
    return tuple(int(part) for part in text.split("."))


def binary_minimums(path):
    output = subprocess.run(["otool", "-l", path], capture_output=True, text=True).stdout
    found = re.findall(r"minos (\d+(?:\.\d+)*)", output)
    found += re.findall(r"LC_VERSION_MIN_MACOSX[\s\S]*?version (\d+(?:\.\d+)*)", output)
    return found


def main(app_path, floor="11.0"):
    best = floor
    for root, _dirs, files in os.walk(app_path):
        for name in files:
            path = os.path.join(root, name)
            if os.path.islink(path):
                continue
            with open(path, "rb") as f:
                magic = f.read(4)
            if magic not in (b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe"):
                continue
            for minimum in binary_minimums(path):
                if version_key(minimum) > version_key(best):
                    best = minimum
    parts = best.split(".")
    print(".".join(parts + ["0"] * (2 - len(parts))))


if __name__ == "__main__":
    main(*sys.argv[1:])
