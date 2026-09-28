import unittest

from markdown_tools import display_width, format_markdown_tables


class FormatTablesTests(unittest.TestCase):
    def test_aligns_columns(self):
        text = "|a|bb|\n|-|-|\n|ccc|d|"
        result, count = format_markdown_tables(text)
        self.assertEqual(count, 1)
        self.assertEqual(result, "| a   | bb  |\n| --- | --- |\n| ccc | d   |")

    def test_keeps_alignment_markers(self):
        text = "| L | C | R |\n|:--|:-:|--:|\n| 1 | 2 | 3 |"
        result, _ = format_markdown_tables(text)
        lines = result.split("\n")
        self.assertEqual(lines[1], "| :-- | :-: | --: |")
        self.assertEqual(lines[2], "| 1   |  2  |   3 |")

    def test_cjk_width(self):
        self.assertEqual(display_width("한글"), 4)
        result, _ = format_markdown_tables("|이름|x|\n|-|-|\n|a|b|")
        self.assertEqual(result.split("\n")[2], "| a    | b   |")

    def test_skips_code_fences_and_counts_multiple_tables(self):
        text = "```\n|a|b|\n|-|-|\n```\n\n|a|b|\n|-|-|\n\ntext\n\n|c|d|\n|-|-|\n|e|f|"
        result, count = format_markdown_tables(text)
        self.assertEqual(count, 2)
        self.assertTrue(result.startswith("```\n|a|b|\n|-|-|\n```"))

    def test_preserves_windows_newlines(self):
        result, count = format_markdown_tables("|a|b|\r\n|-|-|\r\n|c|d|\r\n")
        self.assertEqual(count, 1)
        self.assertIn("\r\n", result)
        self.assertNotIn("\n|", result.replace("\r\n", ""))

    def test_no_tables(self):
        self.assertEqual(format_markdown_tables(""), ("", 0))
        self.assertEqual(format_markdown_tables("a | b"), ("a | b", 0))

    def test_ragged_rows_are_padded(self):
        result, _ = format_markdown_tables("|a|b|c|\n|-|-|-|\n|1|")
        self.assertEqual(result.split("\n")[2], "| 1   |     |     |")


if __name__ == "__main__":
    unittest.main()
