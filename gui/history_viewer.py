"""History viewer panel for sessions, commands, and login attempts."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QTabWidget, QHeaderView, QComboBox
)
from PySide6.QtCore import Qt
from datetime import datetime


class HistoryViewer(QWidget):
    """Panel to view and search session/command history and login attempts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_module = None  # will be set by parent
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        
        # Tab 1: Login Attempts
        self.login_attempts_tab = self._build_login_attempts_tab()
        self.tabs.addTab(self.login_attempts_tab, "Login Attempts")
        
        # Tab 2: Sessions
        self.sessions_tab = self._build_sessions_tab()
        self.tabs.addTab(self.sessions_tab, "Sessions")
        
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def _build_login_attempts_tab(self):
        """Build the login attempts history view."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Filter/Search bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by status:"))
        self.login_status_filter = QComboBox()
        self.login_status_filter.addItems(["All", "success", "failed"])
        self.login_status_filter.currentTextChanged.connect(self._refresh_login_attempts)
        filter_layout.addWidget(self.login_status_filter)
        
        search_label = QLabel("Search user/host:")
        search_input = QLineEdit()
        search_input.setPlaceholderText("e.g., root@192.168.1.1")
        self.login_search_input = search_input
        search_input.textChanged.connect(self._refresh_login_attempts)
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(search_input)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_login_attempts)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Table
        self.login_table = QTableWidget()
        self.login_table.setColumnCount(7)
        self.login_table.setHorizontalHeaderLabels(
            ["ID", "User", "Host", "Port", "Timestamp", "Status", "Reason"]
        )
        # adjust column widths
        header = self.login_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.login_table.setColumnWidth(0, 40)
        self.login_table.setColumnWidth(3, 50)
        self.login_table.setColumnWidth(5, 80)
        layout.addWidget(self.login_table)
        
        widget.setLayout(layout)
        return widget

    def _build_sessions_tab(self):
        """Build the sessions history view."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Filter/Search bar
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by status:"))
        self.session_status_filter = QComboBox()
        self.session_status_filter.addItems(["All", "active", "closed", "failed"])
        self.session_status_filter.currentTextChanged.connect(self._refresh_sessions)
        filter_layout.addWidget(self.session_status_filter)
        
        search_label = QLabel("Search user/host:")
        search_input = QLineEdit()
        search_input.setPlaceholderText("e.g., root@192.168.1.1")
        self.session_search_input = search_input
        search_input.textChanged.connect(self._refresh_sessions)
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(search_input)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_sessions)
        filter_layout.addWidget(refresh_btn)
        
        layout.addLayout(filter_layout)
        
        # Sessions table
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels(
            ["ID", "User", "Host", "Start Time", "End Time", "Status"]
        )
        header = self.sessions_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.sessions_table.setColumnWidth(0, 40)
        self.sessions_table.itemSelectionChanged.connect(self._on_session_selected)
        layout.addWidget(self.sessions_table)
        
        # Events/commands for selected session
        layout.addWidget(QLabel("Commands/Events for selected session:"))
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(3)
        self.events_table.setHorizontalHeaderLabels(["Event ID", "Timestamp", "Event"])
        header = self.events_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.events_table.setColumnWidth(0, 50)
        layout.addWidget(self.events_table)
        
        widget.setLayout(layout)
        return widget

    def set_db_module(self, db_module):
        """Set the DB module reference for data loading."""
        self.db_module = db_module
        self._refresh_login_attempts()
        self._refresh_sessions()

    def _refresh_login_attempts(self):
        """Load and display login attempts from DB."""
        if not self.db_module:
            return
        
        try:
            attempts = self.db_module.get_recent_login_attempts(limit=200)
        except Exception:
            return
        
        # Apply filters
        status_filter = self.login_status_filter.currentText()
        search_text = self.login_search_input.text().lower()
        
        filtered = []
        for attempt in attempts:
            # attempt: (id, user, host, port, timestamp, status, reason)
            if status_filter != "All" and attempt[5] != status_filter:
                continue
            if search_text:
                if search_text not in f"{attempt[1]}@{attempt[2]}".lower():
                    continue
            filtered.append(attempt)
        
        # Populate table
        self.login_table.setRowCount(len(filtered))
        for row, attempt in enumerate(filtered):
            aid, user, host, port, ts, status, reason = attempt
            self.login_table.setItem(row, 0, QTableWidgetItem(str(aid)))
            self.login_table.setItem(row, 1, QTableWidgetItem(user or ""))
            self.login_table.setItem(row, 2, QTableWidgetItem(host or ""))
            self.login_table.setItem(row, 3, QTableWidgetItem(str(port)))
            self.login_table.setItem(row, 4, QTableWidgetItem(self._format_timestamp(ts)))
            
            # Color code status
            status_item = QTableWidgetItem(status or "")
            if status == "success":
                status_item.setBackground(self._color_success())
            elif status == "failed":
                status_item.setBackground(self._color_failed())
            self.login_table.setItem(row, 5, status_item)
            
            self.login_table.setItem(row, 6, QTableWidgetItem(reason or ""))

    def _refresh_sessions(self):
        """Load and display sessions from DB."""
        if not self.db_module:
            return
        
        try:
            sessions = self.db_module.get_recent_sessions(limit=100)
        except Exception:
            return
        
        # Apply filters
        status_filter = self.session_status_filter.currentText()
        search_text = self.session_search_input.text().lower()
        
        filtered = []
        for session in sessions:
            # session: (id, user, host, start_time, end_time, status)
            if status_filter != "All" and session[5] != status_filter:
                continue
            if search_text:
                if search_text not in f"{session[1]}@{session[2]}".lower():
                    continue
            filtered.append(session)
        
        # Populate table
        self.sessions_table.setRowCount(len(filtered))
        for row, session in enumerate(filtered):
            sid, user, host, start_ts, end_ts, status = session
            self.sessions_table.setItem(row, 0, QTableWidgetItem(str(sid)))
            self.sessions_table.setItem(row, 1, QTableWidgetItem(user or ""))
            self.sessions_table.setItem(row, 2, QTableWidgetItem(host or ""))
            self.sessions_table.setItem(row, 3, QTableWidgetItem(self._format_timestamp(start_ts)))
            self.sessions_table.setItem(row, 4, QTableWidgetItem(self._format_timestamp(end_ts) if end_ts else ""))
            
            # Color code status
            status_item = QTableWidgetItem(status or "")
            if status == "active":
                status_item.setBackground(self._color_active())
            elif status == "closed":
                status_item.setBackground(self._color_closed())
            elif status == "failed":
                status_item.setBackground(self._color_failed())
            self.sessions_table.setItem(row, 5, status_item)
        
        # Clear events table
        self.events_table.setRowCount(0)

    def _on_session_selected(self):
        """When a session is selected, load its events."""
        if not self.db_module:
            return
        
        selected_rows = self.sessions_table.selectedIndexes()
        if not selected_rows:
            self.events_table.setRowCount(0)
            return
        
        row = selected_rows[0].row()
        sid_item = self.sessions_table.item(row, 0)
        if not sid_item:
            return
        
        try:
            session_id = int(sid_item.text())
            events = self.db_module.get_events_for_session(session_id)
        except Exception:
            return
        
        # Populate events table
        self.events_table.setRowCount(len(events))
        for row, event in enumerate(events):
            # event: (id, timestamp, event_text)
            eid, ts, event_text = event
            self.events_table.setItem(row, 0, QTableWidgetItem(str(eid)))
            self.events_table.setItem(row, 1, QTableWidgetItem(self._format_timestamp(ts)))
            self.events_table.setItem(row, 2, QTableWidgetItem(event_text or ""))

    def _format_timestamp(self, ts):
        """Format ISO timestamp to readable format."""
        if not ts:
            return ""
        try:
            dt = datetime.fromisoformat(ts)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return ts

    def _color_success(self):
        """Return a green color for successful status."""
        from PySide6.QtGui import QColor
        return QColor(144, 238, 144)  # light green

    def _color_failed(self):
        """Return a red color for failed status."""
        from PySide6.QtGui import QColor
        return QColor(255, 160, 160)  # light red

    def _color_active(self):
        """Return a blue color for active status."""
        from PySide6.QtGui import QColor
        return QColor(173, 216, 230)  # light blue

    def _color_closed(self):
        """Return a gray color for closed status."""
        from PySide6.QtGui import QColor
        return QColor(211, 211, 211)  # light gray
