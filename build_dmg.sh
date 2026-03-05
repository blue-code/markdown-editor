#!/bin/bash
#
# MarkdownPro DMG 빌드 스크립트
# macOS에서 실행하세요
#

set -e

APP_NAME="Nebula Note"
VERSION="3.0.0"
DMG_NAME="${APP_NAME}-${VERSION}"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        Nebula Note v${VERSION} DMG 빌드 시작                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")"

# ===== 1. 이전 빌드 정리 =====
echo "🧹 이전 빌드 정리 중..."
rm -rf build dist *.dmg

# ===== 2. 가상환경 설정 =====
echo "🐍 Python 가상환경 설정 중..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# ===== 3. 의존성 설치 =====
echo "📦 의존성 설치 중..."
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
pip install py2app

# ===== 4. 아이콘 생성 =====
if [ ! -f "icon.icns" ]; then
    echo "🎨 아이콘 생성 중..."
    
    # iconset 디렉토리 생성
    mkdir -p icon.iconset
    
    # Python으로 아이콘 이미지 생성 (splash.png 사용)
    python3 << 'ICONGEN'
import os
try:
    from PIL import Image
    
    # 소스 이미지 (splash.png가 있으면 사용, 없으면 생성)
    source_img = "splash.png"
    if not os.path.exists(source_img):
        print(f"Warning: {source_img} not found. Generating default icon.")
        from PIL import ImageDraw, ImageFont
        img = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([100, 100, 924, 924], radius=200, fill='#007AFF')
        # 텍스트
        try:
            font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 400)
        except:
            font = ImageFont.load_default()
        text = "N"
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((1024-w)/2, (1024-h)/2 - 100), text, fill='white', font=font)
        img.save(source_img)
    
    # 아이콘 리사이징
    img = Image.open(source_img)
    
    # 정사각형으로 크롭 (중앙 기준)
    w, h = img.size
    size = min(w, h)
    left = (w - size) / 2
    top = (h - size) / 2
    right = (w + size) / 2
    bottom = (h + size) / 2
    img = img.crop((left, top, right, bottom))
    
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(f'icon.iconset/icon_{size}x{size}.png')
        
        if size <= 512:
            resized_2x = img.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
            resized_2x.save(f'icon.iconset/icon_{size}x{size}@2x.png')
    
    print("PNG 아이콘 생성 완료")
except Exception as e:
    print(f"Error creating icons: {e}")
    # 빈 iconset 생성 (에러 방지)
    for size in [16, 32, 128, 256, 512]:
        open(f'icon.iconset/icon_{size}x{size}.png', 'w').close()
ICONGEN
    
    # iconutil로 icns 변환
    if command -v iconutil &> /dev/null; then
        iconutil -c icns icon.iconset -o icon.icns 2>/dev/null || touch icon.icns
    else
        touch icon.icns
    fi
    rm -rf icon.iconset
fi

# ===== 5. 앱 빌드 =====
echo "🔨 앱 빌드 중..."
python setup.py py2app


# ===== 5-1. libffi 런타임 보강 (py2app Launch error 방지) =====
echo "🧩 libffi 런타임 확인/복사 중..."
APP_FRAMEWORKS="dist/${APP_NAME}.app/Contents/Frameworks"
mkdir -p "$APP_FRAMEWORKS"

LIBFFI_SRC=""
# 1) brew 기본 경로
if [ -f "/opt/homebrew/opt/libffi/lib/libffi.8.dylib" ]; then
    LIBFFI_SRC="/opt/homebrew/opt/libffi/lib/libffi.8.dylib"
elif [ -f "/usr/local/opt/libffi/lib/libffi.8.dylib" ]; then
    LIBFFI_SRC="/usr/local/opt/libffi/lib/libffi.8.dylib"
fi

# 2) 현재 빌드 파이썬(base_prefix) 기반 탐색 (conda/venv 대응)
if [ -z "$LIBFFI_SRC" ]; then
    LIBFFI_SRC=$(python - <<'PYF'
import sys,glob,os
candidates=[]
for root in [sys.base_prefix, sys.prefix]:
    if root and os.path.exists(root):
        candidates += glob.glob(os.path.join(root, '**', 'libffi.8.dylib'), recursive=True)
print(candidates[0] if candidates else '')
PYF
)
fi

