from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QMessageBox, QHeaderView, QSplitter,
    QFrame, QGroupBox, QTabWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ClientDialog(QDialog):
    def __init__(self, db, cliente=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.cliente = cliente
        self.setWindowTitle("Cliente" if not cliente else "Editar Cliente")
        self.setMinimumSize(550, 450)
        self.setup_ui()
        if cliente:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre completo")
        form.addRow("Nombre:", self.nombre)

        self.telefono = QLineEdit()
        self.telefono.setPlaceholderText("Teléfono")
        form.addRow("Teléfono:", self.telefono)

        self.direccion = QLineEdit()
        self.direccion.setPlaceholderText("Dirección")
        form.addRow("Dirección:", self.direccion)

        self.correo = QLineEdit()
        self.correo.setPlaceholderText("Correo electrónico")
        form.addRow("Correo:", self.correo)

        self.notas = QTextEdit()
        self.notas.setPlaceholderText("Notas adicionales...")
        self.notas.setMaximumHeight(80)
        form.addRow("Notas:", self.notas)

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
        self.nombre.setText(self.cliente["nombre"])
        self.telefono.setText(self.cliente["telefono"] or "")
        self.direccion.setText(self.cliente["direccion"] or "")
        self.correo.setText(self.cliente["correo"] or "")
        self.notas.setPlainText(self.cliente["notas"] or "")

    def guardar(self):
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        data = {
            "nombre": self.nombre.text().strip(),
            "telefono": self.telefono.text().strip(),
            "direccion": self.direccion.text().strip(),
            "correo": self.correo.text().strip(),
            "notas": self.notas.toPlainText().strip(),
        }
        if self.cliente:
            self.db.update("clientes", data, "id=?", [self.cliente["id"]])
        else:
            self.db.insert("clientes", data)
        self.accept()


class ClientsPage(QWidget):
    def __init__(self, db, config, parent=None):
        super().__init__(parent)
        self.db = db
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QHBoxLayout()
        title = QLabel("Clientes")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e94560;")
        header.addWidget(title)
        header.addStretch()

        self.btn_add = QPushButton("+ Nuevo Cliente")
        self.btn_add.clicked.connect(self.add_cliente)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Correo", "Pedidos", "Acciones"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self):
        clientes = self.db.fetch_all("SELECT c.*, (SELECT COUNT(*) FROM clientes_productos WHERE cliente_id=c.id) as pedidos FROM clientes c ORDER BY c.nombre")
        self.table.setRowCount(len(clientes))
        for i, c in enumerate(clientes):
            self.table.setItem(i, 0, QTableWidgetItem(str(c["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(c["nombre"]))
            self.table.setItem(i, 2, QTableWidgetItem(c["telefono"] or ""))
            self.table.setItem(i, 3, QTableWidgetItem(c["correo"] or ""))
            self.table.setItem(i, 4, QTableWidgetItem(str(c["pedidos"])))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)

            btn_edit = QPushButton("Editar")
            btn_edit.setObjectName("small")
            btn_edit.setFixedHeight(30)
            btn_edit.clicked.connect(lambda checked, cid=c["id"]: self.edit_cliente(cid))
            btn_layout.addWidget(btn_edit)

            btn_history = QPushButton("Historial")
            btn_history.setObjectName("small")
            btn_history.setFixedHeight(30)
            btn_history.clicked.connect(lambda checked, cid=c["id"]: self.show_history(cid))
            btn_layout.addWidget(btn_history)

            btn_del = QPushButton("Borrar")
            btn_del.setObjectName("small")
            btn_del.setFixedHeight(30)
            btn_del.setStyleSheet("background-color: #8b0000; font-size: 14px; padding: 4px 10px;")
            btn_del.clicked.connect(lambda checked, cid=c["id"]: self.delete_cliente(cid))
            btn_layout.addWidget(btn_del)

            self.table.setCellWidget(i, 5, btn_widget)

        self.table.setColumnHidden(0, True)

    def add_cliente(self):
        dialog = ClientDialog(self.db)
        if dialog.exec():
            self.refresh()

    def edit_cliente(self, cliente_id):
        cliente = self.db.fetch_one("SELECT * FROM clientes WHERE id=?", [cliente_id])
        if cliente:
            dialog = ClientDialog(self.db, cliente)
            if dialog.exec():
                self.refresh()

    def delete_cliente(self, cliente_id):
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar este cliente?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete("clientes", "id=?", [cliente_id])
            self.refresh()

    def show_history(self, cliente_id):
        cliente = self.db.fetch_one("SELECT * FROM clientes WHERE id=?", [cliente_id])
        if not cliente:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Historial - {cliente['nombre']}")
        dialog.setMinimumSize(700, 400)
        layout = QVBoxLayout(dialog)

        info = QLabel(f"Cliente: {cliente['nombre']} | Tel: {cliente['telefono'] or '—'} | Correo: {cliente['correo'] or '—'}")
        info.setStyleSheet("font-size: 14px; padding: 8px;")
        layout.addWidget(info)

        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Estado", "Fecha", "Total", "Pago", "Estado Pago"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.verticalHeader().setVisible(False)

        pedidos = self.db.fetch_all(
            """SELECT cp.*, COALESCE(p.nombre, cp.nombre_personalizado) as prod_nombre
               FROM clientes_productos cp
               LEFT JOIN productos p ON cp.producto_id = p.id
               WHERE cp.cliente_id=?
               ORDER BY cp.fecha_pedido DESC""",
            [cliente_id]
        )
        table.setRowCount(len(pedidos))
        for i, ped in enumerate(pedidos):
            table.setItem(i, 0, QTableWidgetItem(ped["prod_nombre"] or "—"))
            table.setItem(i, 1, QTableWidgetItem(str(ped["cantidad"])))
            table.setItem(i, 2, QTableWidgetItem(ped["estado"]))
            table.setItem(i, 3, QTableWidgetItem(ped["fecha_pedido"][:10] if ped["fecha_pedido"] else ""))
            table.setItem(i, 4, QTableWidgetItem(f"Q{ped['precio_final']:.2f}" if ped["precio_final"] else "—"))
            table.setItem(i, 5, QTableWidgetItem(f"Q{ped['pago_total']:.2f}" if ped["pago_total"] else "—"))
            table.setItem(i, 6, QTableWidgetItem(ped["estado_pago"] or "—"))

        layout.addWidget(table)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(dialog.accept)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignRight)
        dialog.exec()
