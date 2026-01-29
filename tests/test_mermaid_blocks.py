import unittest

from mermaid_utils import extract_mermaid_blocks


class MermaidBlockExtractTests(unittest.TestCase):
    def test_extract_multiple_blocks(self):
        text = (
            "```mermaid\n"
            "flowchart TD\n"
            "A-->B\n"
            "```\n"
            "\n"
            "text\n"
            "```mermaid\n"
            "sequenceDiagram\n"
            "A->>B: Hi\n"
            "```\n"
        )
        blocks = extract_mermaid_blocks(text)
        self.assertEqual(blocks, ["flowchart TD\nA-->B", "sequenceDiagram\nA->>B: Hi"])

    def test_extract_windows_newlines(self):
        text = "```mermaid\r\nflowchart TD\r\nA-->B\r\n```\r\n"
        blocks = extract_mermaid_blocks(text)
        self.assertEqual(blocks, ["flowchart TD\r\nA-->B"])

    def test_extract_no_blocks(self):
        text = "```python\nprint('hi')\n```\n"
        blocks = extract_mermaid_blocks(text)
        self.assertEqual(blocks, [])


if __name__ == "__main__":
    unittest.main()
