import os
import tempfile
import unittest

import file_io
from file_io import FileAccessError


class FileIoTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.folder.name, "문서 note.md")

    def tearDown(self):
        self.folder.cleanup()

    def test_round_trip_unicode(self):
        file_io.write_text(self.path, "# 제목\n日本語 中文\r\n")
        self.assertEqual(file_io.read_text(self.path), "# 제목\n日本語 中文\r\n")

    def test_overwrite_truncates(self):
        file_io.write_text(self.path, "long content here")
        file_io.write_text(self.path, "short")
        self.assertEqual(file_io.read_text(self.path), "short")

    def test_bom_is_dropped(self):
        with open(self.path, "wb") as f:
            f.write("﻿hello".encode("utf-8"))
        self.assertEqual(file_io.read_text(self.path), "hello")

    def test_missing_file(self):
        missing = os.path.join(self.folder.name, "missing.md")
        self.assertFalse(file_io.exists(missing))
        self.assertIsNone(file_io.file_state(missing))
        with self.assertRaises(FileAccessError) as ctx:
            file_io.read_text(missing)
        self.assertFalse(ctx.exception.permission_denied)

    def test_file_state_changes_with_content(self):
        file_io.write_text(self.path, "a")
        first = file_io.file_state(self.path)
        file_io.write_text(self.path, "abc")
        self.assertNotEqual(file_io.file_state(self.path), first)
        self.assertTrue(file_io.is_file(self.path))

    def test_non_utf8_raises_decode_error(self):
        with open(self.path, "wb") as f:
            f.write(b"\xff\xfe\x00bad")
        with self.assertRaises(UnicodeDecodeError):
            file_io.read_text(self.path)


if __name__ == "__main__":
    unittest.main()
