from PySide6.QtWidgets import (
QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
)
from PySide6.QtCore import Qt
# from app.backend.ssh_client import SSHClientManager
# from app.backend.auth import ZeroTrustAuth


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Zero Trust SSH Client (Prototype)')
        self.resize(800, 600)
        self._build_ui()
        self.log(f'Welcome to Zero Trust SSH Client. Enter host, username, and port to start connecting.')
        # self.ssh_manager = SSHClientManager()
        # self.auth = ZeroTrustAuth()


    def _build_ui(self):
        layout = QVBoxLayout()
        form = QHBoxLayout()
        self.host_in = QLineEdit()
        self.host_in.setPlaceholderText('host (e.g. 192.168.1.100)')
        self.port_in = QLineEdit()
        self.port_in.setPlaceholderText('port (2222)')
        self.port_in.setFixedWidth(80)
        self.user_in = QLineEdit()
        self.user_in.setPlaceholderText('username')
        self.keypath_in = QLineEdit()
        self.keypath_in.setPlaceholderText('path to private key (optional)')
        self.connect_btn = QPushButton('Connect')
        self.config_btn = QPushButton('Config')
        self.log_btn = QPushButton('Log')
        self.connect_btn.clicked.connect(self.on_connect)
        # self.config_btn.clicked.connect(self.on_connect)
        # self.log_btn.clicked.connect(self.on_connect)

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


        self.setLayout(layout)


    def log(self, text: str):
        self.terminal.append(text)

    def on_connect(self):
        host = self.host_in.text().strip()
        port = int(self.port_in.text().strip() or 22)
        user = self.user_in.text().strip()
        keypath = self.keypath_in.text().strip() or None

        if host is None or user is None:
            self.log(f'Host and user is required.')
        else:
            self.log(f'Attempting to authenticate {user}@{host}:{port}...')