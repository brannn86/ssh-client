import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    # Initialize the database before starting the UI
    try:
        from db.db import init_db
        init_db()
    except Exception:
        pass
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()