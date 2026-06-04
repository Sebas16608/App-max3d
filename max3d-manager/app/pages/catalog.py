from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QMessageBox, QHeaderView, QGroupBox
)
from PySide6.QtCore import Qt


class ProductDialog(QDialog):
    def __init__(self, db, producto=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.producto = producto
        self.setWindowTitle("Producto" if not producto else "Editar Producto")
        self.setMinimumSize(600, 600)
        self.setup_ui()
        if producto:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(10)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre del producto")
        form.addRow("Nombre:", self.nombre)

        self.descripcion = QTextEdit()
        self.descripcion.setPlaceholderText("Descripción...")
        self.descripcion.setMaximumHeight(70)
        form.addRow("Descripción:", self.descripcion)

        self.categoria = QComboBox()
        cats = self.db.fetch_all("SELECT id, nombre FROM categorias ORDER BY nombre")
        self.categoria.addItem("Sin categoría", 0)
        for c in cats:
            self.categoria.addItem(c["nombre"], c["id"])
        form.addRow("Categoría:", self.categoria)

        self.material = QLineEdit()
        self.material.setPlaceholderText("Ej: PLA, PETG, TPU...")
        form.addRow("Material principal:", self.material)

        self.peso = QDoubleSpinBox()
        self.peso.setRange(0, 99999)
        self.peso.setSuffix(" g")
        self.peso.setDecimals(1)
        form.addRow("Peso estimado:", self.peso)

        self.horas_impresion = QDoubleSpinBox()
        self.horas_impresion.setRange(0, 999)
        self.horas_impresion.setSuffix(" h")
        self.horas_impresion.setDecimals(1)
        form.addRow("Horas impresión:", self.horas_impresion)

        self.pintado = QCheckBox("¿Incluye pintado?")
        self.pintado.toggled.connect(self.on_pintado_toggled)
        form.addRow("", self.pintado)

        self.color_pintura = QLineEdit()
        self.color_pintura.setPlaceholderText("Color de pintura")
        form.addRow("Color pintura:", self.color_pintura)

        self.costo_pintura = QDoubleSpinBox()
        self.costo_pintura.setRange(0, 99999)
        self.costo_pintura.setPrefix("Q ")
        self.costo_pintura.setDecimals(2)
        form.addRow("Costo pintura:", self.costo_pintura)

        self.modelado_mi = QCheckBox("Modelado por mí")
        self.modelado_mi.toggled.connect(self.on_modelado_toggled)
        form.addRow("", self.modelado_mi)

        self.horas_modelado = QDoubleSpinBox()
        self.horas_modelado.setRange(0, 999)
        self.horas_modelado.setSuffix(" h")
        self.horas_modelado.setDecimals(1)
        form.addRow("Horas modelado:", self.horas_modelado)

        self.precio_personalizado = QDoubleSpinBox()
        self.precio_personalizado.setRange(0, 999999)
        self.precio_personalizado.setPrefix("Q ")
        self.precio_personalizado.setDecimals(2)
        self.precio_personalizado.setSpecialValueText("Automático")
        form.addRow("Precio personalizado:", self.precio_personalizado)

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

        self.on_pintado_toggled(False)
        self.on_modelado_toggled(False)

    def on_pintado_toggled(self, checked):
        self.color_pintura.setEnabled(checked)
        self.costo_pintura.setEnabled(checked)

    def on_modelado_toggled(self, checked):
        self.horas_modelado.setEnabled(checked)

    def load_data(self):
        self.nombre.setText(self.producto["nombre"])
        self.descripcion.setPlainText(self.producto["descripcion"] or "")
        idx = self.categoria.findData(self.producto["categoria_id"])
        if idx >= 0:
            self.categoria.setCurrentIndex(idx)
        self.material.setText(self.producto["material_principal"] or "")
        self.peso.setValue(self.producto["peso_estimado"] or 0)
        self.horas_impresion.setValue(self.producto["horas_impresion"] or 0)
        self.pintado.setChecked(bool(self.producto["pintado"]))
        self.color_pintura.setText(self.producto["color_pintura"] or "")
        self.costo_pintura.setValue(self.producto["costo_pintura"] or 0)
        self.modelado_mi.setChecked(bool(self.producto["modelado_por_mi"]))
        self.horas_modelado.setValue(self.producto["horas_modelado"] or 0)
        if self.producto["precio_personalizado"]:
            self.precio_personalizado.setValue(self.producto["precio_personalizado"])

    def guardar(self):
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        data = {
            "nombre": self.nombre.text().strip(),
            "descripcion": self.descripcion.toPlainText().strip(),
            "categoria_id": self.categoria.currentData(),
            "material_principal": self.material.text().strip(),
            "peso_estimado": self.peso.value(),
            "horas_impresion": self.horas_impresion.value(),
            "pintado": 1 if self.pintado.isChecked() else 0,
            "color_pintura": self.color_pintura.text().strip(),
            "costo_pintura": self.costo_pintura.value(),
            "modelado_por_mi": 1 if self.modelado_mi.isChecked() else 0,
            "horas_modelado": self.horas_modelado.value(),
            "precio_personalizado": self.precio_personalizado.value() if self.precio_personalizado.value() > 0 else None,
        }
        if self.producto:
            self.db.update("productos", data, "id=?", [self.producto["id"]])
        else:
            self.db.insert("productos", data)
        self.accept()


class CatalogPage(QWidget):
    def __init__(self, db, config, parent=None):
        super().__init__(parent)
        self.db = db
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QHBoxLayout()
        title = QLabel("Catálogo de Productos")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e94560;")
        header.addWidget(title)
        header.addStretch()

        self.btn_add = QPushButton("+ Nuevo Producto")
        self.btn_add.clicked.connect(self.add_producto)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Categoría", "Material", "Peso", "Horas",
            "Vendido", "Ganancia", "Acciones"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self):
        productos = self.db.fetch_all("""
            SELECT p.*, c.nombre as cat_nombre,
                (SELECT COALESCE(SUM(cp.cantidad),0) FROM clientes_productos cp WHERE cp.producto_id=p.id AND cp.estado IN ('Entregado','Terminado')) as vendido,
                (SELECT COALESCE(SUM(cp.precio_final - cp.costo_total),0) FROM clientes_productos cp WHERE cp.producto_id=p.id AND cp.estado IN ('Entregado','Terminado')) as ganancia
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            ORDER BY p.nombre
        """)
        self.table.setRowCount(len(productos))
        for i, p in enumerate(productos):
            self.table.setItem(i, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(p["nombre"]))
            self.table.setItem(i, 2, QTableWidgetItem(p["cat_nombre"] or "—"))
            self.table.setItem(i, 3, QTableWidgetItem(p["material_principal"] or "—"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{p['peso_estimado']:.0f}g" if p["peso_estimado"] else "—"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{p['horas_impresion']:.1f}h" if p["horas_impresion"] else "—"))
            self.table.setItem(i, 6, QTableWidgetItem(str(p["vendido"])))
            self.table.setItem(i, 7, QTableWidgetItem(f"Q{p['ganancia']:.2f}"))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)

            btn_edit = QPushButton("Editar")
            btn_edit.setObjectName("small")
            btn_edit.setFixedHeight(30)
            btn_edit.clicked.connect(lambda checked, pid=p["id"]: self.edit_producto(pid))
            btn_layout.addWidget(btn_edit)

            btn_toggle = QPushButton("Desactivar" if p["activo"] else "Activar")
            btn_toggle.setObjectName("small")
            btn_toggle.setFixedHeight(30)
            btn_toggle.setStyleSheet(f"background-color: {'#8b0000' if p['activo'] else '#006400'}; font-size: 14px; padding: 4px 10px;")
            btn_toggle.clicked.connect(lambda checked, pid=p["id"], a=p["activo"]: self.toggle_producto(pid, a))
            btn_layout.addWidget(btn_toggle)

            btn_del = QPushButton("Borrar")
            btn_del.setObjectName("small")
            btn_del.setFixedHeight(30)
            btn_del.setStyleSheet("background-color: #8b0000; font-size: 14px; padding: 4px 10px;")
            btn_del.clicked.connect(lambda checked, pid=p["id"]: self.delete_producto(pid))
            btn_layout.addWidget(btn_del)

            self.table.setCellWidget(i, 8, btn_widget)

        self.table.setColumnHidden(0, True)

    def add_producto(self):
        dialog = ProductDialog(self.db)
        if dialog.exec():
            self.refresh()

    def edit_producto(self, pid):
        producto = self.db.fetch_one("SELECT * FROM productos WHERE id=?", [pid])
        if producto:
            dialog = ProductDialog(self.db, producto)
            if dialog.exec():
                self.refresh()

    def toggle_producto(self, pid, activo):
        self.db.update("productos", {"activo": 0 if activo else 1}, "id=?", [pid])
        self.refresh()

    def delete_producto(self, pid):
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar este producto?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete("productos", "id=?", [pid])
            self.refresh()
