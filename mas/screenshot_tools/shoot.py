"""Capture App Store screenshots (1440x900) for one language.

Usage (from repo root, uses a throwaway HOME so real settings are untouched):
    for L in en ko ja zh; do H=$(mktemp -d); echo "{\"language\":\"$L\"}" > $H/.markdownpro_config.json; \
        HOME=$H venv/bin/python mas/screenshot_tools/shoot.py $L /tmp/shots; done
"""
import os, sys, subprocess
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO); sys.path.insert(0, os.path.dirname(__file__))
lang, out_dir = sys.argv[1], sys.argv[2]
from docs import DOCS
doc_path = os.path.join(os.environ["HOME"], f"launch-{lang}.md")
open(doc_path, "w", encoding="utf-8").write(DOCS[lang])
sys.argv = ["x", doc_path]
import objc
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
import markdown_editor as me
from localized_content import mermaid_examples

def capture(widget, name):
    view = objc.objc_object(c_void_p=int(widget.winId()))
    number = view.window().windowNumber()
    subprocess.run(["screencapture", "-x", "-o", "-l", str(number), os.path.join(out_dir, f"{lang}-{name}.png")])

def steps():
    app = QApplication.instance(); w = app.window
    w.setGeometry(60, 60, 1440, 868)
    w.side_panel.setCurrentIndex(1)  # outline
    w.splitter.setSizes([560, 560])
    def at(delay, fn):
        QTimer.singleShot(delay, fn)
    at(3500, lambda: capture(w, "1-editor"))
    def dark():
        w.toggle_dark_mode(); w.side_panel.setCurrentIndex(3)
        w.mermaid_panel.list.setCurrentRow(2)
        code = dict((i, c) for i, _, c in mermaid_examples(me.current_language()))["sequence"]
        w.editor.setPlainText(w.editor.toPlainText().split("## ")[0] + code + "\n")
    at(4500, dark)
    def clean(): w.is_modified = False; w.update_title()
    at(7500, clean)
    at(8000, lambda: capture(w, "2-dark"))
    def viewer():
        code = dict((i, c) for i, _, c in mermaid_examples(me.current_language()))["mindmap"]
        w.editor.setPlainText(code)
        w.open_mermaid_viewer()
        w.mermaid_viewer.setGeometry(60, 60, 1440, 868)
    at(9000, viewer)
    at(12000, lambda: w.mermaid_viewer.fit_to_view())
    at(13500, lambda: capture(w.mermaid_viewer, "3-viewer"))
    at(14500, lambda: os._exit(0))

_orig_show = me.MarkdownEditor.show
def _show(self):
    _orig_show(self); QTimer.singleShot(1000, steps)
me.MarkdownEditor.show = _show
me.main()
