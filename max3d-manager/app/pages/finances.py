from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDoubleSpinBox, QMessageBox,
    QHeaderView, QGroupBox, QGridLayout, QFrame, QDateEdit,
    QTabWidget
)
from PySide6.QtCore import Qt, QDate
from app.utils import formatear_moneda


class InvestmentDialog(QDialog):
    def __init__(self, db, item=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.item = item
        self.setWindowTitle("Inversión" if not item else "Editar Inversión")
        self.setMinimumSize(450, 300)
        self.setup_ui()
        if item:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.fecha = QDateEdit()
        self.fecha.setCalendarPopup(True)
        self.fecha.setDate(QDate.currentDate())
        form.addRow("Fecha:", self.fecha)

        self.categoria = QComboBox()
        categorias = ["Filamento", "Pintura", "Herramientas", "Impresora", "Repuestos",
                      "Publicidad", "Hosting", "Dominio", "Envíos", "Otros"]
        self.categoria.addItems(categorias)
        form.addRow("Categoría:", self.categoria)

        self.descripcion = QLineEdit()
        self.descripcion.setPlaceholderText("Descripción del gasto")
        form.addRow("Descripción:", self.descripcion)

        self.monto = QDoubleSpinBox()
        self.monto.setRange(0, 999999)
        self.monto.setPrefix("Q ")
        self.monto.setDecimals(2)
        form.addRow("Monto:", self.monto)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardar)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)

    def load_data(self):
        if self.item["fecha"]:
            self.fecha.setDate(QDate.fromString(self.item["fecha"], "yyyy-MM-dd"))
        idx = self.categoria.findText(self.item["categoria"])
        if idx >= 0:
            self.categoria.setCurrentIndex(idx)
        self.descripcion.setText(self.item["descripcion"] or "")
        self.monto.setValue(self.item["monto"] or 0)

    def guardar(self):
        if not self.descripcion.text().strip():
            QMessageBox.warning(self, "Error", "La descripción es obligatoria")
            return
        if self.monto.value() <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0")
            return
        data = {
            "fecha": self.fecha.date().toString("yyyy-MM-dd"),
            "categoria": self.categoria.currentText(),
            "descripcion": self.descripcion.text().strip(),
            "monto": self.monto.value(),
        }
        if self.item:
            self.db.update("inversiones", data, "id=?", [self.item["id"]])
        else:
            self.db.insert("inversiones", data)
        self.accept()


