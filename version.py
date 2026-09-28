"""Single source of truth for the app version.

Bump MAJOR for breaking changes, MINOR for new features, PATCH for fixes.
Build scripts (setup.py, build_dmg.sh, build_mas.sh, build_exe.bat) read this value.
"""

APP_NAME = "Nebula Note"
__version__ = "3.1.0"
# CFBundleVersion must increase for every App Store upload of the same version.
BUILD_NUMBER = "1"
