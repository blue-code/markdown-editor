# Repository Guidelines

## Project Structure & Module Organization
This is a Python desktop app built with PyQt6.
- `markdown_editor.py`: main application window, editor, preview, dialogs, and UI actions.
- `mermaid_utils.py`: Mermaid block extraction helpers used by preview/viewer logic.
- `tests/test_mermaid_blocks.py`: unit tests for Mermaid parsing behavior.
- Build and packaging scripts: `build_exe.bat`, `build_installer.bat`, `build_dmg.sh`, `setup.py`, `installer.nsi`.
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
