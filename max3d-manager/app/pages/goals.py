from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QTextEdit, QDoubleSpinBox, QMessageBox,
    QHeaderView, QProgressBar, QGroupBox
)
from PySide6.QtCore import Qt


class GoalDialog(QDialog):
    def __init__(self, db, goal=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.goal = goal
        self.setWindowTitle("Meta" if not goal else "Editar Meta")
        self.setMinimumSize(450, 300)
        self.setup_ui()
        if goal:
            self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre de la meta")
        form.addRow("Nombre:", self.nombre)

        self.descripcion = QTextEdit()
        self.descripcion.setPlaceholderText("Descripción...")
        self.descripcion.setMaximumHeight(80)
        form.addRow("Descripción:", self.descripcion)

        self.monto_objetivo = QDoubleSpinBox()
        self.monto_objetivo.setRange(0, 999999)
        self.monto_objetivo.setPrefix("Q ")
        self.monto_objetivo.setDecimals(2)
        form.addRow("Monto objetivo:", self.monto_objetivo)

        self.monto_actual = QDoubleSpinBox()
        self.monto_actual.setRange(0, 999999)
        self.monto_actual.setPrefix("Q ")
        self.monto_actual.setDecimals(2)
        form.addRow("Monto actual:", self.monto_actual)

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
        self.nombre.setText(self.goal["nombre"])
        self.descripcion.setPlainText(self.goal["descripcion"] or "")
        self.monto_objetivo.setValue(self.goal["monto_objetivo"] or 0)
        self.monto_actual.setValue(self.goal["monto_actual"] or 0)

    def guardar(self):
        if not self.nombre.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        data = {
            "nombre": self.nombre.text().strip(),
            "descripcion": self.descripcion.toPlainText().strip(),
            "monto_objetivo": self.monto_objetivo.value(),
            "monto_actual": self.monto_actual.value(),
            "completada": 1 if self.monto_actual.value() >= self.monto_objetivo.value() else 0,
        }
        if self.goal:
            self.db.update("metas", data, "id=?", [self.goal["id"]])
        else:
            self.db.insert("metas", data)
        self.accept()


class GoalsPage(QWidget):
    def __init__(self, db, config, parent=None):
        super().__init__(parent)
        self.db = db
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QHBoxLayout()
        title = QLabel("Metas")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e94560;")
        header.addWidget(title)
        header.addStretch()
        self.btn_add = QPushButton("+ Nueva Meta")
        self.btn_add.clicked.connect(self.add_goal)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Progreso", "Actual", "Objetivo", "Acciones"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self):
        goals = self.db.fetch_all("SELECT * FROM metas ORDER BY completada ASC, nombre")
        self.table.setRowCount(len(goals))
        for i, g in enumerate(goals):
            self.table.setItem(i, 0, QTableWidgetItem(str(g["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(g["nombre"]))

            progress = 0
            if g["monto_objetivo"] > 0:
                progress = min(100, int((g["monto_actual"] / g["monto_objetivo"]) * 100))

            prog_widget = QWidget()
            prog_layout = QVBoxLayout(prog_widget)
            prog_layout.setContentsMargins(4, 2, 4, 2)
            prog_bar = QProgressBar()
            prog_bar.setValue(progress)
            prog_bar.setFormat(f"{progress}%")
            if progress >= 100:
                prog_bar.setStyleSheet("QProgressBar::chunk { background-color: #00c853; }")
            prog_layout.addWidget(prog_bar)
            self.table.setCellWidget(i, 2, prog_widget)

            self.table.setItem(i, 3, QTableWidgetItem(f"Q{g['monto_actual']:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"Q{g['monto_objetivo']:.2f}"))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_edit = QPushButton("Editar")
            btn_edit.setObjectName("small")
            btn_edit.setFixedHeight(30)
            btn_edit.clicked.connect(lambda checked, gid=g["id"]: self.edit_goal(gid))
            btn_layout.addWidget(btn_edit)
            btn_del = QPushButton("Borrar")
            btn_del.setObjectName("small")
            btn_del.setFixedHeight(30)
            btn_del.setStyleSheet("background-color: #8b0000; font-size: 14px; padding: 4px 10px;")
            btn_del.clicked.connect(lambda checked, gid=g["id"]: self.delete_goal(gid))
            btn_layout.addWidget(btn_del)
            self.table.setCellWidget(i, 5, btn_widget)

        self.table.setColumnHidden(0, True)

    def add_goal(self):
        dialog = GoalDialog(self.db)
        if dialog.exec():
            self.refresh()

    def edit_goal(self, gid):
        goal = self.db.fetch_one("SELECT * FROM metas WHERE id=?", [gid])
        if goal:
            dialog = GoalDialog(self.db, goal)
            if dialog.exec():
                self.refresh()

    def delete_goal(self, gid):
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar esta meta?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete("metas", "id=?", [gid])
            self.refresh()
