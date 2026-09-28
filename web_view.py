"""Web view widget with two interchangeable backends.

- macOS: Apple's WKWebView via PyObjC. Qt WebEngine (Chromium) is not allowed on the Mac App Store
  (private API use + App Sandbox conflicts), so the macOS build never imports it.
- Other platforms: Qt WebEngine + QWebChannel.

Both expose the same API: load_file(), run_js(), has_web_focus(), copy(), to_html(), print_document(),
and emit message_received(name, data) when page JavaScript calls nebulaPost(name, data).
Set NEBULA_WEB_BACKEND=qt to force the Qt WebEngine backend on macOS during development.
"""

import os
import sys

from PyQt6.QtCore import QObject, QUrl, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QDesktopServices, QWindow
from PyQt6.QtWidgets import QVBoxLayout, QWidget


def _use_webkit():
    if sys.platform != "darwin" or os.environ.get("NEBULA_WEB_BACKEND") == "qt":
        return False
    try:
        import WebKit  # noqa: F401
        return True
    except ImportError:
        return False


USE_WEBKIT = _use_webkit()


class _BaseWebView(QWidget):
    message_received = pyqtSignal(str, str)
    load_finished = pyqtSignal()

    # Extra <head> markup each backend needs for nebulaPost() to reach Python.
    BRIDGE_HEAD = ""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._loaded = False
        self._pending_scripts = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

    def run_js(self, script, callback=None):
        """Run script once the current page has loaded; callback receives the result."""
        if not self._loaded:
            self._pending_scripts.append((script, callback))
            return
        self._evaluate(script, callback)

    def _on_loaded(self):
        self._loaded = True
        pending, self._pending_scripts = self._pending_scripts, []
        for script, callback in pending:
            self._evaluate(script, callback)
        self.load_finished.emit()

    def _begin_load(self):
        self._loaded = False
        self._pending_scripts = []

    @staticmethod
    def _should_open_externally(url, is_link_click):
        """Links clicked in the preview open in the default browser instead of replacing the page."""
        if not is_link_click:
            return False
        return url.scheme() in ("http", "https", "mailto")


# ---------------------------------------------------------------- WKWebView backend
if USE_WEBKIT:
    import objc
    from AppKit import NSApp, NSPrintInfo, NSView, NSWorkspace
    from Foundation import NSURL, NSMakeRect, NSObject
    from WebKit import (
        WKNavigationActionPolicyAllow,
        WKNavigationActionPolicyCancel,
        WKNavigationTypeLinkActivated,
        WKWebView,
        WKWebViewConfiguration,
    )

    class _WebKitDelegate(NSObject):
        """Receives script messages and navigation callbacks and forwards them to the Qt widget."""

        def initWithOwner_(self, owner):
            self = objc.super(_WebKitDelegate, self).init()
            if self is None:
                return None
            self._owner = owner
            return self

        def userContentController_didReceiveScriptMessage_(self, controller, message):
            body = message.body()
            try:
                name = str(body["name"])
                data = str(body["data"])
            except (KeyError, TypeError):
                return
            if self._owner is not None:
                self._owner.message_received.emit(name, data)

        def webView_didFinishNavigation_(self, web_view, navigation):
            if self._owner is not None:
                self._owner._on_loaded()

        def webView_decidePolicyForNavigationAction_decisionHandler_(self, web_view, action, handler):
            url = action.request().URL()
            is_link = action.navigationType() == WKNavigationTypeLinkActivated
            if url is not None and is_link and url.scheme() in ("http", "https", "mailto"):
                NSWorkspace.sharedWorkspace().openURL_(url)
                handler(WKNavigationActionPolicyCancel)
                return
            handler(WKNavigationActionPolicyAllow)

    class WebView(_BaseWebView):
        BRIDGE_HEAD = ""

        def __init__(self, parent=None):
            super().__init__(parent)
            self._delegate = _WebKitDelegate.alloc().initWithOwner_(self)
            config = WKWebViewConfiguration.alloc().init()
            config.userContentController().addScriptMessageHandler_name_(self._delegate, "nebula")
            self._web = WKWebView.alloc().initWithFrame_configuration_(NSMakeRect(0, 0, 400, 300), config)
            self._web.setNavigationDelegate_(self._delegate)
            self._native_window = QWindow.fromWinId(objc.pyobjc_id(self._web))
            self._container = QWidget.createWindowContainer(self._native_window, self)
            self.layout().addWidget(self._container)

            web, delegate = self._web, self._delegate

            def release(*_args):
                # Break the WebKit -> delegate -> widget reference cycle once Qt destroys the widget.
                web.configuration().userContentController().removeScriptMessageHandlerForName_("nebula")
                web.setNavigationDelegate_(None)
                delegate._owner = None

            self.destroyed.connect(release)

        def load_file(self, path):
            self._begin_load()
            url = NSURL.fileURLWithPath_(path)
            # Inside the App Sandbox WebKit may only read the page's own folder, so the page and its
            # scripts live together (see prepare_shell_dir) and local images are inlined by the app.
            read_access = NSURL.fileURLWithPath_isDirectory_(os.path.dirname(path), True)
            self._web.loadFileURL_allowingReadAccessToURL_(url, read_access)

        def _evaluate(self, script, callback):
            def handler(result, error):
                if callback is not None:
                    callback(None if error is not None else _to_python(result))

            self._web.evaluateJavaScript_completionHandler_(script, handler)

        def has_web_focus(self):
            window = self._web.window()
            if window is None:
                return False
            responder = window.firstResponder()
            return (responder is not None and responder.isKindOfClass_(NSView)
                    and responder.isDescendantOf_(self._web))

        def focus_web(self):
            window = self._web.window()
            if window is not None:
                window.makeFirstResponder_(self._web)

        def copy(self):
            NSApp.sendAction_to_from_("copy:", None, None)

        def to_html(self, callback):
            self._evaluate("document.documentElement.outerHTML", callback)

        def print_document(self, parent=None):
            window = self._web.window()
            if window is None:
                return False
            operation = self._web.printOperationWithPrintInfo_(NSPrintInfo.sharedPrintInfo())
            operation.setShowsPrintPanel_(True)
            operation.setShowsProgressPanel_(True)
            # WKWebView print operations render blank pages unless the view has a frame.
            operation.view().setFrame_(self._web.bounds())
            operation.runOperationModalForWindow_delegate_didRunSelector_contextInfo_(window, None, None, None)
            return True

    def _to_python(value):
        if value is None:
            return None
        if isinstance(value, (bool, int, float, str)):
            return value
        try:
            return float(value)
        except (TypeError, ValueError):
            return str(value)


