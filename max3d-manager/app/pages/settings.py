from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFormLayout, QDoubleSpinBox, QComboBox, QGroupBox,
    QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt


class SettingsPage(QWidget):
    def __init__(self, db, config, parent=None):
        super().__init__(parent)
        self.db = db
        self.config = config
        self.setup_ui()

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Configuración")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e94560;")
        layout.addWidget(title)

        costos_group = QGroupBox("Costos")
        costos_form = QFormLayout(costos_group)
        costos_form.setSpacing(10)

        self.modelado_costo = QDoubleSpinBox()
        self.modelado_costo.setRange(0, 999)
        self.modelado_costo.setPrefix("Q ")
        self.modelado_costo.setDecimals(2)
        self.modelado_costo.setValue(self.config.get("modelado_costo_hora", 25))
        costos_form.addRow("Costo por hora de modelado:", self.modelado_costo)

        self.desgaste_costo = QDoubleSpinBox()
        self.desgaste_costo.setRange(0, 99)
        self.desgaste_costo.setPrefix("Q ")
        self.desgaste_costo.setDecimals(2)
        self.desgaste_costo.setValue(self.config.get("desgaste_costo_hora", 0.75))
        costos_form.addRow("Costo desgaste por hora:", self.desgaste_costo)

        self.electricidad_costo = QDoubleSpinBox()
        self.electricidad_costo.setRange(0, 1)
        self.electricidad_costo.setPrefix("Q ")
        self.electricidad_costo.setDecimals(6)
        self.electricidad_costo.setSingleStep(0.00001)
        self.electricidad_costo.setValue(self.config.get("electricidad_costo", 0.000153))
        costos_form.addRow("Costo electricidad por Watt:", self.electricidad_costo)

        layout.addWidget(costos_group)

        trabajo_group = QGroupBox("Trabajo")
        trabajo_form = QFormLayout(trabajo_group)
        trabajo_form.setSpacing(10)

        self.trabajo_porcentaje = QDoubleSpinBox()
        self.trabajo_porcentaje.setRange(0, 100)
        self.trabajo_porcentaje.setSuffix(" %")
        self.trabajo_porcentaje.setDecimals(1)
        self.trabajo_porcentaje.setValue(self.config.get("trabajo_porcentaje", 20))
        trabajo_form.addRow("Porcentaje de trabajo:", self.trabajo_porcentaje)

        layout.addWidget(trabajo_group)

        redondeo_group = QGroupBox("Redondeo de Precios")
        redondeo_form = QFormLayout(redondeo_group)
        redondeo_form.setSpacing(10)

        self.redondeo = QComboBox()
        self.redondeo.addItem("Sin redondeo", 0)
        self.redondeo.addItem("Redondeo Q1", 1)
        self.redondeo.addItem("Redondeo Q5", 5)
        self.redondeo.addItem("Redondeo Q10", 10)
        idx = self.redondeo.findData(self.config.get("redondeo", 5))
        if idx >= 0:
            self.redondeo.setCurrentIndex(idx)
        redondeo_form.addRow("Regla de redondeo:", self.redondeo)

        layout.addWidget(redondeo_group)

        btn_save = QPushButton("Guardar Configuración")
        btn_save.setStyleSheet("background-color: #006400; padding: 12px 24px; font-size: 16px;")
        btn_save.clicked.connect(self.guardar)
        layout.addWidget(btn_save, alignment=Qt.AlignCenter)

        layout.addStretch()

        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def guardar(self):
        self.config.set("modelado_costo_hora", self.modelado_costo.value())
        self.config.set("desgaste_costo_hora", self.desgaste_costo.value())
        self.config.set("electricidad_costo", self.electricidad_costo.value())
        self.config.set("trabajo_porcentaje", self.trabajo_porcentaje.value())
        self.config.set("redondeo", self.redondeo.currentData())
        QMessageBox.information(self, "Configuración", "Configuración guardada exitosamente")
