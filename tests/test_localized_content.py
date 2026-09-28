import unittest
from datetime import datetime

from i18n import SUPPORTED_LANGUAGES
from localized_content import (
    FEATURED_MERMAID_IDS, autocomplete_items, default_snippets, example_templates, mermaid_examples
)
from mermaid_utils import extract_mermaid_blocks


class MermaidExampleTests(unittest.TestCase):
    def test_same_ids_in_every_language(self):
        english_ids = [example_id for example_id, _, _ in mermaid_examples("en")]
        for lang in SUPPORTED_LANGUAGES:
            with self.subTest(lang=lang):
                self.assertEqual([example_id for example_id, _, _ in mermaid_examples(lang)], english_ids)

    def test_each_example_is_one_mermaid_block(self):
        for lang in SUPPORTED_LANGUAGES:
            for example_id, name, code in mermaid_examples(lang):
                with self.subTest(lang=lang, example=example_id):
                    self.assertTrue(name)
                    self.assertEqual(len(extract_mermaid_blocks(code)), 1)

    def test_names_are_unique_per_language(self):
        for lang in SUPPORTED_LANGUAGES:
            names = [name for _, name, _ in mermaid_examples(lang)]
            self.assertEqual(len(names), len(set(names)))

    def test_featured_ids_exist(self):
        ids = {example_id for example_id, _, _ in mermaid_examples("en")}
        self.assertTrue(set(FEATURED_MERMAID_IDS) <= ids)

    def test_unknown_language_uses_english(self):
        self.assertEqual(mermaid_examples("fr"), mermaid_examples("en"))


class TemplateTests(unittest.TestCase):
    def test_templates_localized_and_dated(self):
        now = datetime(2026, 3, 4)
        for lang in SUPPORTED_LANGUAGES:
            templates = example_templates(lang, now=now)
            with self.subTest(lang=lang):
                self.assertEqual([tid for tid, _, _ in templates], ["basic", "readme", "meeting", "api", "blog"])
                bodies = dict((tid, body) for tid, _, body in templates)
                self.assertIn("2026-03-04", bodies["blog"])
                self.assertIn("2026", bodies["meeting"])
                self.assertNotIn("{", bodies["basic"])

    def test_non_korean_templates_have_no_hangul(self):
        for lang in ("en", "ja", "zh"):
            for _, name, body in example_templates(lang):
                with self.subTest(lang=lang, name=name):
                    self.assertFalse(any("가" <= ch <= "힣" for ch in name + body))

    def test_snippets_and_autocomplete(self):
        for lang in SUPPORTED_LANGUAGES:
            self.assertIn("table2", default_snippets(lang))
            self.assertIn("# ", autocomplete_items(lang))


if __name__ == "__main__":
    unittest.main()