# ---------------------------------------------------------------- Qt WebEngine backend
else:
    from PyQt6.QtWebChannel import QWebChannel
    from PyQt6.QtWebEngineCore import QWebEnginePage
    from PyQt6.QtWebEngineWidgets import QWebEngineView

    class _QtBridge(QObject):
        message = pyqtSignal(str, str)

        @pyqtSlot(str, str)
        def post(self, name, data):
            self.message.emit(name, data)

    class _ExternalLinkPage(QWebEnginePage):
        def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
            is_link = navigation_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked
            if _BaseWebView._should_open_externally(url, is_link):
                QDesktopServices.openUrl(url)
                return False
            return super().acceptNavigationRequest(url, navigation_type, is_main_frame)

    class WebView(_BaseWebView):
        BRIDGE_HEAD = (
            '<script src="qrc:///qtwebchannel/qwebchannel.js"></script>\n'
            "<script>\n"
            "if (typeof qt !== 'undefined' && qt.webChannelTransport) {\n"
            "  new QWebChannel(qt.webChannelTransport, function(channel) {\n"
            "    window.nebulaQtBridge = channel.objects.bridge;\n"
            "  });\n"
            "}\n"
            "</script>"
        )

        def __init__(self, parent=None):
            super().__init__(parent)
            self._view = QWebEngineView(self)
            self._page = _ExternalLinkPage(self._view)
            self._view.setPage(self._page)
            self._bridge = _QtBridge()
            self._bridge.message.connect(self.message_received)
            self._channel = QWebChannel()
            self._channel.registerObject("bridge", self._bridge)
            self._page.setWebChannel(self._channel)
            self._view.loadFinished.connect(lambda _ok: self._on_loaded())
            self.layout().addWidget(self._view)

        def load_file(self, path):
            self._begin_load()
            self._view.load(QUrl.fromLocalFile(path))

        def _evaluate(self, script, callback):
            if callback is None:
                self._page.runJavaScript(script)
            else:
                self._page.runJavaScript(script, callback)

        def has_web_focus(self):
            return self._view.hasFocus() or self._view.isAncestorOf(self.focusWidget() or self._view)

        def focus_web(self):
            self._view.setFocus()

        def copy(self):
            self._view.triggerPageAction(QWebEnginePage.WebAction.Copy)

        def to_html(self, callback):
            self._page.toHtml(callback)

        def print_document(self, parent=None):
            try:
                from PyQt6.QtPrintSupport import QPrintPreviewDialog, QPrinter
            except ImportError:
                return False
            from PyQt6.QtCore import QEventLoop

            def paint(printer):
                # QWebEngineView.print() is asynchronous; the preview dialog needs it to finish first.
                loop = QEventLoop()
                self._view.printFinished.connect(loop.quit)
                self._view.print(printer)
                loop.exec()
                self._view.printFinished.disconnect(loop.quit)

            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintPreviewDialog(printer, parent or self)
            dialog.paintRequested.connect(paint)
            dialog.exec()
            return True
