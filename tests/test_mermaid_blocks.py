import unittest

from mermaid_utils import extract_mermaid_blocks, mermaid_block_at


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


class MermaidBlockAtTests(unittest.TestCase):
    TEXT = "intro\n```mermaid\nflowchart TD\nA-->B\n```\nmiddle\n```mermaid\npie\n```\n"

    def test_position_inside_second_block(self):
        position = self.TEXT.index("pie")
        self.assertEqual(mermaid_block_at(self.TEXT, position), (1, "pie\n"))

    def test_position_on_fence_counts(self):
        self.assertEqual(mermaid_block_at(self.TEXT, self.TEXT.index("```mermaid"))[0], 0)

    def test_position_outside_blocks(self):
        self.assertIsNone(mermaid_block_at(self.TEXT, self.TEXT.index("middle")))
        self.assertIsNone(mermaid_block_at("", 0))


if __name__ == "__main__":
    unittest.main()
