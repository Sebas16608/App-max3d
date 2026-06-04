from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QStatusBar, QLabel
from PySide6.QtCore import Qt
from app.widgets.sidebar import Sidebar
from app.pages.dashboard import DashboardPage
from app.pages.clients import ClientsPage
from app.pages.catalog import CatalogPage
from app.pages.orders import OrdersPage
from app.pages.inventory import InventoryPage
from app.pages.finances import FinancesPage
from app.pages.goals import GoalsPage
from app.pages.reports import ReportsPage
from app.pages.settings import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self, db, config):
        super().__init__()
        self.db = db
        self.config = config
        self.setWindowTitle("Max3D Creations Manager")
        self.setMinimumSize(1200, 750)
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack, 1)

        self.pages = [
            DashboardPage(self.db, self.config),
            ClientsPage(self.db, self.config),
            CatalogPage(self.db, self.config),
            OrdersPage(self.db, self.config),
            InventoryPage(self.db, self.config),
            FinancesPage(self.db, self.config),
            GoalsPage(self.db, self.config),
            ReportsPage(self.db, self.config),
            SettingsPage(self.db, self.config),
        ]

        for page in self.pages:
            self.stack.addWidget(page)

        self.sidebar.page_changed.connect(self.on_page_changed)

        self.status = QStatusBar()
        self.status.setStyleSheet("background-color: #16213e; color: #a0a0b0; border-top: 1px solid #0f3460;")
        self.status_label = QLabel("Listo")
        self.status.addWidget(self.status_label)
        self.setStatusBar(self.status)

    def on_page_changed(self, index):
        self.stack.setCurrentIndex(index)
        if hasattr(self.pages[index], "refresh"):
            self.pages[index].refresh()
        page_names = [
            "Dashboard", "Clientes", "Catálogo", "Pedidos",
            "Inventario", "Finanzas", "Metas", "Reportes", "Configuración"
        ]
        if index < len(page_names):
            self.status_label.setText(f"{page_names[index]}")

    def refresh_all(self):
        for page in self.pages:
            if hasattr(page, "refresh"):
                page.refresh()
