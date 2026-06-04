from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QGroupBox, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.utils import formatear_moneda


class MetricCard(QFrame):
    def __init__(self, title, value, color="#e94560", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 10px;
                padding: 16px;
                border-left: 4px solid {color};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 13px; color: #a0a0b0; font-weight: normal; border: none;")
        layout.addWidget(self.title_label)

        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {color}; border: none;")
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


class AlertCard(QFrame):
    def __init__(self, message, alert_type="warning", parent=None):
        super().__init__(parent)
        colors = {"warning": "#e94560", "info": "#533483", "success": "#006400"}
        color = colors.get(alert_type, "#e94560")
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #16213e;
                border: 1px solid {color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        layout = QHBoxLayout(self)
        icon = QLabel("⚠️" if alert_type == "warning" else "ℹ️")
        icon.setStyleSheet("font-size: 18px; border: none;")
        layout.addWidget(icon)
        self.msg_label = QLabel(message)
        self.msg_label.setStyleSheet(f"font-size: 13px; color: {color}; border: none;")
        layout.addWidget(self.msg_label, 1)


class DashboardPage(QWidget):
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
        main_layout = QVBoxLayout(content)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e94560;")
        main_layout.addWidget(title)

        subtitle = QLabel("Resumen general del negocio")
        subtitle.setStyleSheet("font-size: 14px; color: #a0a0b0; margin-bottom: 8px;")
        main_layout.addWidget(subtitle)

        pedidos_group = QGroupBox("Estado de Pedidos")
        pedidos_grid = QGridLayout(pedidos_group)
        pedidos_grid.setSpacing(12)

        estados = [
            ("Pendientes", "Pendiente", "#e94560"),
            ("En impresión", "En impresión", "#533483"),
            ("Pintando", "Pintando", "#ff8c00"),
            ("Terminados", "Terminado", "#006400"),
            ("Entregados", "Entregado", "#1a8a4a"),
            ("Cancelados", "Cancelado", "#8b0000"),
        ]

        self.pedido_cards = {}
        for i, (label, estado, color) in enumerate(estados):
            card = MetricCard(label, "0", color)
            pedidos_grid.addWidget(card, i // 3, i % 3)
            self.pedido_cards[estado] = card

        main_layout.addWidget(pedidos_group)

        metricas_group = QGroupBox("Métricas del Mes")
        metricas_grid = QGridLayout(metricas_group)
        metricas_grid.setSpacing(12)

        metricas = [
            ("Ventas del mes", "ventas", "#e94560"),
            ("Ganancia neta", "ganancia_neta", "#00c853"),
            ("Ganancia bruta", "ganancia_bruta", "#00bcd4"),
            ("Total invertido", "invertido", "#ff8c00"),
            ("Material disponible", "material", "#533483"),
            ("Tiempo impresión", "tiempo_impresion", "#e040fb"),
            ("Tiempo modelado", "tiempo_modelado", "#7c4dff"),
        ]

        self.metrica_cards = {}
        for i, (label, key, color) in enumerate(metricas):
            card = MetricCard(label, "0", color)
            metricas_grid.addWidget(card, i // 4, i % 4)
            self.metrica_cards[key] = card

        main_layout.addWidget(metricas_group)

        indicadores_group = QGroupBox("Indicadores")
        indicadores_grid = QGridLayout(indicadores_group)
        indicadores_grid.setSpacing(12)

        indicadores = [
            ("Producto más vendido", "producto_top"),
            ("Producto más rentable", "producto_rentable"),
            ("Cliente que más compra", "cliente_top"),
            ("Material más utilizado", "material_top"),
        ]

        self.indicador_cards = {}
        for i, (label, key) in enumerate(indicadores):
            frame = QFrame()
            frame.setStyleSheet("background-color: #16213e; border: 1px solid #0f3460; border-radius: 8px; padding: 12px;")
            fl = QVBoxLayout(frame)
            lbl = QLabel(label)
            lbl.setStyleSheet("font-size: 12px; color: #a0a0b0; border: none;")
            fl.addWidget(lbl)
            val = QLabel("—")
            val.setStyleSheet("font-size: 16px; font-weight: bold; color: #e0e0e0; border: none;")
            fl.addWidget(val)
            indicadores_grid.addWidget(frame)
            self.indicador_cards[key] = val

        main_layout.addWidget(indicadores_group)

        alertas_group = QGroupBox("Alertas")
        alertas_layout = QVBoxLayout(alertas_group)
        alertas_layout.setSpacing(8)
        self.alertas_container = QVBoxLayout()
        alertas_layout.addLayout(self.alertas_container)

        main_layout.addWidget(alertas_group)

        main_layout.addStretch()

        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh(self):
        db = self.db
        estados = ["Pendiente", "En impresión", "Pintando", "Terminado", "Entregado", "Cancelado"]
        for estado in estados:
            row = db.fetch_one(
                "SELECT COUNT(*) as c FROM clientes_productos WHERE estado=?",
                (estado,)
            )
            if estado in self.pedido_cards:
                self.pedido_cards[estado].set_value(str(row["c"] if row else 0))

        ventas_row = db.fetch_one(
            "SELECT COALESCE(SUM(precio_final),0) as total FROM clientes_productos WHERE estado='Entregado'"
        )
        ventas = ventas_row["total"] if ventas_row else 0
        self.metrica_cards["ventas"].set_value(formatear_moneda(ventas, self.config.get("moneda", "Q")))

        gastos_row = db.fetch_one("SELECT COALESCE(SUM(monto),0) as total FROM inversiones")
        gastos = gastos_row["total"] if gastos_row else 0

        costo_row = db.fetch_one(
            "SELECT COALESCE(SUM(costo_total),0) as total FROM clientes_productos WHERE estado='Entregado'"
        )
        costos = costo_row["total"] if costo_row else 0

        ganancia_bruta = ventas - costos
        ganancia_neta = ganancia_bruta - gastos

        self.metrica_cards["ganancia_bruta"].set_value(formatear_moneda(ganancia_bruta, self.config.get("moneda", "Q")))
        self.metrica_cards["ganancia_neta"].set_value(formatear_moneda(ganancia_neta, self.config.get("moneda", "Q")))
        self.metrica_cards["invertido"].set_value(formatear_moneda(gastos, self.config.get("moneda", "Q")))

        mat_row = db.fetch_one(
            "SELECT COALESCE(SUM(peso_disponible),0) as total FROM filamentos"
        )
        self.metrica_cards["material"].set_value(f"{mat_row['total']:.0f}g" if mat_row else "0g")

        tiempo_imp = db.fetch_one(
            "SELECT COALESCE(SUM(horas_impresion_real),0) as total FROM clientes_productos"
        )
        self.metrica_cards["tiempo_impresion"].set_value(f"{tiempo_imp['total']:.1f}h" if tiempo_imp else "0h")

        tiempo_mod = db.fetch_one(
            "SELECT COALESCE(SUM(horas_modelado),0) as total FROM clientes_productos"
        )
        self.metrica_cards["tiempo_modelado"].set_value(f"{tiempo_mod['total']:.1f}h" if tiempo_mod else "0h")

        prod_top = db.fetch_one("""
            SELECT p.nombre, SUM(cp.cantidad) as total
            FROM clientes_productos cp
            JOIN productos p ON cp.producto_id = p.id
            WHERE cp.estado IN ('Entregado','Terminado')
            GROUP BY cp.producto_id
            ORDER BY total DESC LIMIT 1
        """)
        self.indicador_cards["producto_top"].setText(prod_top["nombre"] if prod_top else "—")

        prod_rent = db.fetch_one("""
            SELECT p.nombre, SUM(cp.precio_final - cp.costo_total) as ganancia
            FROM clientes_productos cp
            JOIN productos p ON cp.producto_id = p.id
            WHERE cp.estado IN ('Entregado','Terminado')
            GROUP BY cp.producto_id
            ORDER BY ganancia DESC LIMIT 1
        """)
        self.indicador_cards["producto_rentable"].setText(prod_rent["nombre"] if prod_rent else "—")

        cli_top = db.fetch_one("""
            SELECT c.nombre, SUM(cp.precio_final) as total
            FROM clientes_productos cp
            JOIN clientes c ON cp.cliente_id = c.id
            WHERE cp.estado IN ('Entregado','Terminado')
            GROUP BY cp.cliente_id
            ORDER BY total DESC LIMIT 1
        """)
        self.indicador_cards["cliente_top"].setText(cli_top["nombre"] if cli_top else "—")

        mat_top = db.fetch_one("""
            SELECT cp.material_principal, COUNT(*) as total
            FROM clientes_productos cp
            WHERE cp.material_principal IS NOT NULL
            GROUP BY cp.material_principal
            ORDER BY total DESC LIMIT 1
        """)
        self.indicador_cards["material_top"].setText(mat_top["material_principal"] if mat_top else "—")

        for i in reversed(range(self.alertas_container.count())):
            w = self.alertas_container.itemAt(i).widget()
            if w:
                w.deleteLater()

        filamentos_bajos = db.fetch_all(
            "SELECT nombre, peso_disponible FROM filamentos WHERE peso_disponible < 200 ORDER BY peso_disponible ASC LIMIT 5"
        )
        for f in filamentos_bajos:
            card = AlertCard(f"Filamento bajo: {f['nombre']} ({f['peso_disponible']}g restantes)", "warning")
            self.alertas_container.addWidget(card)

        pinturas_bajas = db.fetch_all(
            "SELECT color, cantidad_disponible FROM pinturas WHERE cantidad_disponible < 50 ORDER BY cantidad_disponible ASC LIMIT 5"
        )
        for p in pinturas_bajas:
            card = AlertCard(f"Pintura por agotarse: {p['color']} ({p['cantidad_disponible']} restante)", "warning")
            self.alertas_container.addWidget(card)

        if not filamentos_bajos and not pinturas_bajas:
            card = AlertCard("No hay alertas. Inventario en buen estado.", "success")
            self.alertas_container.addWidget(card)
