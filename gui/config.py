import json
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
    QListWidget, QListWidgetItem, QPushButton, 
    QMessageBox, QHBoxLayout, QComboBox, QInputDialog
)

CONFIG_PATH = Path(__file__).resolve().parent.parent / "policies.json"

class ConfigPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        with open(CONFIG_PATH, "r") as f:
            self.config_data = json.load(f)

        self.layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        # === USER SELECTION ===
        self.user_select = QComboBox()
        self.user_select.addItems(self.config_data["users"].keys())
        self.user_select.currentTextChanged.connect(self.load_user_data)
        self.form_layout.addRow("Select User:", self.user_select)

        # Buttons beside selector
        user_btn_layout = QHBoxLayout()
        add_user_btn = QPushButton("➕ Add User")
        del_user_btn = QPushButton("🗑️ Delete User")
        add_user_btn.clicked.connect(self.add_user)
        del_user_btn.clicked.connect(self.delete_user)
        user_btn_layout.addWidget(add_user_btn)
        user_btn_layout.addWidget(del_user_btn)
        self.layout.addLayout(user_btn_layout)

        # === USER DATA FIELDS ===
        self.user_field = QLineEdit()
        self.form_layout.addRow("Username:", self.user_field)

        self.allowed_hosts_list = QListWidget()
        self.form_layout.addRow("Allowed Hosts:", self.allowed_hosts_list)

        self.blocked_commands_list = QListWidget()
        self.form_layout.addRow("Blocked Commands:", self.blocked_commands_list)

        self.layout.addLayout(self.form_layout)

        # === SAVE BUTTON ===
        save_btn = QPushButton("💾 Save Config")
        save_btn.clicked.connect(self.save_config)
        self.layout.addWidget(save_btn)

        self.setLayout(self.layout)

        # Load initial user
        self.load_user_data(self.user_select.currentText())

    def load_user_data(self, username):
        self.current_user = username
        user_data = self.config_data["users"].get(username, {})

        self.user_field.setText(username)

        # Load allowed hosts
        self.allowed_hosts_list.clear()
        for host in user_data.get("allowed_hosts", []):
            self.allowed_hosts_list.addItem(QListWidgetItem(host))

        # Load blocked commands
        self.blocked_commands_list.clear()
        for cmd in user_data.get("blocked_commands", []):
            self.blocked_commands_list.addItem(QListWidgetItem(cmd))

    def add_user(self):
        username, ok = QInputDialog.getText(self, "Add User", "Enter new username:")
        if ok and username.strip():
            username = username.strip()
            if username in self.config_data["users"]:
                QMessageBox.warning(self, "Error", "User already exists!")
                return

            self.config_data["users"][username] = {
                "allowed_hosts": [],
                "blocked_commands": []
            }
            self.user_select.addItem(username)
            self.user_select.setCurrentText(username)

    def delete_user(self):
        user = self.user_select.currentText()
        if QMessageBox.question(
            self, "Confirm Delete", f"Delete user '{user}'?"
        ) == QMessageBox.Yes:
            self.config_data["users"].pop(user, None)
            self.user_select.removeItem(self.user_select.currentIndex())

            if self.user_select.count() > 0:
                self.user_select.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "No Users", "All users deleted. Add a new one.")
                self.add_user()

    def save_config(self):
        username = self.user_field.text().strip()
        if username != self.current_user:
            # Rename key
            self.config_data["users"][username] = self.config_data["users"].pop(self.current_user)
            self.current_user = username
            self.user_select.setItemText(self.user_select.currentIndex(), username)

        allowed_hosts = [self.allowed_hosts_list.item(i).text() for i in range(self.allowed_hosts_list.count())]
        blocked_cmds = [self.blocked_commands_list.item(i).text() for i in range(self.blocked_commands_list.count())]

        self.config_data["users"][username]["allowed_hosts"] = allowed_hosts
        self.config_data["users"][username]["blocked_commands"] = blocked_cmds

        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config_data, f, indent=2)

        QMessageBox.information(self, "Saved", "Config updated successfully!")