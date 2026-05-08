"""
Script de migración: inventariobd.xls → zuri.db
Ejecutar desde la carpeta raíz del proyecto:
    python migrar_inventario.py

Requisitos:
- Coloca inventariobd.xls en la misma carpeta que este script
- El archivo zuri.db debe existir (ejecuta main.py al menos una vez primero)
"""

import sqlite3
import os

# ── CONFIGURACIÓN ─────────────────────────────────────────────
ARCHIVO_XLS  = "inventariobd.xls"
ARCHIVO_DB   = "database/zuri.db"

# ── VERIFICACIONES ────────────────────────────────────────────
if not os.path.exists(ARCHIVO_XLS):
    print(f"❌ No se encontró el archivo: {ARCHIVO_XLS}")
    exit()

if not os.path.exists(ARCHIVO_DB):
    print(f"❌ No se encontró la base de datos: {ARCHIVO_DB}")
    print("   Ejecuta main.py primero para crear la BD.")
    exit()

# ── LECTURA DEL ARCHIVO ───────────────────────────────────────
with open(ARCHIVO_XLS, encoding='iso-8859-1') as f:
    lines = f.readlines()

print(f"📄 Archivo leído: {len(lines) - 1} productos encontrados.")

# ── CONEXIÓN A LA BD ──────────────────────────────────────────
con = sqlite3.connect(ARCHIVO_DB)
con.row_factory = sqlite3.Row
cur = con.cursor()

# ── OBTENER O CREAR CATEGORÍAS ───────────────────────────────
def obtener_o_crear_categoria(nombre):
    nombre = nombre.strip()
    if nombre == "- Sin Departamento -" or not nombre:
        nombre = "General"
    nombre = nombre.capitalize()
    cur.execute("SELECT id_categoria FROM categoria WHERE nombre_categoria = ?", (nombre,))
    row = cur.fetchone()
    if row:
        return row["id_categoria"]
    cur.execute("INSERT INTO categoria(nombre_categoria) VALUES(?)", (nombre,))
    return cur.lastrowid

# ── MIGRACIÓN ─────────────────────────────────────────────────
insertados  = 0
omitidos    = 0
actualizados = 0

for i, linea in enumerate(lines[1:], start=2):  # saltar encabezado
    cols = linea.strip().split('\t')
    if len(cols) < 8:
        continue

    codigo   = cols[0].strip()
    nombre   = cols[1].strip().title()  # Primera letra mayúscula por palabra
    p_costo  = cols[2].strip().replace('$', '').replace(',', '')
    p_venta  = cols[3].strip().replace('$', '').replace(',', '')
    stock    = cols[5].strip()
    stk_min  = cols[6].strip()
    depto    = cols[7].strip()

    # Convertir valores
    try:
        precio_costo = float(p_costo) if p_costo else 0.0
    except:
        precio_costo = 0.0

    try:
        precio_venta = float(p_venta) if p_venta else 0.0
    except:
        precio_venta = 0.0

    try:
        stock_actual = int(float(stock)) if stock not in ('N/A', '', 'N') else 0
    except:
        stock_actual = 0

    try:
        stock_minimo = int(float(stk_min)) if stk_min else 5
    except:
        stock_minimo = 5

    if stock_minimo == 0:
        stock_minimo = 5  # mínimo razonable por defecto

    if not nombre:
        omitidos += 1
        continue

    id_cat = obtener_o_crear_categoria(depto)

    # Verificar si ya existe por código de barras o nombre
    cur.execute("""
        SELECT id_producto FROM producto
        WHERE codigo_barras = ? OR nombre = ?
    """, (codigo, nombre))
    existe = cur.fetchone()

    if existe:
        # Actualizar precio si ya existe
        cur.execute("""
            UPDATE producto SET
                precio_venta = ?,
                precio_costo = ?,
                id_categoria = ?
            WHERE id_producto = ?
        """, (precio_venta, precio_costo, id_cat, existe["id_producto"]))
        actualizados += 1
    else:
        cur.execute("""
            INSERT INTO producto(
                codigo_barras, nombre, precio_venta, precio_costo,
                stock_actual, stock_minimo, id_categoria
            ) VALUES(?, ?, ?, ?, ?, ?, ?)
        """, (codigo, nombre, precio_venta, precio_costo,
              stock_actual, stock_minimo, id_cat))
        insertados += 1

con.commit()
con.close()

# ── RESUMEN ───────────────────────────────────────────────────
print()
print("=" * 45)
print("✅ MIGRACIÓN COMPLETADA")
print("=" * 45)
print(f"  Productos insertados:   {insertados}")
print(f"  Productos actualizados: {actualizados}")
print(f"  Productos omitidos:     {omitidos}")
print(f"  TOTAL procesados:       {insertados + actualizados + omitidos}")
print("=" * 45)
print()
print("Abre el sistema y ve a Inventario para verificar.")
