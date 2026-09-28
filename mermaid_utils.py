import re

MERMAID_BLOCK_RE = re.compile(r"```mermaid[ \t]*\r?\n([\s\S]*?)```", re.IGNORECASE)


def extract_mermaid_blocks(text):
    blocks = MERMAID_BLOCK_RE.findall(text)
    return [block.strip() for block in blocks]


def replace_mermaid_blocks(text, replacer):
    """Replace each ```mermaid fence with replacer(block_source)."""
    return MERMAID_BLOCK_RE.sub(lambda match: replacer(match.group(1).strip()), text)


def mermaid_block_at(text, position):
    """(index, source) of the ```mermaid fence containing character offset position, else None."""
    for index, match in enumerate(MERMAID_BLOCK_RE.finditer(text)):
        if match.start() <= position <= match.end():
            return index, match.group(1)
    return None
