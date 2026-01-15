"""Pyte-based terminal widget adapter for Paramiko channels.

This widget uses `pyte` as the terminal emulation core and renders
plain text into a `QPlainTextEdit`. It forwards user input to a
Paramiko channel and feeds incoming bytes into pyte.

This is a minimal, prototype-friendly implementation intended for
your thesis prototype. It renders plain text (no colors/attributes)
and implements basic key mapping (Enter, Backspace, Tab, arrows).
"""
import threading
import time
from typing import Optional

from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Signal, Slot, Qt
from PySide6.QtGui import QFont

try:
    import pyte
except Exception:
    pyte = None


class PyteTerminalWidget(QPlainTextEdit):
    """A simple pyte-backed terminal widget.

    Methods:
    - set_ssh_channel(channel): attach a Paramiko channel (invoked shell)
    - set_command_logger(callable): called with a command line (str) on Enter
    - set_close_callback(callable): called when the session ends/closed
    """

    data_ready = Signal()

    def __init__(self, parent=None, cols: int = 80, rows: int = 24):
        super().__init__(parent)
        f = QFont('Courier')
        f.setPointSize(10)
        self.setFont(f)
        self.setReadOnly(False)

        self.cols = cols
        self.rows = rows
        self.channel = None
        self._reader_thread: Optional[threading.Thread] = None
        self._reader_running = False
        self._command_logger = None
        self._close_callback = None

        # pyte core
        if pyte is not None:
            self.screen = pyte.Screen(self.cols, self.rows)
            self.stream = pyte.Stream(self.screen)
        else:
            self.screen = None
            self.stream = None

        # current typed input buffer (for logging)
        self._current_input = ''
        # disable logging when password-like prompt detected
        self._suppress_logging = False

        self.data_ready.connect(self._render_screen)

    def set_ssh_channel(self, channel):
        """Attach a Paramiko channel (expects pty and invoke_shell already done)."""
        self.channel = channel
        if channel:
            self._start_reader()

    def set_command_logger(self, logger_callable):
        self._command_logger = logger_callable

    def set_close_callback(self, close_callable):
        self._close_callback = close_callable

    def _start_reader(self):
        if self._reader_running:
            return
        self._reader_running = True
        self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._reader_thread.start()

    def _read_loop(self):
        try:
            while self._reader_running and self.channel and not self.channel.closed:
                if self.channel.recv_ready():
                    data = self.channel.recv(4096)
                    if not data:
                        continue
                    # feed data into pyte (pyte expects text)
                    text = data.decode('utf-8', errors='replace')
                    if self.stream is not None:
                        try:
                            self.stream.feed(text)
                        except Exception:
                            # fallback: ignore parsing errors
                            pass
                    # heuristics: suppress logging when password prompt shown
                    try:
                        if self.screen is not None:
                            joined = '\n'.join(self.screen.display)
                            if 'password' in joined.lower() or 'passphrase' in joined.lower():
                                self._suppress_logging = True
                            else:
                                self._suppress_logging = False
                    except Exception:
                        pass
                    # notify GUI to render
                    try:
                        self.data_ready.emit()
                    except Exception:
                        pass
                else:
                    time.sleep(0.02)
        finally:
            self._reader_running = False
            # session closed
            try:
                if callable(self._close_callback):
                    self._close_callback()
            except Exception:
                pass

    @Slot()
    def _render_screen(self):
        # Minimal render: display plain text lines from pyte screen
        if self.screen is None:
            return
        try:
            lines = list(self.screen.display)
            text = '\n'.join(lines)
        except Exception:
            # fallback: show nothing
            text = ''
        # Replace the viewer content while keeping it editable area small
        self.blockSignals(True)
        self.setPlainText(text)
        self.blockSignals(False)
        # move cursor to end
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        self.setTextCursor(cursor)

    def keyPressEvent(self, event):
        # Basic mapping: send printable text directly, map special keys
        if not self.channel or self.channel.closed:
            return super().keyPressEvent(event)

        key = event.key()
        txt = event.text()
        seq = None
        if txt:
            seq = txt
        else:
            # map special keys
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                seq = '\r'
            elif key == Qt.Key_Backspace:
                seq = '\x7f'
            elif key == Qt.Key_Tab:
                seq = '\t'
            elif key == Qt.Key_Left:
                seq = '\x1b[D'
            elif key == Qt.Key_Right:
                seq = '\x1b[C'
            elif key == Qt.Key_Up:
                seq = '\x1b[A'
            elif key == Qt.Key_Down:
                seq = '\x1b[B'

        if seq is not None:
            try:
                self.channel.send(seq.encode('utf-8'))
            except Exception:
                pass

            # update logging buffer
            if seq in ('\r', '\n'):
                # commit current input as a command (unless suppressed)
                if self._current_input and not self._suppress_logging and callable(self._command_logger):
                    try:
                        self._command_logger(self._current_input)
                    except Exception:
                        pass
                self._current_input = ''
            else:
                # for escape sequences, don't append raw bytes; append printable chars
                if len(seq) == 1 and ord(seq) >= 32:
                    self._current_input += seq

            return

        # default handling if nothing matched
        return super().keyPressEvent(event)

    def closeEvent(self, event):
        # stop reader
        self._reader_running = False
        try:
            if self._reader_thread and self._reader_thread.is_alive():
                self._reader_thread.join(timeout=0.1)
        except Exception:
            pass
        super().closeEvent(event)
