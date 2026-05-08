import customtkinter as ctk
from database.conexion import get_conexion
from datetime import datetime


class ComprasFrame(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="#F0F4FA", corner_radius=0)
        self.user = user
        self.detalle = []  # productos de la compra actual
        self._build_ui()
        self._cargar_historial()

    def _build_ui(self):
        ctk.CTkLabel(self, text="🛒 Registro de Compras",
                     font=("Arial", 20, "bold"),
                     text_color="#1F497D").pack(anchor="w", padx=20, pady=(20, 10))

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=5)

        self._panel_formulario(cuerpo)
        self._panel_historial(cuerpo)

    # ── PANEL IZQUIERDO: formulario de compra ────────────────
    def _panel_formulario(self, parent):
        panel = ctk.CTkScrollableFrame(parent, fg_color="white",
                                        corner_radius=10, width=340)
        panel.pack(side="left", fill="y", padx=(0, 10))

        ctk.CTkLabel(panel, text="Nueva compra",
                     font=("Arial", 14, "bold"),
                     text_color="#1F497D").pack(anchor="w", padx=15, pady=(15, 10))

        # Proveedor
        ctk.CTkLabel(panel, text="Proveedor:",
                     font=("Arial", 12, "bold"),
                     text_color="#333333").pack(anchor="w", padx=15)

        self.combo_proveedor = ctk.CTkComboBox(panel, height=36,
                                                font=("Arial", 12),
                                                state="readonly")
        self.combo_proveedor.pack(fill="x", padx=15, pady=(3, 10))
        self._cargar_proveedores()

        ctk.CTkLabel(panel, text="─" * 30,
                     text_color="#DDDDDD").pack(pady=5)

        # Agregar producto
        ctk.CTkLabel(panel, text="Agregar producto:",
                     font=("Arial", 12, "bold"),
                     text_color="#333333").pack(anchor="w", padx=15)

        self.frame_busq = ctk.CTkFrame(panel, fg_color="transparent")
        self.frame_busq.pack(fill="x", padx=15, pady=(3, 5))

        self.entry_buscar = ctk.CTkEntry(self.frame_busq, height=34,
                                          placeholder_text="Nombre o código...",
                                          font=("Arial", 11))
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.entry_buscar.bind("<Return>", lambda e: self._buscar_producto())
        self.entry_buscar.bind("<KeyRelease>", self._autocompletar)

        ctk.CTkButton(self.frame_busq, text="Buscar", width=70, height=34,
                      fg_color="#1F497D", hover_color="#16375e",
                      font=("Arial", 11),
                      command=self._buscar_producto).pack(side="left")

        # Sugerencias - van dentro del panel principal del módulo (no del scroll)
        self.panel_ref = panel
        self.lista_sugerencias = ctk.CTkFrame(panel, fg_color="white",
                                               corner_radius=8,
                                               border_width=1,
                                               border_color="#DDDDDD")
        self.lista_sugerencias.pack(fill="x", padx=15)
        self.lista_sugerencias.pack_forget()

        # Info producto encontrado
        self.lbl_producto = ctk.CTkLabel(panel, text="—",
                                          font=("Arial", 11, "bold"),
                                          text_color="#1F497D")
        self.lbl_producto.pack(anchor="w", padx=15)

        # Cantidad y precio costo
        frame_cant = ctk.CTkFrame(panel, fg_color="transparent")
        frame_cant.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(frame_cant, text="Cantidad:",
                     font=("Arial", 11)).pack(side="left")
        self.entry_cantidad = ctk.CTkEntry(frame_cant, width=60, height=32,
                                            font=("Arial", 11))
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.pack(side="left", padx=(5, 15))

        ctk.CTkLabel(frame_cant, text="P.Costo:",
                     font=("Arial", 11)).pack(side="left")
        self.entry_costo = ctk.CTkEntry(frame_cant, width=70, height=32,
                                         font=("Arial", 11))
        self.entry_costo.pack(side="left", padx=(5, 0))

        self.lbl_err = ctk.CTkLabel(panel, text="", text_color="#C0392B",
                                     font=("Arial", 11))
        self.lbl_err.pack()

        ctk.CTkButton(panel, text="➕ Agregar",
                      height=34, fg_color="#2E7D32", hover_color="#1B5E20",
                      font=("Arial", 12),
                      command=self._agregar_producto).pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(panel, text="─" * 30,
                     text_color="#DDDDDD").pack(pady=5)

        # Lista de productos agregados
        ctk.CTkLabel(panel, text="Productos en esta compra:",
                     font=("Arial", 11, "bold"),
                     text_color="#333333").pack(anchor="w", padx=15)

        self.lista_compra = ctk.CTkScrollableFrame(panel, height=150,
                                                    fg_color="#F9F9F9",
                                                    corner_radius=6)
        self.lista_compra.pack(fill="x", padx=15, pady=5)

        self.lbl_total = ctk.CTkLabel(panel, text="Total: $0.00",
                                       font=("Arial", 14, "bold"),
                                       text_color="#1F497D")
        self.lbl_total.pack(pady=5)

        ctk.CTkButton(panel, text="✅ Registrar compra",
                      height=42, fg_color="#1F497D", hover_color="#16375e",
                      font=("Arial", 13, "bold"),
                      command=self._registrar_compra).pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkButton(panel, text="🗑 Cancelar",
                      height=34, fg_color="#C0392B", hover_color="#922B21",
                      font=("Arial", 12),
                      command=self._cancelar).pack(fill="x", padx=15, pady=(0, 15))

        self.producto_actual = None

    # ── PANEL DERECHO: historial ─────────────────────────────
    def _panel_historial(self, parent):
        panel = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        panel.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(panel, text="📋 Historial de compras",
                     font=("Arial", 13, "bold"),
                     text_color="#333333").pack(anchor="w", padx=15, pady=(15, 8))

        headers = ["Fecha",     "Proveedor",  "Total",   "Registró"]
        anchos  = [120,         200,          90,        150]

        hf = ctk.CTkFrame(panel, fg_color="#1F497D", corner_radius=0, height=32)
        hf.pack(fill="x", padx=10)
        hf.pack_propagate(False)

        for i, (h, w) in enumerate(zip(headers, anchos)):
            ctk.CTkLabel(hf, text=h, width=w,
                         font=("Arial", 11, "bold"),
                         text_color="white").grid(row=0, column=i, padx=4, pady=4)

        self.scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ── LÓGICA ───────────────────────────────────────────────
    def _cargar_proveedores(self):
        con = get_conexion()
        cur = con.cursor()
        cur.execute("SELECT id_proveedor, nombre FROM proveedor ORDER BY nombre")
        self.proveedores = {row["nombre"]: row["id_proveedor"] for row in cur.fetchall()}
        con.close()

        nombres = list(self.proveedores.keys())
        self.combo_proveedor.configure(values=nombres)
        if nombres:
            self.combo_proveedor.set(nombres[0])
        else:
            self.combo_proveedor.set("Sin proveedores")
    def _autocompletar(self, event=None):
        termino = self.entry_buscar.get().strip()

        for w in self.lista_sugerencias.winfo_children():
            w.destroy()

        if len(termino) < 2:
            self.lista_sugerencias.pack_forget()
            return

        con = get_conexion()
        cur = con.cursor()
        cur.execute("""
            SELECT id_producto, nombre, precio_costo, stock_actual
            FROM producto
            WHERE nombre LIKE ? OR codigo_barras LIKE ?
            LIMIT 6
        """, (f"%{termino}%", f"%{termino}%"))
        rows = cur.fetchall()
        con.close()

        if not rows:
            self.lista_sugerencias.pack_forget()
            return

        # Mostrar sugerencias justo después del frame de búsqueda
        self.lista_sugerencias.pack(in_=self.panel_ref, fill="x", padx=15,
                                    after=self.frame_busq)
        self.lista_sugerencias.lift()

        for row in rows:
            texto = f"{row['nombre']}  —  Costo: ${row['precio_costo']:.2f}  |  Stock: {row['stock_actual']}"
            btn = ctk.CTkButton(
                self.lista_sugerencias,
                text=texto,
                height=30,
                fg_color="white",
                hover_color="#EBF3FB",
                text_color="#333333",
                anchor="w",
                font=("Arial", 11),
                command=lambda r=dict(row): self._seleccionar_sugerencia(r)
            )
            btn.pack(fill="x", pady=1, padx=2)

    def _seleccionar_sugerencia(self, row):
        self.producto_actual = row
        self.entry_buscar.delete(0, "end")
        self.entry_buscar.insert(0, row["nombre"])
        self.lbl_producto.configure(
            text=f"✅ {row['nombre']} — Stock: {row['stock_actual']}",
            text_color="#2E7D32")
        self.entry_costo.delete(0, "end")
        self.entry_costo.insert(0, str(row["precio_costo"]))
        self.lbl_err.configure(text="")

        for w in self.lista_sugerencias.winfo_children():
            w.destroy()
        self.lista_sugerencias.pack_forget()

        self.entry_cantidad.focus()
        
    def _buscar_producto(self):
        termino = self.entry_buscar.get().strip()
        if not termino:
            return

        con = get_conexion()
        cur = con.cursor()
        cur.execute("""
            SELECT * FROM producto
            WHERE codigo_barras = ? OR nombre LIKE ?
            LIMIT 1
        """, (termino, f"%{termino}%"))
        row = cur.fetchone()
        con.close()

        if row:
            self.producto_actual = dict(row)
            self.lbl_producto.configure(
                text=f"✅ {row['nombre']} — Stock: {row['stock_actual']}",
                text_color="#2E7D32")
            self.entry_costo.delete(0, "end")
            self.entry_costo.insert(0, str(row["precio_costo"]))
            self.lbl_err.configure(text="")
        else:
            self.producto_actual = None
            self.lbl_producto.configure(text="❌ Producto no encontrado.",
                                         text_color="#C0392B")

    def _agregar_producto(self):
        if not self.producto_actual:
            self.lbl_err.configure(text="⚠ Busca un producto primero.")
            return
        try:
            cantidad = int(self.entry_cantidad.get())
            costo    = float(self.entry_costo.get())
            if cantidad <= 0 or costo <= 0:
                raise ValueError
        except ValueError:
            self.lbl_err.configure(text="⚠ Cantidad y costo deben ser números válidos.")
            return

        # Si ya está en la lista, actualizar
        for item in self.detalle:
            if item["id_producto"] == self.producto_actual["id_producto"]:
                item["cantidad"] += cantidad
                item["subtotal"] = item["cantidad"] * item["precio_unitario"]
                self._actualizar_lista()
                self.lbl_err.configure(text="✅ Cantidad actualizada.", text_color="#2E7D32")
                return

        self.detalle.append({
            "id_producto":    self.producto_actual["id_producto"],
            "nombre":         self.producto_actual["nombre"],
            "cantidad":       cantidad,
            "precio_unitario": costo,
            "subtotal":       cantidad * costo,
        })
        self._actualizar_lista()
        self.lbl_err.configure(text="✅ Producto agregado.", text_color="#2E7D32")
        self.entry_buscar.delete(0, "end")
        self.entry_cantidad.delete(0, "end")
        self.entry_cantidad.insert(0, "1")
        self.entry_costo.delete(0, "end")
        self.producto_actual = None
        self.lbl_producto.configure(text="—", text_color="#1F497D")
        self.entry_buscar.focus()

    def _actualizar_lista(self):
        for w in self.lista_compra.winfo_children():
            w.destroy()

        total = 0
        for i, item in enumerate(self.detalle):
            bg = "#EBF3FB" if i % 2 == 0 else "#F9F9F9"
            fila = ctk.CTkFrame(self.lista_compra, fg_color=bg, corner_radius=4)
            fila.pack(fill="x", pady=1, padx=2)

            texto = f"{item['nombre'][:16]} x{item['cantidad']} @${item['precio_unitario']:.2f} = ${item['subtotal']:.2f}"
            ctk.CTkLabel(fila, text=texto, font=("Arial", 10),
                         text_color="#333333", anchor="w").pack(side="left", padx=6, pady=4, fill="x", expand=True)

            ctk.CTkButton(fila, text="✕", width=28, height=24,
                          fg_color="#C0392B", hover_color="#922B21",
                          font=("Arial", 11, "bold"),
                          command=lambda idx=i: self._quitar_producto(idx)
                          ).pack(side="right", padx=4, pady=2)

            total += item["subtotal"]
        self.lbl_total.configure(text=f"Total: ${total:.2f}")

    def _quitar_producto(self, idx):
        if 0 <= idx < len(self.detalle):
            nombre = self.detalle[idx]["nombre"]
            del self.detalle[idx]
            self._actualizar_lista()
            self.lbl_err.configure(text=f"🗑 {nombre} eliminado.", text_color="#888888")

    def _registrar_compra(self):
        if not self.detalle:
            self.lbl_err.configure(text="⚠ Agrega al menos un producto.")
            return

        nombre_prov = self.combo_proveedor.get()
        if nombre_prov not in self.proveedores:
            self.lbl_err.configure(text="⚠ Selecciona un proveedor válido.")
            return

        id_proveedor = self.proveedores[nombre_prov]
        total = sum(i["subtotal"] for i in self.detalle)
        fecha = datetime.now().strftime("%Y-%m-%d")

        con = get_conexion()
        cur = con.cursor()
        try:
            cur.execute("""
                INSERT INTO compra(fecha, total, id_proveedor, id_usuario)
                VALUES(?, ?, ?, ?)
            """, (fecha, total, id_proveedor, self.user["id_usuario"]))
            id_compra = cur.lastrowid

            for item in self.detalle:
                cur.execute("""
                    INSERT INTO detalle_compra(id_compra, id_producto,
                    cantidad, precio_unitario, subtotal)
                    VALUES(?, ?, ?, ?, ?)
                """, (id_compra, item["id_producto"], item["cantidad"],
                      item["precio_unitario"], item["subtotal"]))

                # Actualizar stock y precio costo
                cur.execute("""
                    UPDATE producto SET
                        stock_actual = stock_actual + ?,
                        precio_costo = ?
                    WHERE id_producto = ?
                """, (item["cantidad"], item["precio_unitario"], item["id_producto"]))

            con.commit()
            self._mostrar_confirmacion(total, nombre_prov)
            self.detalle = []
            self._actualizar_lista()
            self._cargar_historial()
            self.lbl_err.configure(text="")
        except Exception as e:
            con.rollback()
            self.lbl_err.configure(text=f"❌ Error: {e}")
        finally:
            con.close()

    def _mostrar_confirmacion(self, total, proveedor):
        win = ctk.CTkToplevel(self)
        win.title("Compra registrada")
        win.geometry("300x180")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="✅", font=("Arial", 40)).pack(pady=(15, 5))
        ctk.CTkLabel(win,
                     text=f"Compra registrada\nProveedor: {proveedor}\nTotal: ${total:.2f}",
                     font=("Arial", 13, "bold"), text_color="#2E7D32").pack()
        ctk.CTkButton(win, text="Cerrar", fg_color="#1F497D",
                      command=win.destroy).pack(pady=12)

    def _cancelar(self):
        self.detalle = []
        self._actualizar_lista()
        self.lbl_err.configure(text="🗑 Compra cancelada.", text_color="#888888")
        self.entry_buscar.delete(0, "end")
        self.producto_actual = None
        self.lbl_producto.configure(text="—", text_color="#1F497D")

    def _cargar_historial(self):
        con = get_conexion()
        cur = con.cursor()
        cur.execute("""
            SELECT c.fecha, p.nombre AS proveedor,
                   c.total, u.nombre AS usuario
            FROM compra c
            JOIN proveedor p ON c.id_proveedor = p.id_proveedor
            JOIN usuario u   ON c.id_usuario   = u.id_usuario
            ORDER BY c.fecha DESC, c.id_compra DESC
            LIMIT 50
        """)
        rows = cur.fetchall()
        con.close()

        for w in self.scroll.winfo_children():
            w.destroy()

        anchos = [120, 200, 90, 150]
        for i, row in enumerate(rows):
            bg = "#F7F9FC" if i % 2 == 0 else "white"
            fila = ctk.CTkFrame(self.scroll, fg_color=bg, height=32, corner_radius=0)
            fila.pack(fill="x")
            fila.pack_propagate(False)

            for j, (val, w) in enumerate(zip(
                [row["fecha"], row["proveedor"], f"${row['total']:.2f}", row["usuario"]],
                anchos
            )):
                ctk.CTkLabel(fila, text=val, width=w,
                             font=("Arial", 11),
                             text_color="#333333").grid(row=0, column=j, padx=4, pady=4)