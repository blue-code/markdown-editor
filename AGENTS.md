# Repository Guidelines

## Project Structure & Module Organization
This is a Python desktop app built with PyQt6.
- `markdown_editor.py`: main application window, editor, dialogs, and UI actions.
- `i18n.py` / `localized_content.py`: UI strings and sample content for ko/en/ja/zh. Every user-visible string goes through `tr()`; add a key to all four languages (tests enforce parity).
- `web_view.py`: preview web view. macOS uses WKWebView (Qt WebEngine is not allowed on the Mac App Store); other platforms use Qt WebEngine.
- `preview_html.py`: preview / Mermaid viewer HTML shells; `file_io.py`: user-file I/O through QFile (required inside the App Sandbox).
- `mermaid_utils.py`, `markdown_tools.py`: pure helpers.
- `tests/`: unittest suites.
- Build and packaging scripts: `build_exe.bat`, `build_installer.bat`, `build_dmg.sh`, `build_mas.sh` (Mac App Store), `setup.py`, `installer.nsi`, `mas/`.
- Version lives in `app_version.py` only (`APP_VERSION`, plus `BUILD_NUMBER` for Mac App Store uploads); build scripts read it.
- Assets: `icon.ico`, `icon_source.png`, `splash.png`.

Keep new code in focused modules. If a feature is reusable, move logic out of `markdown_editor.py` into a helper module and add tests.

## Build, Test, and Development Commands
- `python -m venv venv` then `venv\Scripts\activate` (Windows): create and activate virtual environment.
- `pip install -r requirements.txt`: install runtime dependencies.
- `python markdown_editor.py`: run the app locally.
- `python -m unittest discover -s tests -v`: run test suite.
- `python -m py_compile markdown_editor.py mermaid_utils.py`: quick syntax check.
- `build_exe.bat`: build Windows executable.
- `build_installer.bat`: build NSIS installer (requires NSIS in PATH).
- `build_msix.ps1`: build Microsoft Store MSIX package (requires Windows SDK, fill `msix/store_identity.json`). See `docs/MS_STORE_배포가이드.md`.
- build 후에 dmg나, exe 파일에 버전 정보를 자동으로 붙여줘.  업데이트 할 때마다 그 성격 메이저, 마이터에 따라 버전정보를 업데이트 해줘.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation.
- `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_CASE` for constants.
- Keep UI slot methods short; extract complex logic into pure helper functions.
- Prefer explicit names over abbreviations. Add brief comments only where logic is non-obvious.

## Testing Guidelines
- Framework: standard `unittest`.
- Test files: `tests/test_*.py`.
- Test methods: `test_<behavior>` naming.
- Add/extend tests for parser, text transforms, and edge cases (empty input, Windows newlines, multiple blocks).

## Commit & Pull Request Guidelines
- Preferred commit prefixes: `feat :`, `fix :`, `refactor :`, `docs :`.
- Use concise, intent-focused messages (recent history includes Korean summaries; keep style consistent within a PR).
- PRs should include:
  - what changed and why,
  - test evidence (`unittest` output or equivalent),
  - screenshots/GIFs for UI-visible changes,
  - linked issue (if available).

## Security & Configuration Tips
- Do not commit local artifacts: `venv/`, `build/`, `dist/`, `__pycache__/`.
- User config is stored in home-directory dotfiles (for example `~/.markdownpro_config.json`); never hardcode secrets or machine-specific paths.
