from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QDockWidget
)
from PySide6.QtWidgets import QInputDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import threading
import time
from backend.ssh_client import SSHClientManager
from backend.auth import ZeroTrustAuth
from gui.config import ConfigPanel
from gui.history_viewer import HistoryViewer
# Optional pyte-based terminal; fall back to built-in TerminalWidget
try:
    from gui.pyte_terminal import PyteTerminalWidget as PyteTerminal
except Exception:
    PyteTerminal = None


class TerminalWidget(QTextEdit):
    """A terminal-like text widget that allows typing input and displaying output."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.command_history = []
        self.history_index = -1
        self.current_input_line = 0
        self.prompt = '> '
        self.ssh_channel = None  # paramiko SSH channel
        self.read_thread = None
        self.thread_running = False
        
        # terminal styling
        font = QFont('Courier')
        font.setPointSize(10)
        self.setFont(font)
        self.setStyleSheet('background-color: #1e1e1e; color: #d4d4d4;')
        
        # initialize with prompt
        self._print_prompt()
    
    def set_ssh_channel(self, channel):
        """Set the paramiko SSH channel for interactive I/O."""
        self.ssh_channel = channel
        if channel:
            self._start_read_thread()

    def set_command_logger(self, logger_callable):
        """Set a callable to be invoked with the command text after sending to SSH.

        The callable should accept a single string argument (the command).
        """
        self._command_logger = logger_callable

    def set_close_callback(self, close_callable):
        """Set a callable to be invoked when the terminal requests the SSH session to close."""
        self._close_callback = close_callable
    
    def _start_read_thread(self):
        """Start a background thread to read from the SSH channel."""
        if self.thread_running:
            return
        self.thread_running = True
        self.read_thread = threading.Thread(target=self._read_channel_loop, daemon=True)
        self.read_thread.start()
    
    def _read_channel_loop(self):
        """Read output from SSH channel in background and display it."""
        try:
            while self.thread_running and self.ssh_channel:
                # check if data is available (non-blocking)
                if self.ssh_channel.recv_ready():
                    data = self.ssh_channel.recv(1024)
                    if data:
                        text = data.decode('utf-8', errors='replace')
                        # display output via Qt signal-safe method
                        self.log(text.rstrip('\r\n'))
                else:
                    time.sleep(0.1)
        except Exception as e:
            # connection closed or error
            self.log(f'[SSH connection closed: {e}]')
            self.thread_running = False
    
    def _print_prompt(self):
        """Add a new prompt line."""
        self.append(self.prompt)
        self.current_input_line = self.document().blockCount() - 1
        self.moveCursor(self.textCursor().__class__.End)
    
    def log(self, text: str):
        """Print output to terminal (read-only line)."""
        # move to end, remove the prompt temporarily
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        # get current line (the one with prompt)
        block = self.document().findBlock(cursor.position())
        line_text = block.text()
        
        # if we have a prompt, insert output above it
        if line_text.startswith(self.prompt):
            cursor.movePosition(cursor.MoveOperation.StartOfBlock)
            cursor.insertText(text + '\n')
            self.setTextCursor(cursor)
        else:
            # no prompt, just append
            self.append(text)
            # only add new prompt if not connected to SSH
            if not self.ssh_channel:
                self._print_prompt()
    
    def _send_command_to_ssh(self, command: str):
        """Send command to SSH channel and await response."""
        if not self.ssh_channel:
            self.log('[No SSH channel connected]')
            self._print_prompt()
            return
        
        try:
            # send command with newline
            self.ssh_channel.send(command + '\n')
            # small delay for command to execute
            time.sleep(0.2)
        except Exception as e:
            self.log(f'[SSH send error: {e}]')
        else:
            # log the command to persistent storage if a logger was provided
            try:
                if hasattr(self, '_command_logger') and callable(self._command_logger):
                    self._command_logger(command)
            except Exception:
                pass
        
    def mousePressEvent(self, event):
        """Prevent clicking on text outside the current line."""
        cursor = self.textCursor()
        cursor.setPosition(self.cursorForPosition(event.pos()).position())
        block = cursor.block()
        pos_in_block = cursor.positionInBlock()
        
        # Only allow clicks on the last (current input) line
        if block.blockNumber() != self.document().blockCount() - 1:
            # Clicked on old text, move to end instead
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)
            return
        
        # Allow click only after the prompt
        if pos_in_block < len(self.prompt):
            cursor.setPosition(block.position() + len(self.prompt))
            self.setTextCursor(cursor)
            return
        
        super().mousePressEvent(event)
    
    def insertFromMimeData(self, source):
        """Only allow paste on the current input line."""
        cursor = self.textCursor()
        block = cursor.block()
        pos_in_block = cursor.positionInBlock()
        
        # Only allow on last line, after prompt
        if block.blockNumber() == self.document().blockCount() - 1 and pos_in_block >= len(self.prompt):
            super().insertFromMimeData(source)
    
    def cut(self):
        """Only allow cut on the current input line."""
        cursor = self.textCursor()
        block = cursor.block()
        
        if block.blockNumber() == self.document().blockCount() - 1:
            super().cut()
    
    def mousePressEvent(self, event):
        """Prevent clicking on text outside the current line."""
        cursor = self.textCursor()
        cursor.setPosition(self.cursorForPosition(event.pos()).position())
        block = cursor.block()
        pos_in_block = cursor.positionInBlock()
        
        # Only allow clicks on the last (current input) line
        if block.blockNumber() != self.document().blockCount() - 1:
            # Clicked on old text, move to end instead
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)
            return
        
        # Allow click only after the prompt
        if pos_in_block < len(self.prompt):
            cursor.setPosition(block.position() + len(self.prompt))
            self.setTextCursor(cursor)
            return
        
        super().mousePressEvent(event)
    
    def insertFromMimeData(self, source):
        """Only allow paste on the current input line."""
        cursor = self.textCursor()
        block = cursor.block()
        pos_in_block = cursor.positionInBlock()
        
        # Only allow on last line, after prompt
        if block.blockNumber() == self.document().blockCount() - 1 and pos_in_block >= len(self.prompt):
            super().insertFromMimeData(source)
    
    def cut(self):
        """Only allow cut on the current input line."""
        cursor = self.textCursor()
        block = cursor.block()
        
        if block.blockNumber() == self.document().blockCount() - 1:
            super().cut()

    def keyPressEvent(self, event):
        """Handle key presses: Return for command, Up/Down for history."""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # get current line text
            cursor = self.textCursor()
            block = self.document().findBlock(cursor.position())
            line_text = block.text()
            
            # extract command (remove prompt)
            command = line_text.replace(self.prompt, '', 1).strip()
            
            if command:
                # store in history
                self.command_history.append(command)
                self.history_index = -1
                
                # print command as echo
                self.append('')
                
                # handle built-in commands
                if command.lower() == 'clear':
                    self.clear()
                    self._print_prompt()
                elif command.lower() == 'exit':
                    if self.ssh_channel:
                        self.log('[Closing SSH connection]')
                        self.thread_running = False
                        try:
                            self.ssh_channel.close()
                        except Exception:
                            pass
                        self.ssh_channel = None
                        # notify manager to close and mark session ended
                        try:
                            if hasattr(self, '_close_callback') and callable(self._close_callback):
                                self._close_callback()
                        except Exception:
                            pass
                        self._print_prompt()
                    else:
                        self.log('[No SSH connection to close]')
                        self._print_prompt()
                elif self.ssh_channel:
                    # send to SSH channel
                    self._send_command_to_ssh(command)
                else:
                    # no SSH, just echo
                    self.log(f'[local: {command}]')
                    self._print_prompt()
            else:
                # empty command, just add new prompt
                self.append('')
                self._print_prompt()
        
        elif event.key() == Qt.Key.Key_Up:
            # show previous command
            if self.command_history:
                if self.history_index < len(self.command_history) - 1:
                    self.history_index += 1
                    self._replace_current_command(self.command_history[-(self.history_index + 1)])
            event.accept()
        
        elif event.key() == Qt.Key.Key_Down:
            # show next command
            if self.history_index > 0:
                self.history_index -= 1
                self._replace_current_command(self.command_history[-(self.history_index + 1)])
            elif self.history_index == 0:
                self.history_index = -1
                self._replace_current_command('')
            event.accept()
        
        else:
            # normal key press
            super().keyPressEvent(event)
    
    def _replace_current_command(self, new_cmd: str):
        """Replace the current input command in the prompt line."""
        cursor = self.textCursor()
        block = self.document().findBlock(cursor.position())
        block_num = block.blockNumber()
        
        # select from prompt end to end of line
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        cursor.movePosition(cursor.MoveOperation.EndOfBlock, cursor.MoveMode.KeepAnchor)
        
        # delete and rewrite
        cursor.removeSelectedText()
        cursor.insertText(self.prompt + new_cmd)
        self.setTextCursor(cursor)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zero Trust SSH Client (Prototype)')
        self.resize(800, 600)

        self.config_dock = None  # dock reference
        # global debug mode (off by default). When enabled this toggles:
        # - policy bypass in auth
        # - debug key logging output
        # - (future) other debug helpers
        self.debug_mode = False
        self.debug_key_logging = False

        self._build_ui()

        # self.log('Welcome to Zero Trust SSH Client. Enter host, username, and port to start connecting.')
        self.ssh_manager = SSHClientManager()
        self.auth = ZeroTrustAuth()

    def _build_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        form = QHBoxLayout()

        # input fields
        self.host_in = QLineEdit()
        self.host_in.setPlaceholderText('host (e.g. 192.168.1.100)')

        self.port_in = QLineEdit()
        self.port_in.setPlaceholderText('port (22)')
        self.port_in.setFixedWidth(80)

        self.user_in = QLineEdit()
        self.user_in.setPlaceholderText('username')

        self.keypath_in = QLineEdit()
        self.keypath_in.setPlaceholderText('path to private key (optional)')

        # buttons
        self.connect_btn = QPushButton('Connect')
        self.config_btn = QPushButton('Config')
        self.history_btn = QPushButton('History')
        self.debug_btn = QPushButton('🐛 Debug')

        self.connect_btn.clicked.connect(self.on_connect)
        self.config_btn.clicked.connect(self.show_config_panel)
        self.history_btn.clicked.connect(self.show_history_panel)
        self.debug_btn.clicked.connect(self.on_toggle_debug)

        # add widgets
        form.addWidget(QLabel('Host:'))
        form.addWidget(self.host_in)
        form.addWidget(QLabel('Port:'))
        form.addWidget(self.port_in)
        form.addWidget(QLabel('User:'))
        form.addWidget(self.user_in)
        form.addWidget(self.keypath_in)
        form.addWidget(self.connect_btn)
        form.addWidget(self.config_btn)
        form.addWidget(self.history_btn)
        form.addWidget(self.debug_btn)

        layout.addLayout(form)

        # prefer pyte-backed terminal if available (better ANSI handling)
        if PyteTerminal is not None:
            try:
                self.terminal = PyteTerminal()
            except Exception:
                self.terminal = TerminalWidget()
        else:
            self.terminal = TerminalWidget()
        layout.addWidget(self.terminal)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)  # IMPORTANT!

    def log(self, text: str):
        """Write a message to the terminal widget or stdout if unavailable."""
        try:
            if hasattr(self, 'terminal') and self.terminal is not None:
                # terminal may be a pyte widget (QPlainTextEdit) or QTextEdit
                try:
                    # prefer append-like API
                    append = getattr(self.terminal, 'append', None)
                    if callable(append):
                        append(text)
                        return
                except Exception:
                    pass
                try:
                    # fallback for QPlainTextEdit
                    set_text = getattr(self.terminal, 'setPlainText', None)
                    if callable(set_text):
                        # append to existing content
                        cur = self.terminal.toPlainText()
                        if cur:
                            self.terminal.setPlainText(cur + '\n' + text)
                        else:
                            self.terminal.setPlainText(text)
                        return
                except Exception:
                    pass
        except Exception:
            pass
        # final fallback
        try:
            print(text)
        except Exception:
            pass

    # def log(self, text: str):
        # self.terminal.append(text)

    def _log_debug_key_attempts(self):
        """If debug logging is enabled, dump the SSHClientManager.debug_key_attempts entries.

        Marked clearly with DEBUG so you can disable it later.
        """
        if not getattr(self, 'debug_key_logging', False):
            return
        if not hasattr(self, 'ssh_manager'):
            return
        attempts = getattr(self.ssh_manager, 'debug_key_attempts', None)
        if not attempts:
            return
        self.log('--- DEBUG: attempted private key loads ---')
        for entry in attempts:
            # two kinds of entries: per-path summary with 'attempts', or single success
            if 'attempts' in entry:
                self.log(f"DEBUG: path={entry['path']}")
                for a in entry['attempts']:
                    used = 'with-passphrase' if a.get('used_password') else 'no-passphrase'
                    err = a.get('error')
                    if err:
                        self.log(f"DEBUG:   loader={a.get('loader')} {used} -> ERROR: {err}")
                    else:
                        self.log(f"DEBUG:   loader={a.get('loader')} {used} -> OK")
            else:
                used = 'with-passphrase' if entry.get('used_password') else 'no-passphrase'
                res = entry.get('result', 'unknown')
                self.log(f"DEBUG: path={entry.get('path')} loader={entry.get('loader')} {used} -> {res}")
        self.log('--- end DEBUG ---')

    def show_config_panel(self):
        if self.config_dock is None:
            self.config_dock = QDockWidget("Settings", self)
            self.config_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
            config_widget = ConfigPanel()
            self.config_dock.setWidget(config_widget)
            self.addDockWidget(Qt.RightDockWidgetArea, self.config_dock)
        else:
            self.config_dock.show()

    def show_history_panel(self):
        if not hasattr(self, 'history_dock') or self.history_dock is None:
            self.history_dock = QDockWidget("Session & Login History", self)
            self.history_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
            history_widget = HistoryViewer()
            # import db module to pass to history viewer
            try:
                import db.db as db_module
            except Exception:
                from db import db as db_module
            history_widget.set_db_module(db_module)
            self.history_dock.setWidget(history_widget)
            self.addDockWidget(Qt.RightDockWidgetArea, self.history_dock)
        else:
            self.history_dock.show()

    def on_connect(self):
        host = self.host_in.text().strip()
        port = int(self.port_in.text().strip() or 22)
        user = self.user_in.text().strip()
        keypath = self.keypath_in.text().strip() or None

        self.log(f'Attempting to authenticate {user}@{host}:{port}...')

        ok, reason = self.auth.pre_check(user=user, host=host, keypath=keypath)
        if not ok:
            self.log(f'AUTH DENIED: {reason}')
            return

        self.log('Auth OK — opening SSH session...')
        try:
            chan = self.ssh_manager.open_session(host=host, port=port, username=user, key_filename=keypath)
            if chan:
                self.log('SSH session established.')
                # connect SSH channel to terminal for interactive I/O
                self.terminal.set_ssh_channel(chan)
                # wire command logging and close callback so commands are persisted
                try:
                    self.terminal.set_command_logger(self.ssh_manager.log_command)
                    self.terminal.set_close_callback(self.ssh_manager.close)
                except Exception:
                    pass
            else:
                self.log('Failed to obtain interactive channel.')
        except Exception as e:
            err = str(e).lower()
            # Detect encrypted private key error and prompt for passphrase
            if 'encrypted' in err or 'passwordrequiredexception' in err:
                # Prompt user for passphrase (password echo hidden)
                passphrase, ok = QInputDialog.getText(self, 'Private Key Passphrase',
                                                      'Enter passphrase for private key:', QLineEdit.Password)
                if ok and passphrase:
                    try:
                        chan = self.ssh_manager.open_session(host=host, port=port, username=user,
                                                             key_filename=keypath, key_passphrase=passphrase)
                        if chan:
                            self.log('SSH session established (using provided passphrase).')
                            # connect channel and wire logging similarly to non-passphrase flow
                            self.terminal.set_ssh_channel(chan)
                            try:
                                self.terminal.set_command_logger(self.ssh_manager.log_command)
                                self.terminal.set_close_callback(self.ssh_manager.close)
                            except Exception:
                                pass
                        else:
                            self.log('Failed to obtain interactive channel (after passphrase).')
                    except Exception as e2:
                        self.log(f'Connection error after passphrase: {e2}')
                        # dump debug info about key attempts if available
                        self._log_debug_key_attempts()
                        return
                else:
                    self.log('Passphrase not provided; aborting connection.')
                    self._log_debug_key_attempts()
                    return
            self.log(f'Connection error: {e}')
            # dump debug info about key attempts if available
            self._log_debug_key_attempts()

    def on_debug_bypass(self):
        """Deprecated compatibility shim: kept for older wiring."""
        # prefer using on_toggle_debug which controls multiple debug behaviors
        return

    def on_toggle_debug(self):
        """Toggle global debug mode: policy bypass, debug logs, etc."""
        self.debug_mode = not self.debug_mode
        # enable/disable policy bypass on auth
        try:
            # auth exposes debug_bypass attribute
            self.auth.debug_bypass = self.debug_mode
        except Exception:
            # fallback to toggle method if present
            if hasattr(self.auth, 'toggle_debug_bypass'):
                # ensure toggle_debug_bypass results in desired state
                cur = getattr(self.auth, 'debug_bypass', False)
                if cur != self.debug_mode:
                    self.auth.toggle_debug_bypass()

        # enable/disable key-debug logging
        self.debug_key_logging = self.debug_mode

        status = 'ON' if self.debug_mode else 'OFF'
        self.log(f'🐛 DEBUG {status} — bypass={self.debug_mode}, key-logs={self.debug_key_logging}')
        # visual indicator: red when enabled
        self.debug_btn.setStyleSheet('background-color: #ff6b6b;' if self.debug_mode else '')
