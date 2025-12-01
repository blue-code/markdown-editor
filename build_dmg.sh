#!/bin/bash
#
# MarkdownPro DMG 빌드 스크립트
# macOS에서 실행하세요
#

set -e

APP_NAME="MarkdownPro"
VERSION="3.0.0"
DMG_NAME="${APP_NAME}-${VERSION}"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║        MarkdownPro v${VERSION} DMG 빌드 시작                  ║"
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
    
    # Python으로 간단한 아이콘 이미지 생성
    python3 << 'ICONGEN'
import os
try:
    from PIL import Image, ImageDraw, ImageFont
    
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    
    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 배경 (둥근 사각형)
        margin = size // 8
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=size // 5,
            fill='#007AFF'
        )
        
        # 텍스트
        try:
            font_size = size // 3
            font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', font_size)
        except:
            font = ImageFont.load_default()
        
        text = "MD"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size - text_width) // 2
        y = (size - text_height) // 2 - size // 10
        draw.text((x, y), text, fill='white', font=font)
        
        # 저장
        img.save(f'icon.iconset/icon_{size}x{size}.png')
        if size <= 512:
            img_2x = img.resize((size * 2, size * 2), Image.Resampling.LANCZOS)
            img_2x.save(f'icon.iconset/icon_{size}x{size}@2x.png')
    
    print("PNG 아이콘 생성 완료")
except ImportError:
    print("Pillow가 없어 기본 아이콘 사용")
    # 빈 iconset 생성
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
   MarkdownPro v3.0 설치 방법
===============================================

1. MarkdownPro.app을 Applications 폴더로 드래그하세요

2. 처음 실행 시 보안 경고가 나타나면:
   - 시스템 설정 > 개인 정보 보호 및 보안
   - "확인 없이 열기" 클릭
   
   또는 터미널에서:
   xattr -cr /Applications/MarkdownPro.app

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
    # 임시 DMG 생성
    hdiutil create -volname "$APP_NAME" \
                   -srcfolder "$DMG_DIR" \
                   -ov -format UDRW \
                   "dist/${DMG_NAME}_temp.dmg"
    
    # 마운트
    MOUNT_DIR=$(hdiutil attach "dist/${DMG_NAME}_temp.dmg" | grep Volumes | awk '{print $3}')
    
    # 배경 및 아이콘 위치 설정 (AppleScript)
    if [ -n "$MOUNT_DIR" ]; then
        osascript << APPLESCRIPT
tell application "Finder"
    tell disk "$APP_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set bounds of container window to {400, 100, 900, 450}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 80
        set position of item "${APP_NAME}.app" of container window to {130, 180}
        set position of item "Applications" of container window to {380, 180}
        set position of item "README.txt" of container window to {250, 320}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
APPLESCRIPT
        
        # 동기화 및 언마운트
        sync
        hdiutil detach "$MOUNT_DIR"
    fi
    
    # 최종 압축 DMG
    hdiutil convert "dist/${DMG_NAME}_temp.dmg" \
                    -format UDZO \
                    -imagekey zlib-level=9 \
                    -o "dist/${DMG_NAME}.dmg"
    
    rm -f "dist/${DMG_NAME}_temp.dmg"
    
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
