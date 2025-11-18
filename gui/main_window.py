from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QDockWidget
)
from PySide6.QtCore import Qt
from backend.ssh_client import SSHClientManager
from backend.auth import ZeroTrustAuth
from gui.config import ConfigPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zero Trust SSH Client (Prototype)')
        self.resize(800, 600)

        self.config_dock = None  # dock reference

        self._build_ui()

        self.log('Welcome to Zero Trust SSH Client. Enter host, username, and port to start connecting.')
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
        self.log_btn = QPushButton('Log')

        self.connect_btn.clicked.connect(self.on_connect)
        self.config_btn.clicked.connect(self.show_config_panel)

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
        form.addWidget(self.log_btn)

        layout.addLayout(form)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        layout.addWidget(self.terminal)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)  # IMPORTANT!

    def log(self, text: str):
        self.terminal.append(text)

    def show_config_panel(self):
        if self.config_dock is None:
            self.config_dock = QDockWidget("Settings", self)
            self.config_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
            config_widget = ConfigPanel()
            self.config_dock.setWidget(config_widget)
            self.addDockWidget(Qt.RightDockWidgetArea, self.config_dock)
        else:
            self.config_dock.show()

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
            else:
                self.log('Failed to obtain interactive channel.')
        except Exception as e:
            self.log(f'Connection error: {e}')
