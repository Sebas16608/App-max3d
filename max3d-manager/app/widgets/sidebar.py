from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SidebarButton(QPushButton):
    def __init__(self, text, icon_text="", parent=None):
        super().__init__(parent)
        self.setText(f"  {icon_text}  {text}" if icon_text else text)
        self.setFixedHeight(54)
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #a0a0b0;
                border: none;
                border-radius: 10px;
                text-align: left;
                padding-left: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #0f3460;
                color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #533483;
                color: #ffffff;
            }
        """)


class Sidebar(QWidget):
    page_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self.setStyleSheet("background-color: #16213e; border-right: 2px solid #0f3460;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 16)
        layout.setSpacing(4)

        title = QLabel("Max3D Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e94560; padding: 8px 12px;")
        layout.addWidget(title)

        subtitle = QLabel("Impresión 3D ERP")
        subtitle.setStyleSheet("font-size: 12px; color: #a0a0b0; padding: 0 12px 16px 12px;")
        layout.addWidget(subtitle)

        self.buttons = []
        pages = [
            (0, "📊", "Dashboard"),
            (1, "👥", "Clientes"),
            (2, "📦", "Catálogo"),
            (3, "🛒", "Pedidos"),
            (4, "📋", "Inventario"),
            (5, "💰", "Finanzas"),
            (6, "🎯", "Metas"),
            (7, "📈", "Reportes"),
            (8, "⚙️", "Configuración"),
        ]

        for idx, icon, text in pages:
            btn = SidebarButton(text, icon)
            btn.clicked.connect(lambda checked, i=idx: self.on_page_clicked(i))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        version = QLabel("v1.0.0")
        version.setStyleSheet("font-size: 11px; color: #555; padding: 8px 12px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        self.buttons[0].setChecked(True)

    def on_page_clicked(self, index):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)
        self.page_changed.emit(index)
