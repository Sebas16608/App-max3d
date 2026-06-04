from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QCheckBox, QMessageBox, QHeaderView, QDateEdit, QGroupBox,
    QRadioButton, QTabWidget
)
from PySide6.QtCore import Qt, QDate
from app.utils import calcular_totales_pedido, formatear_moneda


class OrderDialog(QDialog):
    def __init__(self, db, config, pedido=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.config = config
        self.pedido = pedido
        self.setWindowTitle("Nuevo Pedido" if not pedido else "Editar Pedido")
        self.setMinimumSize(650, 600)
        self.setup_ui()
        if pedido:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        tabs = QTabWidget()
        main_tab = QWidget()
        costs_tab = QWidget()
        payment_tab = QWidget()

        # Main tab
        m_layout = QFormLayout(main_tab)
        m_layout.setSpacing(10)

        self.cliente = QComboBox()
        self.cliente.setMinimumWidth(250)
        clientes = self.db.fetch_all("SELECT id, nombre FROM clientes ORDER BY nombre")
        self.cliente.addItem("Seleccionar cliente", 0)
        for c in clientes:
            self.cliente.addItem(c["nombre"], c["id"])
        m_layout.addRow("Cliente:", self.cliente)

        self.tipo_producto = QComboBox()
        self.tipo_producto.addItem("Producto personalizado", "custom")
        self.tipo_producto.addItem("Desde catálogo", "catalog")
        self.tipo_producto.currentIndexChanged.connect(self.on_tipo_cambio)
        m_layout.addRow("Tipo:", self.tipo_producto)

        self.producto_catalogo = QComboBox()
        self.producto_catalogo.setMinimumWidth(250)
        productos = self.db.fetch_all("SELECT id, nombre, material_principal, peso_estimado, horas_impresion, pintado, color_pintura, costo_pintura, modelado_por_mi, horas_modelado, precio_personalizado FROM productos WHERE activo=1 ORDER BY nombre")
        self.producto_catalogo.addItem("Seleccionar producto", 0)
        for p in productos:
            self.producto_catalogo.addItem(p["nombre"], p["id"])
        self.producto_catalogo.currentIndexChanged.connect(self.on_producto_cambio)
        m_layout.addRow("Producto:", self.producto_catalogo)

        self.nombre_personalizado = QLineEdit()
        self.nombre_personalizado.setPlaceholderText("Nombre del producto personalizado")
        m_layout.addRow("Nombre producto:", self.nombre_personalizado)

        self.cantidad = QSpinBox()
        self.cantidad.setRange(1, 9999)
        self.cantidad.setValue(1)
        m_layout.addRow("Cantidad:", self.cantidad)

        self.estado = QComboBox()
        estados = ["Pendiente", "En impresión", "Pintando", "Terminado", "Entregado", "Cancelado"]
        self.estado.addItems(estados)
        m_layout.addRow("Estado:", self.estado)

        self.fecha_entrega = QDateEdit()
        self.fecha_entrega.setCalendarPopup(True)
        self.fecha_entrega.setDate(QDate.currentDate())
        self.fecha_entrega.setSpecialValueText("Sin fecha")
        m_layout.addRow("Fecha entrega:", self.fecha_entrega)

        self.notas = QTextEdit()
        self.notas.setPlaceholderText("Notas del pedido...")
        self.notas.setMaximumHeight(60)
        m_layout.addRow("Notas:", self.notas)

        tabs.addTab(main_tab, "Principal")

        # Costs tab
        c_layout = QFormLayout(costs_tab)
        c_layout.setSpacing(10)

        self.material = QLineEdit()
        self.material.setPlaceholderText("Ej: PLA Negro")
        c_layout.addRow("Material:", self.material)

        self.peso = QDoubleSpinBox()
        self.peso.setRange(0, 99999)
        self.peso.setSuffix(" g")
        self.peso.setDecimals(1)
        c_layout.addRow("Peso real:", self.peso)

        self.horas_impresion = QDoubleSpinBox()
        self.horas_impresion.setRange(0, 999)
        self.horas_impresion.setSuffix(" h")
        self.horas_impresion.setDecimals(1)
        c_layout.addRow("Horas impresión:", self.horas_impresion)

        self.pintado_chk = QCheckBox("Pintado")
        self.pintado_chk.toggled.connect(self.on_pintado_toggled)
        c_layout.addRow("", self.pintado_chk)

        self.color_pintura = QLineEdit()
        self.color_pintura.setPlaceholderText("Color pintura")
        c_layout.addRow("Color pintura:", self.color_pintura)

        self.costo_pintura = QDoubleSpinBox()
        self.costo_pintura.setRange(0, 99999)
        self.costo_pintura.setPrefix("Q ")
        self.costo_pintura.setDecimals(2)
        c_layout.addRow("Costo pintura:", self.costo_pintura)

        self.modelado_chk = QCheckBox("Modelado por mí")
        self.modelado_chk.toggled.connect(self.on_modelado_toggled)
        c_layout.addRow("", self.modelado_chk)

        self.horas_modelado = QDoubleSpinBox()
        self.horas_modelado.setRange(0, 999)
        self.horas_modelado.setSuffix(" h")
        self.horas_modelado.setDecimals(1)
        c_layout.addRow("Horas modelado:", self.horas_modelado)

        self.costo_modelado = QDoubleSpinBox()
        self.costo_modelado.setRange(0, 99999)
        self.costo_modelado.setPrefix("Q ")
        self.costo_modelado.setDecimals(2)
        self.costo_modelado.setReadOnly(True)
        c_layout.addRow("Costo modelado:", self.costo_modelado)

        self.btn_calcular = QPushButton("Calcular Costos")
        self.btn_calcular.clicked.connect(self.calcular_costos)
        c_layout.addRow("", self.btn_calcular)

        self.resultados = QGroupBox("Resultados")
        r_layout = QFormLayout(self.resultados)
        self.lbl_costo_material = QLabel("—")
        r_layout.addRow("Costo material:", self.lbl_costo_material)
        self.lbl_costo_luz = QLabel("—")
        r_layout.addRow("Costo luz:", self.lbl_costo_luz)
        self.lbl_costo_desgaste = QLabel("—")
        r_layout.addRow("Costo desgaste:", self.lbl_costo_desgaste)
        self.lbl_costo_pintura = QLabel("—")
        r_layout.addRow("Costo pintura:", self.lbl_costo_pintura)
        self.lbl_costo_modelado = QLabel("—")
        r_layout.addRow("Costo modelado:", self.lbl_costo_modelado)
        self.lbl_costo_total = QLabel("—")
        self.lbl_costo_total.setStyleSheet("font-weight: bold; color: #e94560;")
        r_layout.addRow("Costo total:", self.lbl_costo_total)
        self.lbl_trabajo = QLabel("—")
        r_layout.addRow("Trabajo:", self.lbl_trabajo)
        self.lbl_precio_sugerido = QLabel("—")
        self.lbl_precio_sugerido.setStyleSheet("font-weight: bold; color: #00c853;")
        r_layout.addRow("Precio sugerido:", self.lbl_precio_sugerido)
        self.lbl_ganancia = QLabel("—")
        self.lbl_ganancia.setStyleSheet("color: #00bcd4;")
        r_layout.addRow("Ganancia estimada:", self.lbl_ganancia)

        self.precio_final = QDoubleSpinBox()
        self.precio_final.setRange(0, 999999)
        self.precio_final.setPrefix("Q ")
        self.precio_final.setDecimals(2)
        r_layout.addRow("Precio final:", self.precio_final)

        c_layout.addWidget(self.resultados)

        tabs.addTab(costs_tab, "Costos")

        # Payment tab
        p_layout = QFormLayout(payment_tab)
        p_layout.setSpacing(10)

        self.estado_pago = QComboBox()
        self.estado_pago.addItems(["Sin pagar", "Anticipo recibido", "Pagado parcialmente", "Pagado completamente"])
        p_layout.addRow("Estado pago:", self.estado_pago)

        self.anticipo = QDoubleSpinBox()
        self.anticipo.setRange(0, 999999)
        self.anticipo.setPrefix("Q ")
        self.anticipo.setDecimals(2)
        p_layout.addRow("Anticipo:", self.anticipo)

        self.pago_total = QDoubleSpinBox()
        self.pago_total.setRange(0, 999999)
        self.pago_total.setPrefix("Q ")
        self.pago_total.setDecimals(2)
        p_layout.addRow("Total pagado:", self.pago_total)

        self.fecha_pago = QDateEdit()
        self.fecha_pago.setCalendarPopup(True)
        self.fecha_pago.setDate(QDate.currentDate())
        self.fecha_pago.setSpecialValueText("Sin fecha")
        p_layout.addRow("Fecha pago:", self.fecha_pago)

        tabs.addTab(payment_tab, "Pagos")

        layout.addWidget(tabs)

        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardar)
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)

        self.on_tipo_cambio(0)
        self.on_pintado_toggled(False)
        self.on_modelado_toggled(False)

    def on_tipo_cambio(self, idx):
        tipo = self.tipo_producto.currentData()
        is_catalog = tipo == "catalog"
        self.producto_catalogo.setVisible(is_catalog)
        self.nombre_personalizado.setVisible(not is_catalog)
        if not is_catalog:
            self.nombre_personalizado.setEnabled(True)

    def on_pintado_toggled(self, checked):
        self.color_pintura.setEnabled(checked)
        self.costo_pintura.setEnabled(checked)

    def on_modelado_toggled(self, checked):
        self.horas_modelado.setEnabled(checked)
        self.costo_modelado.setEnabled(checked)
        if checked:
            self.calcular_costo_modelado()

    def on_producto_cambio(self, idx):
        if idx <= 0:
            return
        prod_id = self.producto_catalogo.currentData()
        prod = self.db.fetch_one("SELECT * FROM productos WHERE id=?", [prod_id])
        if prod:
            self.material.setText(prod["material_principal"] or "")
            self.peso.setValue(prod["peso_estimado"] or 0)
            self.horas_impresion.setValue(prod["horas_impresion"] or 0)
            self.pintado_chk.setChecked(bool(prod["pintado"]))
            self.color_pintura.setText(prod["color_pintura"] or "")
            self.costo_pintura.setValue(prod["costo_pintura"] or 0)
            self.modelado_chk.setChecked(bool(prod["modelado_por_mi"]))
            self.horas_modelado.setValue(prod["horas_modelado"] or 0)
            if prod["precio_personalizado"]:
                self.precio_final.setValue(prod["precio_personalizado"])
            self.calcular_costos()

    def calcular_costo_modelado(self):
        horas = self.horas_modelado.value()
        costo_hora = self.config.get("modelado_costo_hora", 25)
        self.costo_modelado.setValue(horas * costo_hora)

    def calcular_costos(self):
        peso = self.peso.value()
        horas_imp = self.horas_impresion.value()
        horas_mod = self.horas_modelado.value() if self.modelado_chk.isChecked() else 0
        costo_pint = self.costo_pintura.value() if self.pintado_chk.isChecked() else 0

        precio_por_gramo = 0
        mat_nombre = self.material.text().strip()
        if mat_nombre:
            fil = self.db.fetch_one("SELECT precio_por_gramo FROM filamentos WHERE nombre LIKE ? LIMIT 1", (f"%{mat_nombre}%",))
            if fil:
                precio_por_gramo = fil["precio_por_gramo"] or 0

        if self.modelado_chk.isChecked():
            self.calcular_costo_modelado()

        resultados = calcular_totales_pedido(
            peso=peso,
            precio_por_gramo=precio_por_gramo,
            horas_impresion=horas_imp,
            horas_modelado=horas_mod,
            costo_hora_modelado=self.config.get("modelado_costo_hora", 25),
            costo_pintura=costo_pint,
            potencia_w=self.config.get("electricidad_potencia", 300),
            costo_kwh=self.config.get("electricidad_costo", 0.000153),
            costo_desgaste_hora=self.config.get("desgaste_costo_hora", 0.75),
            trabajo_porcentaje=self.config.get("trabajo_porcentaje", 20),
            redondeo=self.config.get("redondeo", 5),
        )

        self.lbl_costo_material.setText(formatear_moneda(resultados["costo_material"]))
        self.lbl_costo_luz.setText(formatear_moneda(resultados["costo_luz"]))
        self.lbl_costo_desgaste.setText(formatear_moneda(resultados["costo_desgaste"]))
        self.lbl_costo_pintura.setText(formatear_moneda(costo_pint))
        self.lbl_costo_modelado.setText(formatear_moneda(resultados["costo_modelado"]))
        self.lbl_costo_total.setText(formatear_moneda(resultados["costo_total"]))
        self.lbl_trabajo.setText(formatear_moneda(resultados["trabajo"]))
        self.lbl_precio_sugerido.setText(formatear_moneda(resultados["precio_sugerido"]))
        self.lbl_ganancia.setText(formatear_moneda(resultados["ganancia_estimada"]))
        self.precio_final.setValue(resultados["precio_sugerido"])

    def load_data(self):
        self.cliente.setCurrentIndex(self.cliente.findData(self.pedido["cliente_id"]))
        if self.pedido["producto_id"]:
            self.tipo_producto.setCurrentIndex(1)
            idx = self.producto_catalogo.findData(self.pedido["producto_id"])
            if idx >= 0:
                self.producto_catalogo.setCurrentIndex(idx)
        self.nombre_personalizado.setText(self.pedido["nombre_personalizado"] or "")
        self.cantidad.setValue(self.pedido["cantidad"] or 1)
        idx = self.estado.findText(self.pedido["estado"])
        if idx >= 0:
            self.estado.setCurrentIndex(idx)
        if self.pedido["fecha_entrega"]:
            self.fecha_entrega.setDate(QDate.fromString(self.pedido["fecha_entrega"], "yyyy-MM-dd"))
        self.notas.setPlainText(self.pedido["notas"] or "")
        self.material.setText(self.pedido["material_principal"] or "")
        self.peso.setValue(self.pedido["peso_real"] or 0)
        self.horas_impresion.setValue(self.pedido["horas_impresion_real"] or 0)
        self.pintado_chk.setChecked(bool(self.pedido["pintado"]))
        self.color_pintura.setText(self.pedido["color_pintura"] or "")
        self.costo_pintura.setValue(self.pedido["costo_pintura"] or 0)
        self.modelado_chk.setChecked(bool(self.pedido["modelado_por_mi"]))
        self.horas_modelado.setValue(self.pedido["horas_modelado"] or 0)
        self.estado_pago.setCurrentText(self.pedido["estado_pago"] or "Sin pagar")
        self.anticipo.setValue(self.pedido["pago_anticipo"] or 0)
        self.pago_total.setValue(self.pedido["pago_total"] or 0)
        if self.pedido["fecha_pago"]:
            self.fecha_pago.setDate(QDate.fromString(self.pedido["fecha_pago"], "yyyy-MM-dd"))

    def guardar(self):
        if self.cliente.currentData() == 0:
            QMessageBox.warning(self, "Error", "Seleccione un cliente")
            return

        es_catalogo = self.tipo_producto.currentData() == "catalog"
        prod_id = self.producto_catalogo.currentData() if es_catalogo and self.producto_catalogo.currentData() != 0 else None
        nom_personalizado = self.nombre_personalizado.text().strip() if not es_catalogo else None

        if not prod_id and not nom_personalizado:
            QMessageBox.warning(self, "Error", "Especifique un producto o nombre personalizado")
            return

        costo_modelado_val = self.horas_modelado.value() * self.config.get("modelado_costo_hora", 25) if self.modelado_chk.isChecked() else 0

        data = {
            "cliente_id": self.cliente.currentData(),
            "producto_id": prod_id,
            "nombre_personalizado": nom_personalizado,
            "cantidad": self.cantidad.value(),
            "estado": self.estado.currentText(),
            "fecha_entrega": self.fecha_entrega.date().toString("yyyy-MM-dd") if self.fecha_entrega.date() != QDate.currentDate() or self.fecha_entrega.specialValueText() == "" else None,
            "notas": self.notas.toPlainText().strip(),
            "pintado": 1 if self.pintado_chk.isChecked() else 0,
            "color_pintura": self.color_pintura.text().strip(),
            "costo_pintura": self.costo_pintura.value(),
            "modelado_por_mi": 1 if self.modelado_chk.isChecked() else 0,
            "horas_modelado": self.horas_modelado.value(),
            "costo_modelado": costo_modelado_val,
            "material_principal": self.material.text().strip(),
            "peso_real": self.peso.value(),
            "horas_impresion_real": self.horas_impresion.value(),
            "costo_material": float(self.lbl_costo_material.text().replace("Q", "").replace(",", "")) if self.lbl_costo_material.text() != "—" else 0,
            "costo_luz": float(self.lbl_costo_luz.text().replace("Q", "").replace(",", "")) if self.lbl_costo_luz.text() != "—" else 0,
            "costo_desgaste": float(self.lbl_costo_desgaste.text().replace("Q", "").replace(",", "")) if self.lbl_costo_desgaste.text() != "—" else 0,
            "costo_total": float(self.lbl_costo_total.text().replace("Q", "").replace(",", "")) if self.lbl_costo_total.text() != "—" else 0,
            "trabajo": float(self.lbl_trabajo.text().replace("Q", "").replace(",", "")) if self.lbl_trabajo.text() != "—" else 0,
            "precio_sugerido": float(self.lbl_precio_sugerido.text().replace("Q", "").replace(",", "")) if self.lbl_precio_sugerido.text() != "—" else 0,
            "precio_final": self.precio_final.value(),
            "pago_anticipo": self.anticipo.value(),
            "pago_total": self.pago_total.value(),
            "estado_pago": self.estado_pago.currentText(),
            "fecha_pago": self.fecha_pago.date().toString("yyyy-MM-dd") if self.fecha_pago.date() != QDate.currentDate() or self.fecha_pago.specialValueText() == "" else None,
        }

        if self.pedido:
            self.db.update("clientes_productos", data, "id=?", [self.pedido["id"]])
        else:
            self.db.insert("clientes_productos", data)

        if self.estado.currentText() == "Terminado" or self.estado.currentText() == "Entregado":
            self.descontar_material()

        self.accept()

    def descontar_material(self):
        mat_nombre = self.material.text().strip()
        peso_consumido = self.peso.value()
        if mat_nombre and peso_consumido > 0:
            fil = self.db.fetch_one("SELECT id, peso_disponible FROM filamentos WHERE nombre LIKE ? LIMIT 1", (f"%{mat_nombre}%",))
            if fil:
                nuevo_peso = max(0, fil["peso_disponible"] - peso_consumido)
                self.db.update("filamentos", {"peso_disponible": nuevo_peso}, "id=?", [fil["id"]])
                self.db.insert("inventario_movimientos", {
                    "tipo": "consumo",
                    "item_id": fil["id"],
                    "item_tipo": "filamento",
                    "cantidad": -peso_consumido,
                    "descripcion": f"Consumido en pedido"
                })


