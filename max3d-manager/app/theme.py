from PySide6.QtGui import QPalette, QColor, QFont


DARK_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
}

QMenuBar {
    background-color: #16213e;
    color: #e0e0e0;
    border-bottom: 1px solid #0f3460;
}

QMenuBar::item:selected {
    background-color: #0f3460;
}

QMenu {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
}

QMenu::item:selected {
    background-color: #0f3460;
}

QPushButton {
    background-color: #0f3460;
    color: #e0e0e0;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #1a4a8a;
}

QPushButton:pressed {
    background-color: #0a2540;
}

QPushButton#danger {
    background-color: #8b0000;
}

QPushButton#danger:hover {
    background-color: #a00000;
}

QPushButton#success {
    background-color: #006400;
}

QPushButton#success:hover {
    background-color: #008000;
}

QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border-color: #533483;
}

QComboBox::drop-down {
    border: none;
    background-color: #0f3460;
    border-radius: 0 6px 6px 0;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    selection-background-color: #0f3460;
}

QTableWidget, QTableView {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 6px;
    gridline-color: #0f3460;
    selection-background-color: #533483;
}

QTableWidget::item, QTableView::item {
    padding: 6px;
}

QHeaderView::section {
    background-color: #0f3460;
    color: #e0e0e0;
    padding: 8px;
    border: none;
    border-right: 1px solid #1a1a2e;
    border-bottom: 1px solid #1a1a2e;
    font-weight: bold;
}

QLabel {
    color: #e0e0e0;
}

QLabel#title {
    font-size: 24px;
    font-weight: bold;
    color: #e94560;
}

QLabel#subtitle {
    font-size: 14px;
    color: #a0a0b0;
}

QLabel#card-title {
    font-size: 14px;
    font-weight: bold;
    color: #e0e0e0;
}

QLabel#card-value {
    font-size: 28px;
    font-weight: bold;
    color: #e94560;
}

QLabel#card-label {
    font-size: 12px;
    color: #a0a0b0;
}

QGroupBox {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px;
    font-weight: bold;
    color: #e0e0e0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

QScrollBar:vertical {
    background-color: #1a1a2e;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #0f3460;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #533483;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #1a1a2e;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #0f3460;
    border-radius: 5px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #533483;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QTabWidget::pane {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #1a1a2e;
    color: #a0a0b0;
    padding: 8px 16px;
    border: none;
    margin-right: 2px;
    border-radius: 6px 6px 0 0;
}

QTabBar::tab:selected {
    background-color: #0f3460;
    color: #e0e0e0;
}

QTabBar::tab:hover {
    background-color: #16213e;
}

QCheckBox, QRadioButton {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 18px;
    height: 18px;
}

QDateEdit, QDateTimeEdit {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 6px;
    padding: 6px 10px;
}

QProgressBar {
    background-color: #16213e;
    border: 1px solid #0f3460;
    border-radius: 6px;
    text-align: center;
    color: #e0e0e0;
    height: 22px;
}

QProgressBar::chunk {
    background-color: #e94560;
    border-radius: 5px;
}
"""


def apply_dark_theme(app):
    app.setStyleSheet(DARK_STYLESHEET)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 26, 46))
    palette.setColor(QPalette.WindowText, QColor(224, 224, 224))
    palette.setColor(QPalette.Base, QColor(22, 33, 62))
    palette.setColor(QPalette.AlternateBase, QColor(26, 26, 46))
    palette.setColor(QPalette.ToolTipBase, QColor(15, 52, 96))
    palette.setColor(QPalette.ToolTipText, QColor(224, 224, 224))
    palette.setColor(QPalette.Text, QColor(224, 224, 224))
    palette.setColor(QPalette.Button, QColor(15, 52, 96))
    palette.setColor(QPalette.ButtonText, QColor(224, 224, 224))
    palette.setColor(QPalette.BrightText, QColor(233, 69, 96))
    palette.setColor(QPalette.Highlight, QColor(83, 52, 131))
    palette.setColor(QPalette.HighlightedText, QColor(224, 224, 224))
    app.setPalette(palette)