# 3) 최후 fallback
if [ -z "$LIBFFI_SRC" ]; then
    LIBFFI_SRC=$(find /opt/homebrew /usr/local /Users/$(whoami) -name "libffi.8.dylib" 2>/dev/null | head -n 1 || true)
fi


if [ -n "$LIBFFI_SRC" ] && [ -f "$LIBFFI_SRC" ]; then
    cp -f "$LIBFFI_SRC" "$APP_FRAMEWORKS/libffi.8.dylib"
    # py2app의 _ctypes 상대 경로 대응용 복사
    PY_LIB_DIR=$(find "dist/${APP_NAME}.app/Contents/Resources/lib" -maxdepth 2 -type d -name "python*" 2>/dev/null | head -n 1 || true)
    if [ -n "$PY_LIB_DIR" ]; then
        cp -f "$LIBFFI_SRC" "$PY_LIB_DIR/libffi.8.dylib" || true
    fi
    echo "✅ libffi 복사 완료: $LIBFFI_SRC"
else
    echo "⚠️  libffi.8.dylib를 찾지 못했습니다. 앱 실행 시 Launch error가 날 수 있습니다."
fi

# 빌드 확인
if [ ! -d "dist/${APP_NAME}.app" ]; then
    echo "❌ 앱 빌드 실패!"
    exit 1
fi

echo "✅ 앱 빌드 완료: dist/${APP_NAME}.app"

# ===== 6. DMG 생성 =====
echo "💿 DMG 생성 중..."

DMG_DIR="dist/dmg_temp"
mkdir -p "$DMG_DIR"

# 앱 복사
cp -R "dist/${APP_NAME}.app" "$DMG_DIR/"

# Applications 심볼릭 링크
ln -sf /Applications "$DMG_DIR/Applications"

# README 생성
cat > "$DMG_DIR/README.txt" << 'README'
===============================================
   Nebula Note v3.0 설치 방법
===============================================

1. Nebula Note.app을 Applications 폴더로 드래그하세요

2. 처음 실행 시 보안 경고가 나타나면:
   - 시스템 설정 > 개인 정보 보호 및 보안
   - "확인 없이 열기" 클릭
   
   또는 터미널에서:
   xattr -cr /Applications/Nebula Note.app

===============================================
   주요 기능
===============================================

✅ 실시간 마크다운 미리보기
✅ Mermaid 다이어그램 19종 지원
✅ 포커스 모드 (방해 없는 글쓰기)
✅ 문서 개요 & 통계
✅ 스니펫 관리
✅ 다크 모드
✅ SVG/PNG 다이어그램 내보내기

===============================================
   단축키
===============================================

Ctrl+N     새 문서
Ctrl+O     열기
Ctrl+S     저장
Ctrl+M     Mermaid 뷰어
F11        포커스 모드
Ctrl+B/I   굵게/기울임
Tab        스니펫 확장

===============================================
README

# DMG 생성
if command -v hdiutil &> /dev/null; then
    # 안정 모드: 마운트/AppleScript 단계 없이 바로 압축 DMG 생성
    hdiutil create -volname "$APP_NAME"                    -srcfolder "$DMG_DIR"                    -ov -format UDZO                    -imagekey zlib-level=9                    "dist/${DMG_NAME}.dmg"

    echo "✅ DMG 생성 완료: dist/${DMG_NAME}.dmg"
else
    # hdiutil 없으면 ZIP으로 대체
    echo "⚠️  hdiutil 없음, ZIP으로 패키징..."
    cd dist
    zip -r "${DMG_NAME}.zip" "${APP_NAME}.app" ../README.txt
    cd ..
    echo "✅ ZIP 생성 완료: dist/${DMG_NAME}.zip"
fi

# 정리
rm -rf "$DMG_DIR"

# ===== 완료 =====
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    빌드 완료! 🎉                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📁 생성된 파일:"
ls -lh dist/*.dmg 2>/dev/null || ls -lh dist/*.zip 2>/dev/null
echo ""
echo "📌 다음 단계:"
echo "   1. DMG 파일을 테스트"
echo "   2. 코드 서명 (배포용): codesign --deep --force --sign \"Developer ID\" dist/${APP_NAME}.app"
echo "   3. 공증 (배포용): xcrun notarytool submit dist/${DMG_NAME}.dmg"
echo ""

deactivate 2>/dev/null || true
