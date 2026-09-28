"""HTML builders for the live preview and the Mermaid viewer.

Each web view loads a static "shell" page once (scripts, theme, CSS) and then receives content
updates through JavaScript, so typing does not reload Mermaid/MathJax or reset the scroll position.
JavaScript talks back to Python through nebulaPost(name, data), which each web backend wires up.
"""

import base64
import html
import json
import mimetypes
import os
import re
from urllib.parse import unquote, urlparse

import markdown
from pygments.formatters import HtmlFormatter

from mermaid_utils import replace_mermaid_blocks

MARKDOWN_EXTENSIONS = ["tables", "fenced_code", "codehilite", "toc", "nl2br", "sane_lists"]

# Shared by every shell page: routes messages to WKWebView or Qt WebChannel.
_POST_SCRIPT = """
function nebulaPost(name, data) {
  var payload = String(data == null ? '' : data);
  if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.nebula) {
    window.webkit.messageHandlers.nebula.postMessage({name: name, data: payload});
    return true;
  }
  if (window.nebulaQtBridge) {
    window.nebulaQtBridge.post(name, payload);
    return true;
  }
  return false;
}
"""


def markdown_to_html(text):
    """Convert Markdown to an HTML fragment, turning ```mermaid fences into <div class="mermaid">."""
    def to_mermaid_div(block):
        return f'\n<div class="mermaid">\n{html.escape(block)}\n</div>\n'

    prepared = replace_mermaid_blocks(text, to_mermaid_div)
    return markdown.Markdown(extensions=MARKDOWN_EXTENSIONS).convert(prepared)


_IMG_SRC_RE = re.compile(r'(<img\b[^>]*?\bsrc=")([^"]+)(")', re.IGNORECASE)
MAX_INLINE_IMAGE_BYTES = 15 * 1024 * 1024


def _local_image_path(src, base_dir):
    if src.startswith(("data:", "http:", "https:", "//")):
        return None
    if src.startswith("file:"):
        return unquote(urlparse(src).path)
    path = unquote(src.split("#", 1)[0].split("?", 1)[0])
    if not os.path.isabs(path):
        if not base_dir:
            return None
        path = os.path.join(base_dir, path)
    return os.path.normpath(path)


def _read_file(path):
    with open(path, "rb") as f:
        return f.read()


def inline_local_images(content_html, base_dir, reader=None):
    """Embed local <img> files as data: URIs.

    The WebKit content process cannot read files next to the document inside the App Sandbox,
    but the app process can (it was granted the document or its folder), so it reads them instead.
    reader(path) -> bytes lets the caller route reads through Qt's sandbox-aware file engine.
    Unreadable or oversized images are left untouched.
    """
    reader = reader or _read_file

    def replace(match):
        src = html.unescape(match.group(2))
        path = _local_image_path(src, base_dir)
        if not path:
            return match.group(0)
        try:
            raw = reader(path)
        except OSError:
            return match.group(0)
        if len(raw) > MAX_INLINE_IMAGE_BYTES:
            return match.group(0)
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        data = base64.b64encode(raw).decode("ascii")
        return f"{match.group(1)}data:{mime};base64,{data}{match.group(3)}"

    return _IMG_SRC_RE.sub(replace, content_html)


def _theme_colors(dark_mode):
    if dark_mode:
        return {
            "bg": "#1e1e1e", "fg": "#d4d4d4", "code_bg": "#2d2d2d", "border": "#444",
            "btn_border": "#666", "btn_bg": "#3a3a3a", "btn_hover": "#4a4a4a",
        }
    return {
        "bg": "#ffffff", "fg": "#333333", "code_bg": "#f5f5f5", "border": "#ddd",
        "btn_border": "#cfd3d8", "btn_bg": "#ffffff", "btn_hover": "#f0f3f6",
    }


def _fill(template, values):
    for key, value in values.items():
        template = template.replace(f"__{key}__", value)
    return template


_PREVIEW_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<base id="doc-base" href="__BASE_URL__">
__BRIDGE_HEAD__
<script>
__POST_SCRIPT__
window.MathJax = {
  tex: { inlineMath: [['$', '$'], ['\\\\(', '\\\\)']] },
  svg: { fontCache: 'global' }
};
var COPY_LABELS = __COPY_LABELS__;

