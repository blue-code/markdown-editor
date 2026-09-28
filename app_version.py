"""앱 버전의 단일 출처.

About 창, MSIX/py2app 매니페스트, 빌드 산출물 파일명(dmg/pkg/exe/msix)이 모두 여기서 읽어간다.
릴리스 성격에 따라 올린다: 호환 깨짐 → major, 기능 추가 → minor, 버그 수정 → patch.
"""

APP_NAME = "Nebula Note"
APP_VERSION = "1.3.0"
# Mac App Store: 같은 APP_VERSION 으로 다시 업로드할 때마다 올려야 하는 빌드 번호 (CFBundleVersion).
BUILD_NUMBER = "1"
