import sqlite3
import os

# Ruta donde se guardará el archivo de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "zuri.db")


def get_conexion():
    """Retorna una conexión a la base de datos."""
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row   # permite acceder a columnas por nombre
    con.execute("PRAGMA foreign_keys = ON")
    return con


def inicializar_bd():
    """Crea todas las tablas si no existen y carga datos iniciales."""
    con = get_conexion()
    cur = con.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS categoria (
            id_categoria     INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_categoria TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre     TEXT NOT NULL,
            rol        TEXT NOT NULL CHECK(rol IN ('dueño','cajero')),
            usuario    TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS proveedor (
            id_proveedor        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre              TEXT NOT NULL,
            telefono            TEXT,
            productos_que_surte TEXT
        );

        CREATE TABLE IF NOT EXISTS producto (
            id_producto   INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_barras TEXT UNIQUE,
            nombre        TEXT NOT NULL,
            precio_venta  REAL NOT NULL,
            precio_costo  REAL NOT NULL,
            stock_actual  INTEGER NOT NULL DEFAULT 0,
            stock_minimo  INTEGER NOT NULL DEFAULT 5,
            id_categoria  INTEGER,
            FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria)
        );

        CREATE TABLE IF NOT EXISTS venta (
            id_venta   INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL DEFAULT (datetime('now')),
            total      REAL NOT NULL,
            id_usuario INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        );

        CREATE TABLE IF NOT EXISTS detalle_venta (
            id_detalle      INTEGER PRIMARY KEY AUTOINCREMENT,
            id_venta        INTEGER NOT NULL,
            id_producto     INTEGER NOT NULL,
            cantidad        INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal        REAL NOT NULL,
            FOREIGN KEY (id_venta)    REFERENCES venta(id_venta),
            FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
        );

        CREATE TABLE IF NOT EXISTS compra (
            id_compra    INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha        TEXT NOT NULL,
            total        REAL NOT NULL,
            id_proveedor INTEGER NOT NULL,
            id_usuario   INTEGER NOT NULL,
            FOREIGN KEY (id_proveedor) REFERENCES proveedor(id_proveedor),
            FOREIGN KEY (id_usuario)   REFERENCES usuario(id_usuario)
        );

        CREATE TABLE IF NOT EXISTS detalle_compra (
            id_detalle_c    INTEGER PRIMARY KEY AUTOINCREMENT,
            id_compra       INTEGER NOT NULL,
            id_producto     INTEGER NOT NULL,
            cantidad        INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal        REAL NOT NULL,
            FOREIGN KEY (id_compra)   REFERENCES compra(id_compra),
            FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
        );

        CREATE TABLE IF NOT EXISTS caja (
            id_corte     INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha        TEXT NOT NULL,
            total_ventas REAL NOT NULL,
            total_gastos REAL NOT NULL DEFAULT 0.0,
            saldo_final  REAL NOT NULL,
            id_usuario   INTEGER NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
        );
    """)

    # Datos iniciales solo si las tablas están vacías
    cur.execute("SELECT COUNT(*) FROM categoria")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO categoria(nombre_categoria) VALUES(?)", [
            ('Abarrotes',), ('Bebidas',), ('Limpieza',),
            ('Dulcería',),  ('Lácteos',),
        ])

    cur.execute("SELECT COUNT(*) FROM usuario")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO usuario(nombre,rol,usuario,contrasena) VALUES(?,?,?,?)", [
            ('Heidi Bustamante', 'dueño',  'heidi',  'admin123'),
            ('Cajera 1',         'cajero', 'cajera', 'cajero123'),
        ])
    cur.execute("SELECT COUNT(*) FROM producto")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO producto(codigo_barras,nombre,precio_venta,precio_costo,stock_actual,stock_minimo,id_categoria) VALUES(?,?,?,?,?,?,?)", [
            ('7501000001','Arroz 1kg',          18.00,13.00,30, 5,1),
            ('7501000002','Frijol 1kg',         22.00,16.00,25, 5,1),
            ('7501000003','Aceite 1L',          35.00,27.00,15, 3,1),
            ('7501000004','Refresco Coca 600ml',16.00,11.00,48,10,2),
            ('7501000005','Agua 1.5L',          14.00, 9.00,36,10,2),
            ('7501000006','Jabon de barra',     12.00, 8.00,20, 5,3),
            ('7501000007','Sabritas original',  18.00,13.00,40, 8,4),
            ('7501000008','Leche 1L',           24.00,18.00,18, 5,5),
        ])
    con.commit()
    con.close()
    print(f"✅ Base de datos lista en: {DB_PATH}")


# Prueba rápida — solo se ejecuta si corres este archivo directamente
if __name__ == "__main__":
    inicializar_bd()
    con = get_conexion()
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [r[0] for r in cur.fetchall()]
    print(f"Tablas creadas: {tablas}")
    con.close()