function setScroll(percent) {
  var h = document.documentElement.scrollHeight - window.innerHeight;
  window.scrollTo(0, percent * h);
}

function copyText(text, button) {
  if (!nebulaPost('copy', text)) {
    try {
      var textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
    } catch (err) {
      button.textContent = COPY_LABELS.failed;
      setTimeout(function() { button.textContent = COPY_LABELS.copy; }, 1200);
      return;
    }
  }
  button.textContent = COPY_LABELS.copied;
  setTimeout(function() { button.textContent = COPY_LABELS.copy; }, 1200);
}

function addCodeCopyButtons(root) {
  root.querySelectorAll('pre').forEach(function(pre) {
    if (!pre.parentElement || pre.closest('.code-block-wrap')) { return; }
    var wrapper = document.createElement('div');
    wrapper.className = 'code-block-wrap';
    pre.parentElement.insertBefore(wrapper, pre);
    wrapper.appendChild(pre);
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'code-copy-btn';
    button.textContent = COPY_LABELS.copy;
    button.addEventListener('click', function() {
      copyText(pre.innerText.replace(/\\n$/, ''), button);
    });
    wrapper.appendChild(button);
  });
}

function renderDiagrams(root) {
  var nodes = root.querySelectorAll('.mermaid');
  if (!nodes.length || !window.mermaid) { return; }
  try {
    window.mermaid.run({ nodes: nodes, suppressErrors: true });
  } catch (err) {}
}

function renderMath(root) {
  var mj = window.MathJax;
  if (!mj || !mj.startup || !mj.startup.promise || !mj.typesetPromise) { return; }
  mj.startup.promise = mj.startup.promise.then(function() { return mj.typesetPromise([root]); }).catch(function() {});
}

window.nebulaRender = function(content, baseUrl) {
  var root = document.getElementById('content');
  if (baseUrl) { document.getElementById('doc-base').setAttribute('href', baseUrl); }
  if (window.MathJax && window.MathJax.typesetClear) { window.MathJax.typesetClear([root]); }
  root.innerHTML = content;
  addCodeCopyButtons(root);
  renderDiagrams(root);
  renderMath(root);
};
</script>
<script src="__MERMAID_URL__"></script>
<script>
if (window.mermaid) {
  window.mermaid.initialize({ startOnLoad: false, theme: '__MERMAID_THEME__', securityLevel: 'strict' });
}
</script>
<script id="MathJax-script" async src="__MATHJAX_URL__"></script>
<style>
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Hiragino Sans', 'Apple SD Gothic Neo', 'PingFang SC', Roboto, sans-serif;
       line-height: 1.7; padding: 25px; max-width: 850px; margin: 0 auto;
       background: __BG__; color: __FG__; }
h1,h2,h3,h4,h5,h6 { margin-top: 1.5em; margin-bottom: 0.5em; font-weight: 600; }
h1 { font-size: 2em; border-bottom: 2px solid __CODE_BG__; padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid __CODE_BG__; padding-bottom: 0.3em; }
code { background: __CODE_BG__; padding: 0.2em 0.4em; border-radius: 3px; font-family: 'SF Mono', Menlo, Consolas, monospace; font-size: 0.9em; }
pre { background: __CODE_BG__; padding: 16px; border-radius: 8px; overflow-x: auto; }
pre code { background: none; padding: 0; }
.codehilite { background: __CODE_BG__; border-radius: 8px; }
.code-block-wrap { position: relative; margin: 1em 0; }
.code-block-wrap pre { margin: 0; padding-top: 40px; }
.code-copy-btn { position: absolute; top: 8px; right: 8px; border: 1px solid __BTN_BORDER__;
  background: __BTN_BG__; color: __FG__; border-radius: 6px; padding: 4px 10px; font-size: 12px; cursor: pointer; }
