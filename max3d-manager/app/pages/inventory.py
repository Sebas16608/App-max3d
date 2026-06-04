from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDoubleSpinBox, QMessageBox,
    QHeaderView, QTabWidget, QTextEdit
)
from PySide6.QtCore import Qt
from app.utils import formatear_moneda


class FilamentoDialog(QDialog):
    def __init__(self, db, item=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.item = item
        self.setWindowTitle("Filamento" if not item else "Editar Filamento")
        self.setMinimumSize(400, 350)
        self.setup_ui()
        if item:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Ej: PLA Negro")
        form.addRow("Nombre:", self.nombre)

        self.marca = QLineEdit()
        self.marca.setPlaceholderText("Marca")
        form.addRow("Marca:", self.marca)

        self.tipo = QLineEdit()
        self.tipo.setPlaceholderText("Ej: PLA, PETG, TPU")
        form.addRow("Tipo:", self.tipo)

        self.color = QLineEdit()
        self.color.setPlaceholderText("Color")
        form.addRow("Color:", self.color)

        self.peso = QDoubleSpinBox()
        self.peso.setRange(0, 99999)
        self.peso.setSuffix(" g")
        self.peso.setDecimals(1)
        form.addRow("Peso disponible:", self.peso)

        self.precio = QDoubleSpinBox()
        self.precio.setRange(0, 99999)
        self.precio.setPrefix("Q ")
        self.precio.setDecimals(2)
        form.addRow("Precio compra:", self.precio)

        self.precio_gramo = QDoubleSpinBox()
        self.precio_gramo.setRange(0, 999)
        self.precio_gramo.setPrefix("Q ")
        self.precio_gramo.setDecimals(4)
        self.precio_gramo.setSingleStep(0.01)
        form.addRow("Precio por gramo:", self.precio_gramo)

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
        self.nombre.setText(self.item["nombre"])
        self.marca.setText(self.item["marca"] or "")
        self.tipo.setText(self.item["tipo"] or "")
        self.color.setText(self.item["color"] or "")
        self.peso.setValue(self.item["peso_disponible"] or 0)
        self.precio.setValue(self.item["precio_compra"] or 0)
        self.precio_gramo.setValue(self.item["precio_por_gramo"] or 0)

    def guardar(self):
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        data = {
            "nombre": self.nombre.text().strip(),
            "marca": self.marca.text().strip(),
            "tipo": self.tipo.text().strip(),
            "color": self.color.text().strip(),
            "peso_disponible": self.peso.value(),
            "precio_compra": self.precio.value(),
            "precio_por_gramo": self.precio_gramo.value(),
        }
        if self.item:
            self.db.update("filamentos", data, "id=?", [self.item["id"]])
        else:
            self.db.insert("filamentos", data)
        self.accept()


class PinturaDialog(QDialog):
    def __init__(self, db, item=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.item = item
        self.setWindowTitle("Pintura" if not item else "Editar Pintura")
        self.setMinimumSize(400, 300)
        self.setup_ui()
        if item:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.marca = QLineEdit()
        self.marca.setPlaceholderText("Marca")
        form.addRow("Marca:", self.marca)

        self.tipo = QLineEdit()
        self.tipo.setPlaceholderText("Tipo")
        form.addRow("Tipo:", self.tipo)

        self.color = QLineEdit()
        self.color.setPlaceholderText("Color")
        form.addRow("Color:", self.color)

        self.cantidad = QDoubleSpinBox()
        self.cantidad.setRange(0, 99999)
        self.cantidad.setDecimals(1)
        form.addRow("Cantidad:", self.cantidad)

        self.precio = QDoubleSpinBox()
        self.precio.setRange(0, 99999)
        self.precio.setPrefix("Q ")
        self.precio.setDecimals(2)
        form.addRow("Precio compra:", self.precio)

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
        self.marca.setText(self.item["marca"] or "")
        self.tipo.setText(self.item["tipo"] or "")
        self.color.setText(self.item["color"] or "")
        self.cantidad.setValue(self.item["cantidad_disponible"] or 0)
        self.precio.setValue(self.item["precio_compra"] or 0)

    def guardar(self):
        data = {
            "marca": self.marca.text().strip(),
            "tipo": self.tipo.text().strip(),
            "color": self.color.text().strip(),
            "cantidad_disponible": self.cantidad.value(),
            "precio_compra": self.precio.value(),
        }
        if self.item:
            self.db.update("pinturas", data, "id=?", [self.item["id"]])
        else:
            self.db.insert("pinturas", data)
        self.accept()


class OtroMaterialDialog(QDialog):
    def __init__(self, db, item=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.item = item
        self.setWindowTitle("Otro Material" if not item else "Editar Material")
        self.setMinimumSize(400, 250)
        self.setup_ui()
        if item:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre del material")
        form.addRow("Nombre:", self.nombre)

        self.cantidad = QDoubleSpinBox()
        self.cantidad.setRange(0, 99999)
        self.cantidad.setDecimals(1)
        form.addRow("Cantidad:", self.cantidad)

        self.costo = QDoubleSpinBox()
        self.costo.setRange(0, 99999)
        self.costo.setPrefix("Q ")
        self.costo.setDecimals(2)
        form.addRow("Costo:", self.costo)

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
        self.nombre.setText(self.item["nombre"])
        self.cantidad.setValue(self.item["cantidad"] or 0)
        self.costo.setValue(self.item["costo"] or 0)

    def guardar(self):
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        data = {
            "nombre": self.nombre.text().strip(),
            "cantidad": self.cantidad.value(),
            "costo": self.costo.value(),
        }
        if self.item:
            self.db.update("otros_materiales", data, "id=?", [self.item["id"]])
        else:
            self.db.insert("otros_materiales", data)
        self.accept()


class InventoryPage(QWidget):
    def __init__(self, db, config, parent=None):
        super().__init__(parent)
        self.db = db
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Inventario")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e94560;")
        layout.addWidget(title)

        tabs = QTabWidget()

        fil_tab = QWidget()
        fil_layout = QVBoxLayout(fil_tab)
        fil_header = QHBoxLayout()
        fil_header.addStretch()
        btn_add_fil = QPushButton("+ Filamento")
        btn_add_fil.clicked.connect(self.add_filamento)
        fil_header.addWidget(btn_add_fil)
        fil_layout.addLayout(fil_header)

        self.fil_table = QTableWidget()
        self.fil_table.setColumnCount(7)
        self.fil_table.setHorizontalHeaderLabels(["ID", "Nombre", "Marca", "Tipo", "Color", "Peso disp.", "Acciones"])
        self.fil_table.horizontalHeader().setStretchLastSection(True)
        self.fil_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.fil_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.fil_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.fil_table.verticalHeader().setVisible(False)
        fil_layout.addWidget(self.fil_table)
        tabs.addTab(fil_tab, "Filamentos")

        pin_tab = QWidget()
        pin_layout = QVBoxLayout(pin_tab)
        pin_header = QHBoxLayout()
        pin_header.addStretch()
        btn_add_pin = QPushButton("+ Pintura")
        btn_add_pin.clicked.connect(self.add_pintura)
        pin_header.addWidget(btn_add_pin)
        pin_layout.addLayout(pin_header)

        self.pin_table = QTableWidget()
        self.pin_table.setColumnCount(6)
        self.pin_table.setHorizontalHeaderLabels(["ID", "Marca", "Tipo", "Color", "Cantidad", "Acciones"])
        self.pin_table.horizontalHeader().setStretchLastSection(True)
        self.pin_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.pin_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.pin_table.verticalHeader().setVisible(False)
        pin_layout.addWidget(self.pin_table)
        tabs.addTab(pin_tab, "Pinturas")

        otro_tab = QWidget()
        otro_layout = QVBoxLayout(otro_tab)
        otro_header = QHBoxLayout()
        otro_header.addStretch()
        btn_add_otro = QPushButton("+ Material")
        btn_add_otro.clicked.connect(self.add_otro)
        otro_header.addWidget(btn_add_otro)
        otro_layout.addLayout(otro_header)

        self.otro_table = QTableWidget()
        self.otro_table.setColumnCount(4)
        self.otro_table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad", "Acciones"])
        self.otro_table.horizontalHeader().setStretchLastSection(True)
        self.otro_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.otro_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.otro_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.otro_table.verticalHeader().setVisible(False)
        otro_layout.addWidget(self.otro_table)
        tabs.addTab(otro_tab, "Otros Materiales")

        mov_tab = QWidget()
        mov_layout = QVBoxLayout(mov_tab)
        mov_title = QLabel("Historial de Movimientos")
        mov_title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px 0;")
        mov_layout.addWidget(mov_title)
        self.mov_table = QTableWidget()
        self.mov_table.setColumnCount(5)
        self.mov_table.setHorizontalHeaderLabels(["ID", "Tipo", "Item", "Cantidad", "Fecha"])
        self.mov_table.horizontalHeader().setStretchLastSection(True)
        self.mov_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.mov_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.mov_table.verticalHeader().setVisible(False)
        mov_layout.addWidget(self.mov_table)
        tabs.addTab(mov_tab, "Movimientos")

        layout.addWidget(tabs)

    def refresh(self):
        self.refresh_filamentos()
        self.refresh_pinturas()
        self.refresh_otros()
        self.refresh_movimientos()

    def refresh_filamentos(self):
        items = self.db.fetch_all("SELECT * FROM filamentos ORDER BY nombre")
        self.fil_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.fil_table.setItem(i, 0, QTableWidgetItem(str(item["id"])))
            self.fil_table.setItem(i, 1, QTableWidgetItem(item["nombre"]))
            self.fil_table.setItem(i, 2, QTableWidgetItem(item["marca"] or ""))
            self.fil_table.setItem(i, 3, QTableWidgetItem(item["tipo"] or ""))
            self.fil_table.setItem(i, 4, QTableWidgetItem(item["color"] or ""))
            self.fil_table.setItem(i, 5, QTableWidgetItem(f"{item['peso_disponible']:.0f}g"))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(32, 28)
            btn_edit.clicked.connect(lambda checked, fid=item["id"]: self.edit_filamento(fid))
            btn_layout.addWidget(btn_edit)
            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(32, 28)
            btn_del.clicked.connect(lambda checked, fid=item["id"]: self.delete_filamento(fid))
            btn_layout.addWidget(btn_del)
            self.fil_table.setCellWidget(i, 6, btn_widget)

        self.fil_table.setColumnHidden(0, True)

    def refresh_pinturas(self):
        items = self.db.fetch_all("SELECT * FROM pinturas ORDER BY color")
        self.pin_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.pin_table.setItem(i, 0, QTableWidgetItem(str(item["id"])))
            self.pin_table.setItem(i, 1, QTableWidgetItem(item["marca"] or ""))
            self.pin_table.setItem(i, 2, QTableWidgetItem(item["tipo"] or ""))
            self.pin_table.setItem(i, 3, QTableWidgetItem(item["color"] or ""))
            self.pin_table.setItem(i, 4, QTableWidgetItem(str(item["cantidad_disponible"])))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(32, 28)
            btn_edit.clicked.connect(lambda checked, pid=item["id"]: self.edit_pintura(pid))
            btn_layout.addWidget(btn_edit)
            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(32, 28)
            btn_del.clicked.connect(lambda checked, pid=item["id"]: self.delete_pintura(pid))
            btn_layout.addWidget(btn_del)
            self.pin_table.setCellWidget(i, 5, btn_widget)

        self.pin_table.setColumnHidden(0, True)

    def refresh_otros(self):
        items = self.db.fetch_all("SELECT * FROM otros_materiales ORDER BY nombre")
        self.otro_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.otro_table.setItem(i, 0, QTableWidgetItem(str(item["id"])))
            self.otro_table.setItem(i, 1, QTableWidgetItem(item["nombre"]))
            self.otro_table.setItem(i, 2, QTableWidgetItem(str(item["cantidad"])))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(32, 28)
            btn_edit.clicked.connect(lambda checked, oid=item["id"]: self.edit_otro(oid))
            btn_layout.addWidget(btn_edit)
            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(32, 28)
            btn_del.clicked.connect(lambda checked, oid=item["id"]: self.delete_otro(oid))
            btn_layout.addWidget(btn_del)
            self.otro_table.setCellWidget(i, 3, btn_widget)

        self.otro_table.setColumnHidden(0, True)

    def refresh_movimientos(self):
        items = self.db.fetch_all("SELECT * FROM inventario_movimientos ORDER BY fecha DESC LIMIT 100")
        self.mov_table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.mov_table.setItem(i, 0, QTableWidgetItem(str(item["id"])))
            self.mov_table.setItem(i, 1, QTableWidgetItem(item["tipo"]))
            self.mov_table.setItem(i, 2, QTableWidgetItem(f"{item['item_tipo']} #{item['item_id']}" if item["item_id"] else "—"))
            self.mov_table.setItem(i, 3, QTableWidgetItem(str(item["cantidad"])))
            self.mov_table.setItem(i, 4, QTableWidgetItem(item["fecha"][:16] if item["fecha"] else ""))

        self.mov_table.setColumnHidden(0, True)

    def add_filamento(self):
        dialog = FilamentoDialog(self.db)
        if dialog.exec():
            self.refresh()

    def edit_filamento(self, fid):
        item = self.db.fetch_one("SELECT * FROM filamentos WHERE id=?", [fid])
        if item:
            dialog = FilamentoDialog(self.db, item)
            if dialog.exec():
                self.refresh()

    def delete_filamento(self, fid):
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar este filamento?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete("filamentos", "id=?", [fid])
            self.refresh()

    def add_pintura(self):
        dialog = PinturaDialog(self.db)
        if dialog.exec():
            self.refresh()

    def edit_pintura(self, pid):
        item = self.db.fetch_one("SELECT * FROM pinturas WHERE id=?", [pid])
        if item:
            dialog = PinturaDialog(self.db, item)
            if dialog.exec():
                self.refresh()

    def delete_pintura(self, pid):
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar esta pintura?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete("pinturas", "id=?", [pid])
            self.refresh()

    def add_otro(self):
        dialog = OtroMaterialDialog(self.db)
        if dialog.exec():
            self.refresh()

    def edit_otro(self, oid):
        item = self.db.fetch_one("SELECT * FROM otros_materiales WHERE id=?", [oid])
        if item:
            dialog = OtroMaterialDialog(self.db, item)
            if dialog.exec():
                self.refresh()

    def delete_otro(self, oid):
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar este material?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete("otros_materiales", "id=?", [oid])
            self.refresh()
