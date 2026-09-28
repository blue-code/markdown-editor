import os
import tempfile
import unittest
import xml.etree.ElementTree as ET

from PIL import Image

from app_version import APP_VERSION
from store_packaging import (
    LOGO_SPECS,
    StoreIdentity,
    generate_logos,
    render_manifest,
    stage_package,
    to_msix_version,
)

FOUNDATION_NS = "{http://schemas.microsoft.com/appx/manifest/foundation/windows10}"
UAP_NS = "{http://schemas.microsoft.com/appx/manifest/uap/windows10}"


def sample_identity(**overrides):
    values = dict(
        identity_name="12345Kent.NebulaNote",
        publisher="CN=A1B2C3D4-0000-1111-2222-333344445555",
        publisher_display_name="Kent & Co",
        display_name="Nebula Note",
        description="마크다운 에디터",
    )
    values.update(overrides)
    return StoreIdentity(**values)


class MsixVersionTests(unittest.TestCase):
    def test_semver_gets_zero_revision(self):
        self.assertEqual(to_msix_version("1.2.0"), "1.2.0.0")

    def test_app_version_is_convertible(self):
        self.assertTrue(to_msix_version(APP_VERSION).endswith(".0"))

    def test_rejects_non_numeric_version(self):
        with self.assertRaises(ValueError):
            to_msix_version("1.2.0-beta")

    def test_rejects_wrong_part_count(self):
        with self.assertRaises(ValueError):
            to_msix_version("1.2")

    def test_rejects_part_over_uint16(self):
        with self.assertRaises(ValueError):
            to_msix_version("1.65536.0")


class StoreIdentityTests(unittest.TestCase):
    def test_placeholder_values_are_rejected(self):
        identity = sample_identity(identity_name="REPLACE_WITH_PARTNER_CENTER_VALUE")
        with self.assertRaises(ValueError):
            identity.validate()

    def test_publisher_must_start_with_cn(self):
        with self.assertRaises(ValueError):
            sample_identity(publisher="A1B2C3D4").validate()

    def test_from_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "identity.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(
                    '{"identity_name": "1.Kent", "publisher": "CN=X", '
                    '"publisher_display_name": "Kent", "display_name": "N", '
                    '"description": "d"}'
                )
            identity = StoreIdentity.from_json_file(path)
        self.assertEqual(identity.identity_name, "1.Kent")


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.xml = render_manifest(sample_identity(), "1.2.0")
        self.root = ET.fromstring(self.xml)

    def test_identity_fields(self):
        node = self.root.find(f"{FOUNDATION_NS}Identity")
        self.assertEqual(node.get("Name"), "12345Kent.NebulaNote")
        self.assertEqual(node.get("Publisher"), "CN=A1B2C3D4-0000-1111-2222-333344445555")
        self.assertEqual(node.get("Version"), "1.2.0.0")

    def test_special_characters_are_escaped(self):
        name = self.root.find(f"{FOUNDATION_NS}Properties/{FOUNDATION_NS}PublisherDisplayName")
        self.assertEqual(name.text, "Kent & Co")

    def test_markdown_file_association(self):
        types = [t.text for t in self.root.iter(f"{UAP_NS}FileType")]
        self.assertEqual(types, [".md", ".markdown"])

    def test_every_referenced_logo_is_generated(self):
        generated = {f"Assets\\{spec.filename}" for spec in LOGO_SPECS}
        for attr in ("Square150x150Logo", "Square44x44Logo", "Wide310x150Logo"):
            node = next(n for n in self.root.iter() if n.get(attr))
            self.assertIn(node.get(attr), generated)


class LogoAndStageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = os.path.join(self.tmp.name, "icon.png")
        Image.new("RGBA", (256, 256), (255, 0, 0, 255)).save(self.src)

    def tearDown(self):
        self.tmp.cleanup()

    def test_logos_have_exact_sizes(self):
        out = os.path.join(self.tmp.name, "Assets")
        generate_logos(self.src, out)
        for spec in LOGO_SPECS:
            with Image.open(os.path.join(out, spec.filename)) as img:
                self.assertEqual(img.size, (spec.width, spec.height))

    def test_stage_package_layout(self):
        dist = os.path.join(self.tmp.name, "dist")
        os.makedirs(os.path.join(dist, "_internal"))
        with open(os.path.join(dist, "Nebula Note.exe"), "wb") as f:
            f.write(b"MZ")
        stage = os.path.join(self.tmp.name, "stage")

        stage_package(dist, stage, sample_identity(), "1.2.0", self.src)

        self.assertTrue(os.path.isfile(os.path.join(stage, "Nebula Note.exe")))
        self.assertTrue(os.path.isdir(os.path.join(stage, "_internal")))
        self.assertTrue(os.path.isfile(os.path.join(stage, "AppxManifest.xml")))
        self.assertTrue(os.path.isfile(os.path.join(stage, "Assets", "StoreLogo.png")))

    def test_stage_requires_executable(self):
        dist = os.path.join(self.tmp.name, "empty_dist")
        os.makedirs(dist)
        with self.assertRaises(FileNotFoundError):
            stage_package(dist, os.path.join(self.tmp.name, "s"), sample_identity(), "1.2.0", self.src)


if __name__ == "__main__":
    unittest.main()
