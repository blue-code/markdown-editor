#!/bin/bash
#
# Nebula Note - Mac App Store 빌드 스크립트
#
#   ./build_mas.sh               # 앱 빌드 + 서명 + 설치 패키지(.pkg) 생성
#   ./build_mas.sh --upload      # 위 과정 + App Store Connect 업로드
#   ./build_mas.sh --local-test  # ad-hoc 서명(샌드박스 적용)으로 로컬 실행 테스트용 앱만 생성
#
# 필요:
#   - "Apple Distribution" 및 "3rd Party Mac Developer Installer" 인증서 (키체인)
#   - mas/NebulaNote_MAS.provisionprofile  (python mas/asc.py ensure-profile ... 로 생성)
#   - 업로드 시: ASC_KEY_ID, ASC_ISSUER_ID 환경변수 (~/.appstoreconnect/private_keys/AuthKey_<ID>.p8)
#
set -euo pipefail
cd "$(dirname "$0")"

MODE="${1:-package}"
BUNDLE_ID="${NEBULA_BUNDLE_ID:-com.blueCode.NebulaNote}"
TEAM_ID="${NEBULA_TEAM_ID:-KUDC7C6Z9H}"
APP_SIGN_IDENTITY="${NEBULA_APP_IDENTITY:-Apple Distribution: Byoungho Kim (KUDC7C6Z9H)}"
PKG_SIGN_IDENTITY="${NEBULA_PKG_IDENTITY:-3rd Party Mac Developer Installer: Byoungho Kim (KUDC7C6Z9H)}"
PROFILE="mas/NebulaNote_MAS.provisionprofile"
# Homebrew Python targets only the latest macOS; python-build-standalone (via uv) targets macOS 11+.
PYTHON="${NEBULA_PYTHON:-$(uv python find 3.12 2>/dev/null || true)}"
[ -x "$PYTHON" ] || { echo "❌ Python 3.12 이 필요합니다: uv python install 3.12"; exit 1; }
VENV="venv-mas"

APP_NAME=$("$PYTHON" -c "import app_version; print(app_version.APP_NAME)")
VERSION=$("$PYTHON" -c "import app_version; print(app_version.APP_VERSION)")
BUILD_NUMBER=$("$PYTHON" -c "import app_version; print(app_version.BUILD_NUMBER)")
APP="dist/${APP_NAME}.app"
PKG="dist/NebulaNote-${VERSION}-${BUILD_NUMBER}-mas.pkg"

echo "▶ ${APP_NAME} ${VERSION} (${BUILD_NUMBER}) — Mac App Store build [${MODE}]"

# ===== 1. 환경 =====
if [ ! -x "$VENV/bin/python" ]; then
    "$PYTHON" -m venv "$VENV"
fi
"$VENV/bin/pip" install -q --upgrade pip wheel setuptools
"$VENV/bin/pip" install -q -r requirements.txt -r requirements-build-mac.txt

# ===== 2. 테스트 =====
"$VENV/bin/python" -m unittest discover -s tests

# ===== 3. py2app 빌드 =====
rm -rf build dist
NEBULA_BUNDLE_ID="$BUNDLE_ID" "$VENV/bin/python" setup.py py2app > build_mas.log 2>&1 || { tail -40 build_mas.log; exit 1; }

# ===== 4. 불필요한 Qt 모듈 제거 =====
"$VENV/bin/python" mas/prune_bundle.py "$APP"
xattr -cr "$APP"

# ===== 5. 최소 macOS 버전 = 번들 내 바이너리 중 가장 높은 minos =====
MIN_MACOS=$("$VENV/bin/python" mas/min_macos.py "$APP" 12.0)
plutil -replace LSMinimumSystemVersion -string "$MIN_MACOS" "$APP/Contents/Info.plist"
echo "  LSMinimumSystemVersion = $MIN_MACOS"

# ===== 6. 서명 =====
ENTITLEMENTS="build/entitlements.plist"
if [ "$MODE" = "--local-test" ]; then
    # 로컬 테스트: 프로파일 없이 샌드박스만 적용 (App Store 식별자 엔타이틀먼트 제외)
    APP_SIGN_IDENTITY="-"
    "$VENV/bin/python" - "$ENTITLEMENTS" <<'PY'
import plistlib, sys
with open("mas/entitlements.plist", "rb") as f:
    entitlements = plistlib.load(f)
for key in ("com.apple.application-identifier", "com.apple.developer.team-identifier"):
    entitlements.pop(key, None)
with open(sys.argv[1], "wb") as f:
    plistlib.dump(entitlements, f)
PY
else
    [ -f "$PROFILE" ] || { echo "❌ $PROFILE 가 없습니다. python mas/asc.py ensure-profile $BUNDLE_ID $PROFILE"; exit 1; }
    cp "$PROFILE" "$APP/Contents/embedded.provisionprofile"
    sed -e "s/__TEAM_ID__/${TEAM_ID}/g" -e "s/__BUNDLE_ID__/${BUNDLE_ID}/g" mas/entitlements.plist > "$ENTITLEMENTS"
fi

sign() {
    codesign --force --sign "$APP_SIGN_IDENTITY" "$@"
}

# 안쪽부터: 개별 라이브러리 → 프레임워크 번들 → 보조 실행 파일 → 앱
while IFS= read -r -d '' binary; do
    if file -b "$binary" | grep -q "Mach-O"; then
        sign "$binary"
    fi
done < <(find "$APP/Contents" -type f \( -name "*.so" -o -name "*.dylib" \) -not -path "*/MacOS/*" -print0)

while IFS= read -r -d '' framework; do
    sign "$framework"
done < <(find "$APP/Contents" -type d -name "*.framework" -print0 | sort -rz)

for helper in "$APP/Contents/MacOS/"*; do
    [ "$(basename "$helper")" = "$APP_NAME" ] && continue
    sign --entitlements mas/entitlements-inherit.plist "$helper"
done

sign --entitlements "$ENTITLEMENTS" "$APP"
codesign --verify --deep --strict --verbose=2 "$APP"
echo "✅ 서명 완료: $APP"

if [ "$MODE" = "--local-test" ]; then
    echo "   실행: open \"$APP\"   (샌드박스 컨테이너: ~/Library/Containers/${BUNDLE_ID})"
    exit 0
fi

# ===== 7. 설치 패키지 =====
productbuild --component "$APP" /Applications --sign "$PKG_SIGN_IDENTITY" "$PKG"
echo "✅ 패키지 생성: $PKG"

# ===== 8. 검증 / 업로드 =====
if [ -n "${ASC_KEY_ID:-}" ] && [ -n "${ASC_ISSUER_ID:-}" ]; then
    xcrun altool --validate-app -f "$PKG" -t macos --apiKey "$ASC_KEY_ID" --apiIssuer "$ASC_ISSUER_ID"
    if [ "$MODE" = "--upload" ]; then
        xcrun altool --upload-app -f "$PKG" -t macos --apiKey "$ASC_KEY_ID" --apiIssuer "$ASC_ISSUER_ID"
        echo "✅ 업로드 완료. 다음 업로드 전에 app_version.py 의 BUILD_NUMBER 를 올리세요."
    fi
else
    echo "ℹ️  ASC_KEY_ID / ASC_ISSUER_ID 가 없어 검증/업로드를 건너뜁니다."
fi