.code-copy-btn:hover { background: __BTN_HOVER__; }
blockquote { border-left: 4px solid #007AFF; margin: 1em 0; padding: 0.5em 1em; background: __CODE_BG__; border-radius: 0 8px 8px 0; }
table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid __BORDER__; padding: 10px 14px; text-align: left; }
th { background: __CODE_BG__; font-weight: 600; }
tr:nth-child(even) { background: __CODE_BG__; }
img { max-width: 100%; border-radius: 8px; }
a { color: #007AFF; text-decoration: none; }
a:hover { text-decoration: underline; }
ul, ol { padding-left: 2em; }
li { margin: 0.3em 0; }
hr { border: none; border-top: 1px solid __CODE_BG__; margin: 2em 0; }
.mermaid { background: transparent; text-align: center; margin: 1em 0; }
input[type="checkbox"] { margin-right: 8px; }
__PYGMENTS_CSS__
__CUSTOM_CSS__
</style></head><body>
<div id="content"></div>
</body></html>
"""


def build_preview_shell(dark_mode, assets, copy_labels, bridge_head="", custom_css="", base_url=""):
    """Static preview page. assets: {'mermaid': url, 'mathjax': url}."""
    colors = _theme_colors(dark_mode)
    pygments_style = "monokai" if dark_mode else "default"
    pygments_css = HtmlFormatter(style=pygments_style).get_style_defs(".codehilite")
    return _fill(_PREVIEW_TEMPLATE, {
        "BASE_URL": html.escape(base_url, quote=True),
        "BRIDGE_HEAD": bridge_head,
        "POST_SCRIPT": _POST_SCRIPT,
        "COPY_LABELS": json.dumps(copy_labels, ensure_ascii=False),
        "MERMAID_URL": assets["mermaid"],
        "MATHJAX_URL": assets["mathjax"],
        "MERMAID_THEME": "dark" if dark_mode else "default",
        "BG": colors["bg"],
        "FG": colors["fg"],
        "CODE_BG": colors["code_bg"],
        "BORDER": colors["border"],
        "BTN_BORDER": colors["btn_border"],
        "BTN_BG": colors["btn_bg"],
        "BTN_HOVER": colors["btn_hover"],
        "PYGMENTS_CSS": pygments_css,
        # Custom CSS is inserted last so it can override everything; '</' would close the tag.
        "CUSTOM_CSS": custom_css.replace("</", "<\\/"),
    })


def preview_render_script(content_html, base_url=""):
    """JavaScript that swaps new content into an already-loaded preview shell."""
    return f"window.nebulaRender({json.dumps(content_html)}, {json.dumps(base_url)});"


_VIEWER_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="UTF-8">
__BRIDGE_HEAD__
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;overflow:auto;background:__BG__;color:__FG__}
#container{display:flex;justify-content:center;align-items:center;min-height:100%;padding:30px}
#diagram{transform-origin:center;transition:transform 0.15s ease-out}
#error{position:fixed;left:0;right:0;bottom:0;font-family:'SF Mono',Menlo,Consolas,monospace;white-space:pre-wrap;color:#d9534f;padding:20px}
</style>
<script>
__POST_SCRIPT__
var currentScale = 1;
var renderCount = 0;
var currentCode = '';

function setZoom(s) {
  currentScale = s / 100;
  var el = document.getElementById('diagram');
  if (el) { el.style.transform = 'scale(' + currentScale + ')'; }
}

function fitToView() {
  var c = document.getElementById('container');
  var svg = document.querySelector('#diagram svg');
  if (!svg) { return 100; }
  var rect = svg.getBoundingClientRect();
  var naturalWidth = rect.width / currentScale;
  var naturalHeight = rect.height / currentScale;
  var scale = Math.min((c.clientWidth - 60) / naturalWidth, (c.clientHeight - 60) / naturalHeight) * 100;
  return Math.round(Math.min(Math.max(scale, 10), 500));
}

window.nebulaShowDiagram = function(code) {
  var target = document.getElementById('diagram');
  var errorBox = document.getElementById('error');
  errorBox.textContent = '';
  if (!window.mermaid) { errorBox.textContent = 'Mermaid failed to load.'; return; }
  currentCode = code;
  renderCount += 1;
  window.mermaid.render('nebula-diagram-' + renderCount, code).then(function(result) {
    target.innerHTML = result.svg;
  }).catch(function(err) {
    target.innerHTML = '';
    errorBox.textContent = String(err && err.message ? err.message : err);
  });
};

function exportSVG() {
  var svg = document.querySelector('#diagram svg');
  if (!svg) { return; }
  var clone = svg.cloneNode(true);
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  nebulaPost('svg', new XMLSerializer().serializeToString(clone));
}

function drawPNG(svg, scale) {
  var clone = svg.cloneNode(true);
  clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
  var box = svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width ? svg.viewBox.baseVal : svg.getBBox();
  var width = box.width, height = box.height;
  clone.setAttribute('width', width);
  clone.setAttribute('height', height);
  var data = new XMLSerializer().serializeToString(clone);
  var img = new Image();
  img.onload = function() {
    var canvas = document.createElement('canvas');
    canvas.width = Math.ceil(width * scale);
    canvas.height = Math.ceil(height * scale);
    var ctx = canvas.getContext('2d');
    ctx.fillStyle = '__BG__';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.scale(scale, scale);
    ctx.drawImage(img, 0, 0, width, height);
    nebulaPost('png', canvas.toDataURL('image/png'));
  };
  img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(data);
}

// HTML labels (foreignObject) would taint the canvas, so PNG export re-renders with SVG text labels.
function exportPNG(scale) {
  scale = scale || 1;
  if (!window.mermaid || !currentCode) { return; }
  window.mermaid.initialize(Object.assign({}, MERMAID_CONFIG, EXPORT_LABELS));
  renderCount += 1;
  var host = document.createElement('div');
  host.style.cssText = 'position:absolute;left:-10000px;top:0';
  document.body.appendChild(host);
  window.mermaid.render('nebula-export-' + renderCount, currentCode, host).then(function(result) {
    host.innerHTML = result.svg;
    drawPNG(host.querySelector('svg'), scale);
  }).catch(function() {}).then(function() {
    document.body.removeChild(host);
    window.mermaid.initialize(MERMAID_CONFIG);
  });
}
</script>
<script src="__MERMAID_URL__"></script>
<script>
var MERMAID_CONFIG = {
  startOnLoad: false,
  theme: '__MERMAID_THEME__',
  securityLevel: 'strict',
  flowchart: { useMaxWidth: false },
  sequence: { useMaxWidth: false },
  gantt: { useMaxWidth: false },
  journey: { useMaxWidth: false },
  timeline: { useMaxWidth: false },
  mindmap: { useMaxWidth: false },
  sankey: { useMaxWidth: false }
};
var EXPORT_LABELS = { htmlLabels: false, flowchart: { useMaxWidth: false, htmlLabels: false } };
if (window.mermaid) { window.mermaid.initialize(MERMAID_CONFIG); }
</script>
</head><body>
<div id="container"><div id="diagram"></div></div>
<div id="error"></div>
</body></html>
"""


def build_mermaid_viewer_shell(dark_mode, assets, bridge_head=""):
    colors = _theme_colors(dark_mode)
    return _fill(_VIEWER_TEMPLATE, {
        "BRIDGE_HEAD": bridge_head,
        "POST_SCRIPT": _POST_SCRIPT,
        "BG": colors["bg"],
        "FG": colors["fg"],
        "MERMAID_URL": assets["mermaid"],
        "MERMAID_THEME": "dark" if dark_mode else "default",
    })


def mermaid_show_script(code):
    return f"window.nebulaShowDiagram({json.dumps(code)});"


CDN_ASSETS = {
    "mermaid": "https://cdn.jsdelivr.net/npm/mermaid@11.17.2/dist/mermaid.min.js",
    "mathjax": "https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js",
}


def build_standalone_html(content_html, dark_mode, copy_labels, custom_css="", title="", lang="en"):
    """Self-contained HTML export that renders Mermaid/MathJax from a CDN in any browser."""
    page = build_preview_shell(dark_mode, CDN_ASSETS, copy_labels, custom_css=custom_css)
    page = page.replace("<html>", f'<html lang="{html.escape(lang, quote=True)}">', 1)
    page = page.replace("<head>", f"<head><title>{html.escape(title)}</title>", 1)
    # "</" inside an inline script would end the tag early.
    script = preview_render_script(content_html).replace("</", "<\\/")
    render = f"<script>{script}</script>\n</body>"
    return page.replace("</body>", render, 1)
