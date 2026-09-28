"""Pure text transforms used by the editor's Tools menu."""

import re
import unicodedata

_SEPARATOR_CELL = re.compile(r"^\s*:?-{1,}:?\s*$")


def display_width(text):
    """Column width of text in a monospace editor (CJK and emoji count as two columns)."""
    width = 0
    for ch in text:
        if unicodedata.combining(ch) or ch in ("‍", "️"):
            continue
        width += 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
    return width


def _split_row(line):
    """Split a Markdown table row into trimmed cells, honouring escaped pipes."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|") and not stripped.endswith("\\|"):
        stripped = stripped[:-1]
    cells = re.split(r"(?<!\\)\|", stripped)
    return [cell.strip() for cell in cells]


def _is_table_row(line):
    return "|" in line and line.strip() != ""


def _is_separator_row(line):
    cells = _split_row(line)
    return bool(cells) and all(_SEPARATOR_CELL.match(cell) for cell in cells)


def _alignment(cell):
    cell = cell.strip()
    left, right = cell.startswith(":"), cell.endswith(":")
    if left and right:
        return "center"
    if right:
        return "right"
    if left:
        return "left"
    return None


def _pad(text, width, align):
    gap = width - display_width(text)
    if gap <= 0:
        return text
    if align == "right":
        return " " * gap + text
    if align == "center":
        left = gap // 2
        return " " * left + text + " " * (gap - left)
    return text + " " * gap


def _format_table(lines):
    rows = [_split_row(line) for line in lines]
    column_count = max(len(row) for row in rows)
    rows = [row + [""] * (column_count - len(row)) for row in rows]
    aligns = [_alignment(cell) for cell in rows[1]]

    widths = [3] * column_count
    for index, row in enumerate(rows):
        if index == 1:
            continue
        for col, cell in enumerate(row):
            widths[col] = max(widths[col], display_width(cell))

    formatted = []
    for index, row in enumerate(rows):
        if index == 1:
            cells = []
            for col in range(column_count):
                align = aligns[col]
                dashes = widths[col]
                if align == "center":
                    cells.append(":" + "-" * (dashes - 2) + ":")
                elif align == "right":
                    cells.append("-" * (dashes - 1) + ":")
                elif align == "left":
                    cells.append(":" + "-" * (dashes - 1))
                else:
                    cells.append("-" * dashes)
        else:
            cells = [_pad(cell, widths[col], aligns[col]) for col, cell in enumerate(row)]
        formatted.append("| " + " | ".join(cells) + " |")
    return formatted


def format_markdown_tables(text):
    """Align every pipe table in text. Returns (new_text, table_count).

    Tables inside fenced code blocks are left untouched. Newline style (\\n or \\r\\n) is preserved.
    """
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(newline)
    output = []
    count = 0
    in_fence = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            output.append(line)
            index += 1
            continue
        if (not in_fence and _is_table_row(line) and index + 1 < len(lines)
                and _is_separator_row(lines[index + 1])):
            end = index + 2
            while end < len(lines) and _is_table_row(lines[end]) and not lines[end].lstrip().startswith("```"):
                end += 1
            indent = line[: len(line) - len(line.lstrip())]
            output.extend(indent + row for row in _format_table(lines[index:end]))
            count += 1
            index = end
            continue
        output.append(line)
        index += 1
    return newline.join(output), count
