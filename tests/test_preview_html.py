import os
import tempfile
import unittest

from preview_html import (
    build_mermaid_viewer_shell, build_preview_shell, build_standalone_html, inline_local_images,
    markdown_to_html, preview_render_script
)

ASSETS = {"mermaid": "file:///m.js", "mathjax": "file:///t.js"}
LABELS = {"copy": "Copy", "copied": "Copied", "failed": "Failed"}


class MarkdownToHtmlTests(unittest.TestCase):
    def test_mermaid_blocks_become_escaped_divs(self):
        result = markdown_to_html("# T\n\n```mermaid\nflowchart TD\n  A-->B<br>\n```\n")
        self.assertIn('<div class="mermaid">', result)
        self.assertIn("A--&gt;B&lt;br&gt;", result)
        self.assertIn("<h1", result)

    def test_windows_newlines(self):
        self.assertIn('class="mermaid"', markdown_to_html("```mermaid\r\nflowchart TD\r\nA-->B\r\n```\r\n"))


class ShellTests(unittest.TestCase):
    def test_preview_shell_has_no_unfilled_tokens(self):
        for dark in (False, True):
            html = build_preview_shell(dark, ASSETS, LABELS, custom_css="body{}")
            self.assertNotRegex(html, r"__[A-Z_]+__")
            self.assertIn("file:///m.js", html)

    def test_custom_css_cannot_close_style_tag(self):
        html = build_preview_shell(False, ASSETS, LABELS, custom_css="</style><script>x</script>")
        self.assertNotIn("</style><script>", html)

    def test_viewer_shell_filled(self):
        self.assertNotRegex(build_mermaid_viewer_shell(True, ASSETS), r"__[A-Z_]+__")

    def test_render_script_is_json_encoded(self):
        script = preview_render_script('<p>"hi"</p>', "file:///a/")
        self.assertEqual(script, 'window.nebulaRender("<p>\\"hi\\"</p>", "file:///a/");')

    def test_standalone_export_uses_cdn_and_escapes_script(self):
        html = build_standalone_html("<p>x</p><script>alert(1)</script>", False, LABELS, title="Doc")
        self.assertIn("cdn.jsdelivr.net/npm/mermaid@", html)
        self.assertIn("<title>Doc</title>", html)
        self.assertNotIn("<script>alert(1)</script>", html)


class InlineImageTests(unittest.TestCase):
    def test_relative_image_becomes_data_uri(self):
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, "img dir"))
            with open(os.path.join(folder, "img dir", "a.png"), "wb") as f:
                f.write(b"\x89PNG")
            html = markdown_to_html("![a](img%20dir/a.png)")
            result = inline_local_images(html, folder)
            self.assertIn('src="data:image/png;base64,iVBORw=="', result)

    def test_remote_and_missing_images_untouched(self):
        html = '<img src="https://x/y.png"><img src="missing.png">'
        self.assertEqual(inline_local_images(html, "/nonexistent"), html)

    def test_relative_without_base_dir_untouched(self):
        html = '<img src="a.png">'
        self.assertEqual(inline_local_images(html, ""), html)


if __name__ == "__main__":
    unittest.main()
