"""Microsoft Store 제출용 MSIX 스테이징 도구.

PyInstaller 산출물(dist\\Nebula Note)을 MSIX 레이아웃으로 복사하고
AppxManifest.xml 과 타일 로고를 생성한다. 실제 .msix 압축은 build_msix.ps1 이
Windows SDK 의 makeappx 로 수행한다 (SDK 의존 부분을 파이썬 밖으로 분리해 테스트 가능하게 유지).

사용:
    python store_packaging.py stage --dist "dist/Nebula Note" --out build/msix
"""

import argparse
import json
import os
import shutil
import sys
from dataclasses import dataclass, fields
from string import Template
from xml.sax.saxutils import escape

from app_version import APP_NAME, APP_VERSION

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(HERE, "msix", "AppxManifest.template.xml")
# 계정 식별값이라 git 에서 제외 — example 파일을 복사해 로컬에서만 채운다
IDENTITY_PATH = os.path.join(HERE, "msix", "store_identity.json")
EXE_NAME = f"{APP_NAME}.exe"
PLACEHOLDER_MARK = "REPLACE"


@dataclass(frozen=True)
class LogoSpec:
    filename: str
    width: int
    height: int


# 매니페스트가 참조하는 로고만 생성한다. makepri 없이 패키징하므로 scale-/targetsize- 한정자는 쓰지 않는다.
LOGO_SPECS = (
    LogoSpec("StoreLogo.png", 50, 50),
    LogoSpec("Square44x44Logo.png", 44, 44),
    LogoSpec("Square150x150Logo.png", 150, 150),
    LogoSpec("Wide310x150Logo.png", 310, 150),
)


@dataclass(frozen=True)
class StoreIdentity:
    """Partner Center > 제품 ID 화면의 값. 스토어 서명과 일치해야 해서 임의 값이면 제출이 거절된다."""

    identity_name: str
    publisher: str
    publisher_display_name: str
    display_name: str
    description: str

    @classmethod
    def from_json_file(cls, path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(**{field.name: data[field.name] for field in fields(cls)})

    def validate(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if not value or PLACEHOLDER_MARK in value:
                raise ValueError(f"store_identity.json 의 '{field.name}' 값을 Partner Center 값으로 채워야 합니다.")
        if not self.publisher.startswith("CN="):
            raise ValueError("publisher 는 'CN=' 으로 시작해야 합니다 (Partner Center 의 Package/Identity/Publisher).")


def to_msix_version(semver):
    """'1.2.0' → '1.2.0.0'. 스토어는 네 번째 자리를 예약하므로 항상 0 이어야 한다."""
    parts = semver.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError(f"major.minor.patch 형식이어야 합니다: {semver!r}")
    if any(int(p) > 65535 for p in parts):
        raise ValueError(f"각 자리는 0~65535 범위여야 합니다: {semver!r}")
    return ".".join(parts + ["0"])


def render_manifest(identity, version, template_path=TEMPLATE_PATH):
    with open(template_path, encoding="utf-8") as f:
        template = Template(f.read())
    attr = lambda value: escape(value, {'"': "&quot;"})
    return template.substitute(
        identity_name=attr(identity.identity_name),
        publisher=attr(identity.publisher),
        publisher_display_name=attr(identity.publisher_display_name),
        display_name=attr(identity.display_name),
        description=attr(identity.description),
        version=to_msix_version(version),
        executable=attr(EXE_NAME),
    )


def generate_logos(source_png, out_dir):
    from PIL import Image

    os.makedirs(out_dir, exist_ok=True)
    with Image.open(source_png) as src:
        src = src.convert("RGBA")
        for spec in LOGO_SPECS:
            # 와이드 타일은 정사각 아이콘을 투명 여백 가운데에 놓는다 (늘리면 아이콘이 찌그러짐)
            side = min(spec.width, spec.height)
            icon = src.resize((side, side), Image.LANCZOS)
            canvas = Image.new("RGBA", (spec.width, spec.height), (0, 0, 0, 0))
            canvas.paste(icon, ((spec.width - side) // 2, (spec.height - side) // 2), icon)
            canvas.save(os.path.join(out_dir, spec.filename))


def stage_package(dist_dir, stage_dir, identity, version, icon_png):
    if not os.path.isfile(os.path.join(dist_dir, EXE_NAME)):
        raise FileNotFoundError(f"{EXE_NAME} 이 없습니다. build_exe.bat 을 먼저 실행하세요: {dist_dir}")
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    # exe 를 패키지 루트에 둔다 — Executable 경로를 단순하게 유지하려는 선택
    shutil.copytree(dist_dir, stage_dir)
    generate_logos(icon_png, os.path.join(stage_dir, "Assets"))
    with open(os.path.join(stage_dir, "AppxManifest.xml"), "w", encoding="utf-8") as f:
        f.write(render_manifest(identity, version))


def main(argv=None):
    parser = argparse.ArgumentParser(description="MSIX 스테이징")
    sub = parser.add_subparsers(dest="command", required=True)
    stage = sub.add_parser("stage")
    stage.add_argument("--dist", default=os.path.join(HERE, "dist", APP_NAME))
    stage.add_argument("--out", default=os.path.join(HERE, "build", "msix"))
    stage.add_argument("--identity", default=IDENTITY_PATH)
    stage.add_argument("--icon", default=os.path.join(HERE, "icon_source.png"))
    sub.add_parser("version")
    args = parser.parse_args(argv)

    if args.command == "version":
        print(APP_VERSION)
        return 0

    if not os.path.isfile(args.identity):
        print(f"[msix] {args.identity} 가 없습니다. msix/store_identity.example.json 을 복사해 Partner Center 값을 채우세요.", file=sys.stderr)
        return 2
    identity = StoreIdentity.from_json_file(args.identity)
    try:
        identity.validate()
    except ValueError as exc:
        print(f"[msix] {exc}", file=sys.stderr)
        return 2
    stage_package(args.dist, args.out, identity, APP_VERSION, args.icon)
    print(f"[msix] 스테이징 완료: {args.out} (v{to_msix_version(APP_VERSION)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
