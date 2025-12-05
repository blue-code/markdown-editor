@echo off
rem MarkdownPro Windows 빌드 스크립트

python -m venv venv
call venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

pyinstaller --noconfirm --windowed --name MarkdownPro markdown_editor.py

if exist dist\MarkdownPro\MarkdownPro.exe (
    echo.
    echo 빌드 완료! 결과: dist\MarkdownPro\MarkdownPro.exe
) else (
    echo.
    echo 빌드에 실패했습니다. 위 로그를 확인하세요.
)
