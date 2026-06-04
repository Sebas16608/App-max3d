import sqlite3
import os
from datetime import datetime


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT,
                direccion TEXT,
                correo TEXT,
                notas TEXT,
                fecha_creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                categoria_id INTEGER,
                imagen TEXT,
                material_principal TEXT,
                peso_estimado REAL DEFAULT 0,
                horas_impresion REAL DEFAULT 0,
                pintado INTEGER DEFAULT 0,
                color_pintura TEXT,
                costo_pintura REAL DEFAULT 0,
                modelado_por_mi INTEGER DEFAULT 0,
                horas_modelado REAL DEFAULT 0,
                precio_personalizado REAL,
                activo INTEGER DEFAULT 1,
                fecha_creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id)
            );

            CREATE TABLE IF NOT EXISTS clientes_productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER NOT NULL,
                producto_id INTEGER,
                nombre_personalizado TEXT,
                cantidad INTEGER DEFAULT 1,
                estado TEXT DEFAULT 'Pendiente',
                fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_entrega DATE,
                notas TEXT,
                pintado INTEGER DEFAULT 0,
                color_pintura TEXT,
                costo_pintura REAL DEFAULT 0,
                modelado_por_mi INTEGER DEFAULT 0,
                horas_modelado REAL DEFAULT 0,
                costo_modelado REAL DEFAULT 0,
                material_principal TEXT,
                peso_real REAL DEFAULT 0,
                horas_impresion_real REAL DEFAULT 0,
                costo_material REAL DEFAULT 0,
                costo_luz REAL DEFAULT 0,
                costo_desgaste REAL DEFAULT 0,
                costo_total REAL DEFAULT 0,
                trabajo REAL DEFAULT 0,
                precio_sugerido REAL DEFAULT 0,
                precio_final REAL DEFAULT 0,
                pago_anticipo REAL DEFAULT 0,
                pago_total REAL DEFAULT 0,
                estado_pago TEXT DEFAULT 'Sin pagar',
                fecha_pago DATE,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            );

            CREATE TABLE IF NOT EXISTS filamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                marca TEXT,
                tipo TEXT,
                color TEXT,
                peso_disponible REAL DEFAULT 0,
                precio_compra REAL DEFAULT 0,
                precio_por_gramo REAL DEFAULT 0,
                fecha_creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS pinturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marca TEXT,
                tipo TEXT,
                color TEXT,
                cantidad_disponible REAL DEFAULT 0,
                precio_compra REAL DEFAULT 0,
                fecha_creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS otros_materiales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cantidad REAL DEFAULT 0,
                costo REAL DEFAULT 0,
                fecha_creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS inventario_movimientos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                item_id INTEGER,
                item_tipo TEXT,
                cantidad REAL,
                descripcion TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS inversiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE DEFAULT CURRENT_DATE,
                categoria TEXT NOT NULL,
                descripcion TEXT,
                monto REAL DEFAULT 0,
                fecha_creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS metas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                monto_objetivo REAL DEFAULT 0,
                monto_actual REAL DEFAULT 0,
                completada INTEGER DEFAULT 0,
                fecha_creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS configuracion (
                clave TEXT PRIMARY KEY,
                valor TEXT
            );
        """)
        self.conn.commit()

        self._migrate_schema()
        self._seed_default_data()

    def _migrate_schema(self):
        cursor = self.conn.cursor()
        for table, col in [("filamentos", "categoria"), ("pinturas", "categoria")]:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} TEXT DEFAULT ''")
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    def _seed_default_data(self):
        cursor = self.conn.cursor()
        cats = ["Figuras", "Llaveros", "Soportes", "Accesorios", "Personalizados", "Electrónica", "Hogar", "Otros"]
        for c in cats:
            cursor.execute("INSERT OR IGNORE INTO categorias (nombre) VALUES (?)", (c,))
        self.conn.commit()

    def execute(self, query, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor

    def fetch_all(self, query, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def fetch_one(self, query, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()

    def insert(self, table, data):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self.conn.cursor()
        cursor.execute(query, list(data.values()))
        self.conn.commit()
        return cursor.lastrowid

    def update(self, table, data, where, where_params=None):
        set_clause = ", ".join([f"{k}=?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        params = list(data.values())
        if where_params:
            params.extend(where_params)
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor.rowcount

    def delete(self, table, where, params=None):
        query = f"DELETE FROM {table} WHERE {where}"
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor.rowcount

    def close(self):
        self.conn.close()