class FinancesPage(QWidget):
    def __init__(self, db, config, parent=None):
        super().__init__(parent)
        self.db = db
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Finanzas e Inversiones")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e94560;")
        layout.addWidget(title)

        resumen_group = QGroupBox("Resumen Financiero")
        resumen_grid = QGridLayout(resumen_group)
        resumen_grid.setSpacing(12)

        indicadores = [
            ("Ventas totales", "ventas_totales", "#00c853"),
            ("Gastos totales", "gastos_totales", "#e94560"),
            ("Ganancia bruta", "ganancia_bruta", "#00bcd4"),
            ("Ganancia neta", "ganancia_neta", "#00c853"),
            ("Dinero invertido", "invertido", "#ff8c00"),
            ("Dinero recuperado", "recuperado", "#533483"),
            ("Pendiente recuperar", "pendiente", "#e040fb"),
            ("ROI", "roi", "#7c4dff"),
        ]

        self.card_widgets = {}
        for i, (label, key, color) in enumerate(indicadores):
            card = QFrame()
            card.setStyleSheet(f"background-color: #16213e; border: 1px solid #0f3460; border-radius: 10px; padding: 16px; border-left: 4px solid {color};")
            cl = QVBoxLayout(card)
            cl.setSpacing(4)
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 13px; color: #a0a0b0; border: none;")
            cl.addWidget(lbl)
            val = QLabel("—")
            val.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color}; border: none;")
            cl.addWidget(val)
            resumen_grid.addWidget(card, i // 4, i % 4)
            self.card_widgets[key] = val

        layout.addWidget(resumen_group)

        tabs = QTabWidget()

        inv_tab = QWidget()
        inv_layout = QVBoxLayout(inv_tab)
        inv_header = QHBoxLayout()
        inv_header.addStretch()
        btn_add_inv = QPushButton("+ Nueva Inversión")
        btn_add_inv.clicked.connect(self.add_inversion)
        inv_header.addWidget(btn_add_inv)
        inv_layout.addLayout(inv_header)

        self.inv_table = QTableWidget()
        self.inv_table.setColumnCount(5)
        self.inv_table.setHorizontalHeaderLabels(["ID", "Fecha", "Categoría", "Descripción", "Monto"])
        self.inv_table.horizontalHeader().setStretchLastSection(True)
        self.inv_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.inv_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.inv_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.inv_table.verticalHeader().setVisible(False)
        inv_layout.addWidget(self.inv_table)
        tabs.addTab(inv_tab, "Inversiones")

        layout.addWidget(tabs)

    def refresh(self):
        self.refresh_resumen()
        self.refresh_inversiones()

    def refresh_resumen(self):
        db = self.db

        ventas = db.fetch_one(
            "SELECT COALESCE(SUM(precio_final),0) as total FROM clientes_productos WHERE estado='Entregado'"
        )
        ventas_total = ventas["total"] if ventas else 0

        gastos = db.fetch_one("SELECT COALESCE(SUM(monto),0) as total FROM inversiones")
        gastos_total = gastos["total"] if gastos else 0

        costos = db.fetch_one(
            "SELECT COALESCE(SUM(costo_total),0) as total FROM clientes_productos WHERE estado='Entregado'"
        )
        costos_total = costos["total"] if costos else 0

        ganancia_bruta = ventas_total - costos_total
        ganancia_neta = ganancia_bruta - gastos_total

        pendiente = db.fetch_one(
            "SELECT COALESCE(SUM(precio_final - pago_total),0) as total FROM clientes_productos WHERE estado != 'Cancelado'"
        )
        pendiente_total = pendiente["total"] if pendiente else 0

        roi = ((ganancia_neta / gastos_total) * 100) if gastos_total > 0 else 0

        moneda = self.config.get("moneda", "Q")
        self.card_widgets["ventas_totales"].setText(formatear_moneda(ventas_total, moneda))
        self.card_widgets["gastos_totales"].setText(formatear_moneda(gastos_total, moneda))
        self.card_widgets["ganancia_bruta"].setText(formatear_moneda(ganancia_bruta, moneda))
        self.card_widgets["ganancia_neta"].setText(formatear_moneda(ganancia_neta, moneda))
        self.card_widgets["invertido"].setText(formatear_moneda(gastos_total, moneda))
        self.card_widgets["recuperado"].setText(formatear_moneda(ganancia_neta if ganancia_neta > 0 else 0, moneda))
        self.card_widgets["pendiente"].setText(formatear_moneda(pendiente_total, moneda))
        self.card_widgets["roi"].setText(f"{roi:.1f}%")

    def refresh_inversiones(self):
        items = self.db.fetch_all("SELECT * FROM inversiones ORDER BY fecha DESC")
        self.inv_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.inv_table.setItem(i, 0, QTableWidgetItem(str(item["id"])))
            self.inv_table.setItem(i, 1, QTableWidgetItem(item["fecha"] or ""))
            self.inv_table.setItem(i, 2, QTableWidgetItem(item["categoria"]))
            self.inv_table.setItem(i, 3, QTableWidgetItem(item["descripcion"] or ""))
            self.inv_table.setItem(i, 4, QTableWidgetItem(f"Q{item['monto']:.2f}"))

        self.inv_table.setColumnHidden(0, True)

    def add_inversion(self):
        dialog = InvestmentDialog(self.db)
        if dialog.exec():
            self.refresh()

    def edit_inversion(self, iid):
        item = self.db.fetch_one("SELECT * FROM inversiones WHERE id=?", [iid])
        if item:
            dialog = InvestmentDialog(self.db, item)
            if dialog.exec():
                self.refresh()

    def delete_inversion(self, iid):
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar esta inversión?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete("inversiones", "id=?", [iid])
            self.refresh()
