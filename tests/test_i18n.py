import string
import unittest

import i18n
from i18n import STRINGS, SUPPORTED_LANGUAGES, detect_system_language, normalize_language, set_language, tr


def placeholders(text):
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


class TranslationTableTests(unittest.TestCase):
    def tearDown(self):
        set_language("en")

    def test_every_language_has_every_key(self):
        english_keys = set(STRINGS["en"])
        for lang in SUPPORTED_LANGUAGES:
            with self.subTest(lang=lang):
                self.assertEqual(set(STRINGS[lang]) ^ english_keys, set())

    def test_placeholders_match_english(self):
        for key, english in STRINGS["en"].items():
            for lang in SUPPORTED_LANGUAGES:
                with self.subTest(lang=lang, key=key):
                    self.assertEqual(placeholders(STRINGS[lang][key]), placeholders(english))

    def test_no_empty_translations(self):
        for lang in SUPPORTED_LANGUAGES:
            for key, text in STRINGS[lang].items():
                with self.subTest(lang=lang, key=key):
                    self.assertTrue(text.strip())

    def test_tr_formats_and_falls_back(self):
        set_language("ja")
        self.assertEqual(tr("status.words", count=3), "単語: 3")
        self.assertEqual(tr("does.not.exist"), "does.not.exist")

    def test_unknown_language_falls_back_to_english(self):
        self.assertEqual(set_language("fr"), "en")
        self.assertEqual(i18n.current_language(), "en")


class LanguageDetectionTests(unittest.TestCase):
    def test_normalize_variants(self):
        self.assertEqual(normalize_language("ko_KR"), "ko")
        self.assertEqual(normalize_language("ja-JP"), "ja")
        self.assertEqual(normalize_language("zh-Hans-CN"), "zh")
        self.assertEqual(normalize_language("zh_CN"), "zh")
        self.assertIsNone(normalize_language("zh-Hant-TW"))
        self.assertIsNone(normalize_language("fr-FR"))
        self.assertIsNone(normalize_language(""))

    def test_detect_uses_first_supported_preference(self):
        self.assertEqual(detect_system_language(["fr-FR", "ja-JP", "en-US"]), "ja")
        self.assertEqual(detect_system_language(["zh-Hant-TW", "ko-KR"]), "ko")

    def test_detect_defaults_to_english(self):
        self.assertEqual(detect_system_language(["fr-FR", "de-DE"]), "en")


if __name__ == "__main__":
    unittest.main()
