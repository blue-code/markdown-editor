import re

MERMAID_BLOCK_RE = re.compile(r"```mermaid[ \t]*\r?\n([\s\S]*?)```", re.IGNORECASE)


def extract_mermaid_blocks(text):
    blocks = MERMAID_BLOCK_RE.findall(text)
    return [block.strip() for block in blocks]
