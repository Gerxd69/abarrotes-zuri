import customtkinter as ctk
from database.conexion import get_conexion
from datetime import date, timedelta


class ReportesFrame(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="#F0F4FA", corner_radius=0)
        self.user = user
        self._build_ui()
        self._cargar_reporte()

    def _build_ui(self):
        ctk.CTkLabel(self, text="📊 Reportes",
                     font=("Arial", 20, "bold"),
                     text_color="#1F497D").pack(anchor="w", padx=20, pady=(20, 10))

        filtros = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        filtros.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(filtros, text="Período:",
                     font=("Arial", 12, "bold"),
                     text_color="#333333").pack(side="left", padx=(15, 8), pady=12)

        self.periodo = ctk.CTkSegmentedButton(filtros,
            values=["Hoy", "Esta semana", "Este mes", "Todo"],
            command=lambda v: self._cargar_reporte())
        self.periodo.set("Hoy")
        self.periodo.pack(side="left", pady=12)

        ctk.CTkButton(filtros, text="🔄 Actualizar", width=110, height=34,
                      fg_color="#1F497D", hover_color="#16375e",
                      font=("Arial", 12),
                      command=self._cargar_reporte).pack(side="right", padx=15, pady=12)

        self.frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cards.pack(fill="x", padx=20, pady=(0, 10))

        self.card_ventas   = self._tarjeta("Total ventas",   "$0.00", "#2E7D32")
        self.card_ingresos = self._tarjeta("Ingresos netos", "$0.00", "#1F497D")
        self.card_cantidad = self._tarjeta("N° de ventas",   "0",     "#E65100")
        self.card_producto = self._tarjeta("Producto top",   "—",     "#6A1B9A")

        tablas = ctk.CTkFrame(self, fg_color="transparent")
        tablas.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._tabla_ventas(tablas)
        self._tabla_productos(tablas)

    def _tarjeta(self, titulo, valor, color):
        frame = ctk.CTkFrame(self.frame_cards, fg_color="white",
                              corner_radius=10, width=200)
        frame.pack(side="left", padx=(0, 10), fill="y")
        frame.pack_propagate(False)

        ctk.CTkLabel(frame, text=titulo,
                     font=("Arial", 10), text_color="#666666").pack(anchor="w", padx=12, pady=(10, 0))
        lbl = ctk.CTkLabel(frame, text=valor,
                            font=("Arial", 16, "bold"), text_color=color)
        lbl.pack(anchor="w", padx=12, pady=(0, 10))
        return lbl

    def _tabla_ventas(self, parent):
        panel = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(panel, text="🧾 Últimas ventas",
                     font=("Arial", 13, "bold"),
                     text_color="#333333").pack(anchor="w", padx=15, pady=(12, 8))

        headers = ["Fecha",  "Total",  "Cajero"]
        anchos  = [150,      100,      150]

        hf = ctk.CTkFrame(panel, fg_color="#1F497D", corner_radius=0, height=32)
        hf.pack(fill="x", padx=10)
        hf.pack_propagate(False)

        for i, (h, w) in enumerate(zip(headers, anchos)):
            ctk.CTkLabel(hf, text=h, width=w,
                         font=("Arial", 11, "bold"),
                         text_color="white").grid(row=0, column=i, padx=4, pady=4)

        self.scroll_ventas = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.scroll_ventas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _tabla_productos(self, parent):
        panel = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, width=320)
        panel.pack(side="left", fill="both")
        panel.pack_propagate(False)

        ctk.CTkLabel(panel, text="📦 Productos más vendidos",
                     font=("Arial", 13, "bold"),
                     text_color="#333333").pack(anchor="w", padx=15, pady=(12, 8))

        headers = ["Producto",  "Vendidos",  "Ingresos"]
        anchos  = [130,         80,          90]

        hf = ctk.CTkFrame(panel, fg_color="#1F497D", corner_radius=0, height=32)
        hf.pack(fill="x", padx=10)
        hf.pack_propagate(False)

        for i, (h, w) in enumerate(zip(headers, anchos)):
            ctk.CTkLabel(hf, text=h, width=w,
                         font=("Arial", 11, "bold"),
                         text_color="white").grid(row=0, column=i, padx=4, pady=4)

        self.scroll_productos = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.scroll_productos.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _get_fechas(self):
        hoy = date.today()
        periodo = self.periodo.get()
        if periodo == "Hoy":
            return hoy.isoformat(), hoy.isoformat()
        elif periodo == "Esta semana":
            inicio = hoy - timedelta(days=hoy.weekday())
            return inicio.isoformat(), hoy.isoformat()
        elif periodo == "Este mes":
            inicio = hoy.replace(day=1)
            return inicio.isoformat(), hoy.isoformat()
        else:
            return "2000-01-01", hoy.isoformat()

    def _cargar_reporte(self):
        inicio, fin = self._get_fechas()
        con = get_conexion()
        cur = con.cursor()

        cur.execute("""
            SELECT COUNT(*) as num_ventas, COALESCE(SUM(total), 0) as total_ventas
            FROM venta
            WHERE substr(fecha_hora, 1, 10) BETWEEN ? AND ?
        """, (inicio, fin))
        resumen = cur.fetchone()

        cur.execute("""
            SELECT COALESCE(SUM(dv.subtotal - (dv.cantidad * p.precio_costo)), 0)
            FROM detalle_venta dv
            JOIN producto p ON dv.id_producto = p.id_producto
            JOIN venta v ON dv.id_venta = v.id_venta
            WHERE substr(v.fecha_hora, 1, 10) BETWEEN ? AND ?
        """, (inicio, fin))
        ingresos_netos = cur.fetchone()[0]

        cur.execute("""
            SELECT p.nombre, SUM(dv.cantidad) as total
            FROM detalle_venta dv
            JOIN producto p ON dv.id_producto = p.id_producto
            JOIN venta v ON dv.id_venta = v.id_venta
            WHERE substr(v.fecha_hora, 1, 10) BETWEEN ? AND ?
            GROUP BY p.id_producto
            ORDER BY total DESC LIMIT 1
        """, (inicio, fin))
        top = cur.fetchone()

        self.card_ventas.configure(text=f"${resumen['total_ventas']:.2f}")
        self.card_ingresos.configure(text=f"${ingresos_netos:.2f}")
        self.card_cantidad.configure(text=str(resumen['num_ventas']))
        self.card_producto.configure(text=top["nombre"] if top else "—")

        cur.execute("""
            SELECT v.fecha_hora, v.total, u.nombre
            FROM venta v
            JOIN usuario u ON v.id_usuario = u.id_usuario
            WHERE substr(v.fecha_hora, 1, 10) BETWEEN ? AND ?
            ORDER BY v.fecha_hora DESC
            LIMIT 50
        """, (inicio, fin))
        ventas = cur.fetchall()

        for w in self.scroll_ventas.winfo_children():
            w.destroy()

        anchos_v = [150, 100, 150]
        for i, row in enumerate(ventas):
            bg = "#F7F9FC" if i % 2 == 0 else "white"
            fila = ctk.CTkFrame(self.scroll_ventas, fg_color=bg, height=30, corner_radius=0)
            fila.pack(fill="x")
            fila.pack_propagate(False)
            for j, (val, w) in enumerate(zip(
                [row["fecha_hora"][:16], f"${row['total']:.2f}", row["nombre"]],
                anchos_v
            )):
                ctk.CTkLabel(fila, text=val, width=w,
                             font=("Arial", 10),
                             text_color="#333333").grid(row=0, column=j, padx=4, pady=3)

        cur.execute("""
            SELECT p.nombre, SUM(dv.cantidad) as vendidos,
                   SUM(dv.subtotal) as ingresos
            FROM detalle_venta dv
            JOIN producto p ON dv.id_producto = p.id_producto
            JOIN venta v ON dv.id_venta = v.id_venta
            WHERE substr(v.fecha_hora, 1, 10) BETWEEN ? AND ?
            GROUP BY p.id_producto
            ORDER BY vendidos DESC
            LIMIT 20
        """, (inicio, fin))
        productos = cur.fetchall()
        con.close()

        for w in self.scroll_productos.winfo_children():
            w.destroy()

        anchos_p = [130, 80, 90]
        for i, row in enumerate(productos):
            bg = "#F7F9FC" if i % 2 == 0 else "white"
            fila = ctk.CTkFrame(self.scroll_productos, fg_color=bg, height=30, corner_radius=0)
            fila.pack(fill="x")
            fila.pack_propagate(False)
            for j, (val, w) in enumerate(zip(
                [row["nombre"][:16], str(row["vendidos"]), f"${row['ingresos']:.2f}"],
                anchos_p
            )):
                ctk.CTkLabel(fila, text=val, width=w,
                             font=("Arial", 10),
                             text_color="#333333").grid(row=0, column=j, padx=4, pady=3)