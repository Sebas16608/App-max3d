#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.database import Database
from app.config import Config
from app.theme import apply_dark_theme
from app.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Max3D Creations Manager")
    app.setOrganizationName("Max3D")

    config = Config()
    db = Database(config.db_path)

    apply_dark_theme(app)

    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow(db, config)
    window.show()

    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
