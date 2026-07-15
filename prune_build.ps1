# Nebula Note 빌드 경량화 스크립트
#
# 배경: PyInstaller + PyQt6-WebEngine 는 Chromium 엔진을 통째로 번들한다.
#       엔진 본체(약 200M)는 머메이드/MathJax 렌더링에 필수라 줄일 수 없지만,
#       아래 항목들은 프로덕션 실행에 불필요하므로 안전하게 제거해 배포 용량을 줄인다.
#
# 제거 대상 (무손실):
#   1) resources\*.debug.*        - DevTools 디버그 리소스. non-debug 파일이 별도로 존재.
#   2) qtwebengine_locales        - 브라우저 UI 로케일. en-US(폴백) + ko 만 유지.
#   3) *.qm                       - Qt 프레임워크 번역. 한국어만 유지(없으면 영어 원문 폴백).
#   4) qml\                       - QtQuick/QML 리소스. 위젯 기반 WebEngineWidgets 는 미사용.
#
# 사용: powershell -ExecutionPolicy Bypass -File prune_build.ps1
#       (build_exe.bat 이 exe 빌드 성공 직후, NSIS 패키징 전에 호출한다)

param(
    [string]$DistRoot = "$PSScriptRoot\dist\Nebula Note"
)

$ErrorActionPreference = "Stop"
$qt6 = Join-Path $DistRoot "_internal\PyQt6\Qt6"

if (-not (Test-Path $qt6)) {
    Write-Host "[prune] 대상 없음(스킵): $qt6"
    exit 0
}

function Get-DirKB($path) {
    if (-not (Test-Path $path)) { return 0 }
    return [int]((Get-ChildItem $path -Recurse -File | Measure-Object Length -Sum).Sum / 1KB)
}

$before = Get-DirKB $DistRoot
Write-Host "[prune] 시작 - 현재 크기: $([int]($before/1024)) MB"

# 1) 디버그 리소스 (*.debug.pak / *.debug.bin)
$dbg = Get-ChildItem "$qt6\resources" -File -Filter "*.debug.*" -ErrorAction SilentlyContinue
if ($dbg) {
    $kb = [int](($dbg | Measure-Object Length -Sum).Sum / 1KB)
    $dbg | Remove-Item -Force
    Write-Host "[prune] 1) 디버그 리소스 삭제: $($dbg.Count)개, $kb KB"
}

# 2) WebEngine 로케일 - en-US, ko 외 삭제
$locDir = "$qt6\translations\qtwebengine_locales"
if (Test-Path $locDir) {
    $keep = @("en-US.pak", "ko.pak")
    $drop = Get-ChildItem $locDir -File | Where-Object { $keep -notcontains $_.Name }
    $kb = [int](($drop | Measure-Object Length -Sum).Sum / 1KB)
    $drop | Remove-Item -Force
    Write-Host "[prune] 2) 로케일 정리(en-US,ko 유지): $($drop.Count)개, $kb KB"
}

# 3) Qt 프레임워크 번역(*.qm) - 한국어(*_ko.qm)만 유지
$transDir = "$qt6\translations"
if (Test-Path $transDir) {
    $qm = Get-ChildItem $transDir -File -Filter "*.qm" | Where-Object { $_.Name -notmatch "_ko\.qm$" }
    $kb = [int](($qm | Measure-Object Length -Sum).Sum / 1KB)
    $qm | Remove-Item -Force
    Write-Host "[prune] 3) 번역(.qm) 정리(ko 유지): $($qm.Count)개, $kb KB"
}

# 4) QML 리소스 폴더
$qmlDir = "$qt6\qml"
if (Test-Path $qmlDir) {
    $kb = Get-DirKB $qmlDir
    Remove-Item $qmlDir -Recurse -Force
    Write-Host "[prune] 4) qml 폴더 삭제: $kb KB"
}

$after = Get-DirKB $DistRoot
Write-Host "[prune] 완료 - $([int]($before/1024)) MB -> $([int]($after/1024)) MB (절감 $([int](($before-$after)/1024)) MB)"
