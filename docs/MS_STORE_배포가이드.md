# Microsoft Store 배포 가이드

Nebula Note 를 MSIX 패키지로 만들어 Microsoft Store 에 제출하는 절차.

## 1. 방식 선택: MSIX

| 항목 | MSIX (채택) | EXE/NSIS 설치파일 |
|---|---|---|
| 코드 서명 | 스토어가 대신 서명 | 유료 OV/EV 인증서 필요 |
| 설치/제거 | 깔끔한 격리 설치, 자동 업데이트 | 설치파일 직접 호스팅 필요 |
| 파일 연결(.md) | 매니페스트로 선언 | 레지스트리 직접 작성 |

## 2. 사전 준비 (최초 1회)

1. **Windows SDK 설치** — `makeappx.exe`, `signtool.exe` 제공
   ```powershell
   winget install Microsoft.WindowsSDK.10.0.26100
   ```
2. **Partner Center 에서 앱 이름 예약** — `apps & games > New product > MSIX or PWA app` → `Nebula Note`
3. **제품 ID 값 복사** — `msix/store_identity.example.json` 을 `msix/store_identity.json` 으로 복사한 뒤, `Product management > Product identity` 화면의 값을 입력 (이 파일은 `.gitignore` 대상)

   | store_identity.json | Partner Center 항목 |
   |---|---|
   | `identity_name` | Package/Identity/Name |
   | `publisher` | Package/Identity/Publisher (`CN=...`) |
   | `publisher_display_name` | Package/Properties/PublisherDisplayName |

   `display_name` 은 예약한 Store 이름과 정확히 같아야 한다. 값이 비어 있거나 `REPLACE` 가 남아 있으면 빌드가 중단된다.

## 3. 빌드

```powershell
powershell -ExecutionPolicy Bypass -File build_msix.ps1            # 제출용
powershell -ExecutionPolicy Bypass -File build_msix.ps1 -SkipExe   # 기존 dist 재사용
```

산출물: `dist\NebulaNote-<버전>-x64.msix`

## 4. 로컬 설치 테스트 (선택)

```powershell
powershell -ExecutionPolicy Bypass -File build_msix.ps1 -SkipExe -TestSign
```

스크립트가 안내하는 명령으로 테스트 인증서를 `TrustedPeople` 에 등록한 뒤 `.msix` 를 더블클릭해 설치한다.
확인 항목: 실행, 머메이드/수식 렌더링, `.md` 더블클릭 열기, 설정 저장, 마지막 파일 복원.

## 5. 제출

1. Partner Center → 제출 생성 → **Packages** 에 `.msix` 업로드
2. **runFullTrust 사유** 입력 (예: "PyQt6 기반 Win32 데스크톱 앱으로, 로컬 마크다운 파일 편집과 Chromium 기반 미리보기를 위해 필요")
3. 스토어 등록 정보: 설명, 스크린샷(최소 1장, 1366×768 이상 권장), 개인정보 처리방침 URL
4. 연령 등급 설문 → 가격/지역 → 제출

## 6. 버전 관리

- 버전 단일 출처: `app_version.py` 의 `APP_VERSION` (major.minor.patch)
- MSIX 버전은 자동으로 `major.minor.patch.0` 으로 변환 (네 번째 자리는 스토어 예약)
- 스토어 업데이트는 **이전 제출보다 높은 버전**이어야 한다