class OrdersPage(QWidget):
    def __init__(self, db, config, parent=None):
        super().__init__(parent)
        self.db = db
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QHBoxLayout()
        title = QLabel("Pedidos y Ventas")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e94560;")
        header.addWidget(title)
        header.addStretch()

        self.btn_add = QPushButton("+ Nuevo Pedido")
        self.btn_add.clicked.connect(self.add_pedido)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Cliente", "Producto", "Cant", "Estado", "Total",
            "Pagado", "Pendiente", "Estado Pago", "Acciones"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self):
        pedidos = self.db.fetch_all("""
            SELECT cp.*, c.nombre as cliente_nombre,
                COALESCE(p.nombre, cp.nombre_personalizado) as prod_nombre
            FROM clientes_productos cp
            JOIN clientes c ON cp.cliente_id = c.id
            LEFT JOIN productos p ON cp.producto_id = p.id
            ORDER BY cp.fecha_pedido DESC
        """)
        self.table.setRowCount(len(pedidos))
        for i, ped in enumerate(pedidos):
            self.table.setItem(i, 0, QTableWidgetItem(str(ped["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(ped["cliente_nombre"]))
            self.table.setItem(i, 2, QTableWidgetItem(ped["prod_nombre"] or "—"))
            self.table.setItem(i, 3, QTableWidgetItem(str(ped["cantidad"])))
            self.table.setItem(i, 4, QTableWidgetItem(ped["estado"]))
            self.table.setItem(i, 5, QTableWidgetItem(f"Q{ped['precio_final']:.2f}" if ped["precio_final"] else "—"))
            self.table.setItem(i, 6, QTableWidgetItem(f"Q{ped['pago_total']:.2f}" if ped["pago_total"] else "—"))

            pendiente = (ped["precio_final"] or 0) - (ped["pago_total"] or 0)
            self.table.setItem(i, 7, QTableWidgetItem(f"Q{pendiente:.2f}"))
            self.table.setItem(i, 8, QTableWidgetItem(ped["estado_pago"] or "—"))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)

            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(32, 28)
            btn_edit.clicked.connect(lambda checked, pid=ped["id"]: self.edit_pedido(pid))
            btn_layout.addWidget(btn_edit)

            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(32, 28)
            btn_del.clicked.connect(lambda checked, pid=ped["id"]: self.delete_pedido(pid))
            btn_layout.addWidget(btn_del)

            self.table.setCellWidget(i, 9, btn_widget)

        self.table.setColumnHidden(0, True)

    def add_pedido(self):
        dialog = OrderDialog(self.db, self.config)
        if dialog.exec():
            self.refresh()

    def edit_pedido(self, pid):
        pedido = self.db.fetch_one("SELECT * FROM clientes_productos WHERE id=?", [pid])
        if pedido:
            dialog = OrderDialog(self.db, self.config, pedido)
            if dialog.exec():
                self.refresh()

    def delete_pedido(self, pid):
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar este pedido?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete("clientes_productos", "id=?", [pid])
            self.refresh()
