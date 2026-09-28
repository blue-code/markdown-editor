# Nebula Note — Microsoft Store 제출용 MSIX 빌드
#
# 흐름: build_exe.bat(PyInstaller + prune) → store_packaging.py stage → makeappx pack
#
# 사용:
#   powershell -ExecutionPolicy Bypass -File build_msix.ps1              # 스토어 제출용 (서명 없음, 스토어가 서명)
#   powershell -ExecutionPolicy Bypass -File build_msix.ps1 -SkipExe     # 기존 dist 재사용
#   powershell -ExecutionPolicy Bypass -File build_msix.ps1 -TestSign    # 로컬 설치 테스트용 자체 서명
#
# 전제: Windows SDK (makeappx.exe / signtool.exe)
#   winget install Microsoft.WindowsSDK.10.0.26100

param(
    [switch]$SkipExe,
    [switch]$TestSign
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

function Find-SdkTool($name) {
    $kits = "${env:ProgramFiles(x86)}\Windows Kits\10\bin"
    $tool = Get-ChildItem $kits -Recurse -Filter $name -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match '\\x64\\' } |
        Sort-Object { [version]($_.Directory.Parent.Name -replace '[^\d.]', '') } -Descending |
        Select-Object -First 1
    if (-not $tool) {
        throw "$name 을 찾을 수 없습니다. 'winget install Microsoft.WindowsSDK.10.0.26100' 로 Windows SDK 를 설치하세요."
    }
    return $tool.FullName
}

# SDK 확인을 맨 앞에서 — 수 분짜리 exe 빌드 후에 실패하지 않도록
$makeappx = Find-SdkTool "makeappx.exe"

if (-not $SkipExe) {
    $env:SKIP_INSTALLER = "1"; $env:NO_PAUSE = "1"
    & (Join-Path $PSScriptRoot "build_exe.bat")
    if ($LASTEXITCODE -ne 0) { throw "build_exe.bat 실패" }
}

$version = (& $python (Join-Path $PSScriptRoot "store_packaging.py") version).Trim()
$stage = Join-Path $PSScriptRoot "build\msix"
& $python (Join-Path $PSScriptRoot "store_packaging.py") stage --out $stage
if ($LASTEXITCODE -ne 0) { throw "MSIX 스테이징 실패 (msix\store_identity.json 확인)" }

$output = Join-Path $PSScriptRoot "dist\NebulaNote-$version-x64.msix"
if (Test-Path $output) { Remove-Item $output -Force }
& $makeappx pack /d $stage /p $output /o
if ($LASTEXITCODE -ne 0) { throw "makeappx pack 실패" }

if ($TestSign) {
    # 매니페스트 Publisher 와 인증서 Subject 가 같아야 서명이 유효하다
    [xml]$manifest = Get-Content (Join-Path $stage "AppxManifest.xml") -Encoding UTF8
    $publisher = $manifest.Package.Identity.Publisher
    $cert = Get-ChildItem Cert:\CurrentUser\My | Where-Object { $_.Subject -eq $publisher } | Select-Object -First 1
    if (-not $cert) {
        $cert = New-SelfSignedCertificate -Type Custom -Subject $publisher -KeyUsage DigitalSignature `
            -FriendlyName "Nebula Note MSIX Test" -CertStoreLocation Cert:\CurrentUser\My `
            -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")
        Write-Host "[msix] 테스트 인증서 생성: $($cert.Thumbprint)"
        Write-Host "       설치 전 '신뢰할 수 있는 사용자(TrustedPeople)' 저장소에 등록 필요 (관리자 PowerShell):"
        Write-Host "       Export-Certificate -Cert Cert:\CurrentUser\My\$($cert.Thumbprint) -FilePath nebula_test.cer; Import-Certificate -FilePath nebula_test.cer -CertStoreLocation Cert:\LocalMachine\TrustedPeople"
    }
    $signtool = Find-SdkTool "signtool.exe"
    & $signtool sign /fd SHA256 /sha1 $cert.Thumbprint $output
    if ($LASTEXITCODE -ne 0) { throw "signtool 서명 실패" }
}

Write-Host ""
Write-Host "======================================================"
Write-Host "[*] MSIX Build Success: $output"
if (-not $TestSign) { Write-Host "    Partner Center > 패키지 에 그대로 업로드 (서명은 스토어가 수행)" }
Write-Host "======================================================"
