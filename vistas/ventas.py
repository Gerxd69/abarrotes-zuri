import customtkinter as ctk
from datetime import datetime
from database.conexion import get_conexion


class VentasFrame(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="#F0F4FA", corner_radius=0)
        self.user = user
        self.ticket = []  # lista de productos en la venta actual

        self._build_ui()

    def _build_ui(self):
        # ── Título ───────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="🧾 Registro de Venta",
            font=("Arial", 20, "bold"),
            text_color="#1F497D",
        ).pack(anchor="w", padx=20, pady=(20, 5))

        # ── Cuerpo principal (izquierda + derecha) ───────────
        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=5)

        self._panel_busqueda(cuerpo)
        self._panel_ticket(cuerpo)

    # ── PANEL IZQUIERDO: búsqueda y agregar ─────────────────
    def _panel_busqueda(self, parent):
        panel = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(
            panel,
            text="Buscar producto",
            font=("Arial", 13, "bold"),
            text_color="#333333",
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # Barra de búsqueda
        frame_busq = ctk.CTkFrame(panel, fg_color="transparent")
        frame_busq.pack(fill="x", padx=15)

        self.entry_buscar = ctk.CTkEntry(
            frame_busq,
            height=38,
            placeholder_text="Nombre o código de barras...",
            font=("Arial", 12),
        )
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_buscar.bind("<Return>", lambda e: self._buscar_producto())
        # Autocompletador
        self.lista_sugerencias = ctk.CTkScrollableFrame(panel, fg_color="white",
                                                         corner_radius=8, height=120)
        self.lista_sugerencias.pack(fill="x", padx=15)
        self.lista_sugerencias.pack_forget()  # oculto por defecto

        self.entry_buscar.bind("<KeyRelease>", self._autocompletar)
        ctk.CTkButton(
            frame_busq,
            text="Buscar",
            width=80,
            height=38,
            fg_color="#1F497D",
            hover_color="#16375e",
            command=self._buscar_producto,
        ).pack(side="left")

        ctk.CTkButton(
            frame_busq,
            text="📦 Catálogo",
            width=90,
            height=38,
            fg_color="#5D6D7E",
            hover_color="#424D58",
            font=("Arial", 11),
            command=self._abrir_catalogo,
        ).pack(side="left", padx=(8, 0))

        # Resultado de búsqueda
        self.lbl_resultado = ctk.CTkLabel(
            panel, text="", font=("Arial", 11), text_color="#555555"
        )
        self.lbl_resultado.pack(anchor="w", padx=15, pady=(8, 0))

        # Info del producto encontrado
        self.frame_producto = ctk.CTkFrame(panel, fg_color="#F0F4FA", corner_radius=8)
        self.frame_producto.pack(fill="x", padx=15, pady=8)

        self.lbl_nombre = ctk.CTkLabel(
            self.frame_producto,
            text="—",
            font=("Arial", 13, "bold"),
            text_color="#1F497D",
        )
        self.lbl_nombre.pack(anchor="w", padx=12, pady=(10, 2))

        self.lbl_precio = ctk.CTkLabel(
            self.frame_producto,
            text="Precio: —",
            font=("Arial", 12),
            text_color="#333333",
        )
        self.lbl_precio.pack(anchor="w", padx=12)

        self.lbl_stock = ctk.CTkLabel(
            self.frame_producto,
            text="Stock: —",
            font=("Arial", 12),
            text_color="#333333",
        )
        self.lbl_stock.pack(anchor="w", padx=12, pady=(0, 10))

        # Cantidad
        frame_cant = ctk.CTkFrame(panel, fg_color="transparent")
        frame_cant.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(frame_cant, text="Cantidad:", font=("Arial", 12, "bold")).pack(
            side="left", padx=(0, 8)
        )

        self.entry_cantidad = ctk.CTkEntry(
            frame_cant, width=70, height=36, font=("Arial", 13)
        )
        self.entry_cantidad.insert(0, "1")
        self.entry_cantidad.pack(side="left")

        ctk.CTkButton(
            frame_cant,
            text="➕ Agregar al ticket",
            height=36,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            font=("Arial", 12),
            command=self._agregar_al_ticket,
        ).pack(side="left", padx=(12, 0))

        # Mensaje de estado
        self.lbl_estado = ctk.CTkLabel(
            panel, text="", font=("Arial", 11), text_color="#C0392B"
        )
        self.lbl_estado.pack(anchor="w", padx=15)

        # Producto encontrado (guardado internamente)
        self.producto_actual = None

    # ── PANEL DERECHO: ticket ────────────────────────────────
    def _panel_ticket(self, parent):
        panel = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, width=280)
        panel.pack(side="left", fill="both")
        panel.pack_propagate(False)

        ctk.CTkLabel(
            panel, text="🧾 Ticket", font=("Arial", 13, "bold"), text_color="#333333"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # Lista del ticket
        self.lista_ticket = ctk.CTkTextbox(
            panel,
            font=("Courier", 11),
            fg_color="#F9F9F9",
            state="disabled",
            height=280,
        )
        self.lista_ticket.pack(fill="x", padx=15)

        # Total
        self.lbl_total = ctk.CTkLabel(
            panel,
            text="Total:  $0.00",
            font=("Arial", 16, "bold"),
            text_color="#1F497D",
        )
        self.lbl_total.pack(pady=(10, 5))

        # Botones
        ctk.CTkButton(
            panel,
            text="✅ Cobrar",
            height=40,
            fg_color="#1F497D",
            hover_color="#16375e",
            font=("Arial", 13, "bold"),
            command=self._cobrar,
        ).pack(fill="x", padx=15, pady=(0, 6))

        ctk.CTkButton(
            panel,
            text="🗑 Cancelar venta",
            height=36,
            fg_color="#C0392B",
            hover_color="#922B21",
            font=("Arial", 12),
            command=self._cancelar_venta,
        ).pack(fill="x", padx=15)

    # ── LÓGICA ───────────────────────────────────────────────
    def _autocompletar(self, event=None):
        termino = self.entry_buscar.get().strip()

        # Limpiar sugerencias
        for w in self.lista_sugerencias.winfo_children():
            w.destroy()

        if len(termino) < 2:
            self.lista_sugerencias.pack_forget()
            return

        con = get_conexion()
        cur = con.cursor()
        cur.execute("""
            SELECT id_producto, nombre, precio_venta, stock_actual
            FROM producto
            WHERE nombre LIKE ? OR codigo_barras LIKE ?
            LIMIT 6
        """, (f"%{termino}%", f"%{termino}%"))
        rows = cur.fetchall()
        con.close()

        if not rows:
            self.lista_sugerencias.pack_forget()
            return

        self.lista_sugerencias.pack(fill="x", padx=15)

        for row in rows:
            texto = f"{row['nombre']}  —  ${row['precio_venta']:.2f}  |  Stock: {row['stock_actual']}"
            btn = ctk.CTkButton(
            self.lista_sugerencias,
            text=texto,
            height=35,
            fg_color="white",
            hover_color="#D6EAF8",
            text_color="#333333",
            anchor="w",
            font=("Arial", 11),
            corner_radius=8,
          command=lambda r=dict(row): self._seleccionar_sugerencia(r)
)

# EFECTO HOVER MÁS FUERTE
            btn.bind("<Enter>", lambda e, b=btn: b.configure(fg_color="#D6EAF8"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(fg_color="white"))

            btn.pack(fill="x", pady=3, padx=3)

    def _seleccionar_sugerencia(self, row):
        self.producto_actual = row
        self.entry_buscar.delete(0, "end")
        self.entry_buscar.insert(0, row["nombre"])
        self.lbl_nombre.configure(text=row["nombre"])
        self.lbl_precio.configure(text=f"Precio: ${row['precio_venta']:.2f}")
        self.lbl_stock.configure(
            text=f"Stock: {row['stock_actual']} unidades",
            text_color="#C0392B" if row["stock_actual"] <= 5 else "#333333"
        )
        self.lbl_resultado.configure(text="✅ Producto seleccionado.", text_color="#2E7D32")
        self.lbl_estado.configure(text="")

        # Ocultar sugerencias
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
        cur.execute(
            """
            SELECT p.*, c.nombre_categoria FROM producto p
            LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
            WHERE p.codigo_barras = ? OR p.nombre LIKE ?
            LIMIT 1
        """,
            (termino, f"%{termino}%"),
        )
        row = cur.fetchone()
        con.close()

        if row:
            self.producto_actual = dict(row)
            self.lbl_nombre.configure(text=row["nombre"])
            self.lbl_precio.configure(text=f"Precio: ${row['precio_venta']:.2f}")
            self.lbl_stock.configure(
                text=f"Stock: {row['stock_actual']} unidades",
                text_color=(
                    "#C0392B"
                    if row["stock_actual"] <= row["stock_minimo"]
                    else "#333333"
                ),
            )
            self.lbl_resultado.configure(
                text="✅ Producto encontrado.", text_color="#2E7D32"
            )
            self.lbl_estado.configure(text="")
        else:
            self.producto_actual = None
            self.lbl_nombre.configure(text="—")
            self.lbl_precio.configure(text="Precio: —")
            self.lbl_stock.configure(text="Stock: —", text_color="#333333")
            self.lbl_resultado.configure(
                text="❌ Producto no encontrado.", text_color="#C0392B"
            )

    def _agregar_al_ticket(self):
        if not self.producto_actual:
            self.lbl_estado.configure(text="⚠ Primero busca un producto.")
            return

        try:
            cantidad = int(self.entry_cantidad.get())
            if cantidad <= 0:
                raise ValueError
        except ValueError:
            self.lbl_estado.configure(text="⚠ Cantidad inválida.")
            return

        if cantidad > self.producto_actual["stock_actual"]:
            self.lbl_estado.configure(
                text=f"⚠ Stock insuficiente. Disponible: {self.producto_actual['stock_actual']}"
            )
            return

        # Verificar si ya está en el ticket
        # Verificar si ya está en el ticket
        for item in self.ticket:
            if item["id_producto"] == self.producto_actual["id_producto"]:
                nueva_cantidad = item["cantidad"] + cantidad
                if nueva_cantidad > self.producto_actual["stock_actual"]:
                    self.lbl_estado.configure(
                        text=f"⚠ Stock insuficiente. Disponible: {self.producto_actual['stock_actual']}, "
                             f"ya en ticket: {item['cantidad']}.",
                        text_color="#C0392B"
                    )
                    return
                item["cantidad"] = nueva_cantidad
                item["subtotal"] = item["cantidad"] * item["precio_unitario"]
                self._actualizar_ticket()
                self.lbl_estado.configure(
                    text="✅ Cantidad actualizada.", text_color="#2E7D32"
                )
                return

        # Agregar nuevo item
        self.ticket.append(
            {
                "id_producto": self.producto_actual["id_producto"],
                "nombre": self.producto_actual["nombre"],
                "cantidad": cantidad,
                "precio_unitario": self.producto_actual["precio_venta"],
                "subtotal": cantidad * self.producto_actual["precio_venta"],
            }
        )

        self._actualizar_ticket()
        self.lbl_estado.configure(text="✅ Producto agregado.", text_color="#2E7D32")
        self.entry_buscar.delete(0, "end")
        self.entry_cantidad.delete(0, "end")
        self.producto_actual = None
        self.lbl_nombre.configure(text="—")
        self.lbl_precio.configure(text="Precio: —")
        self.lbl_stock.configure(text="Stock: —")
        self.lbl_resultado.configure(text="")
        self.entry_buscar.focus()

    def _actualizar_ticket(self):
        self.lista_ticket.configure(state="normal")
        self.lista_ticket.delete("1.0", "end")

        linea = f"{'Producto':<18} {'Cant':>4} {'P.Unit':>7} {'Sub':>8}\n"
        linea += "─" * 40 + "\n"
        total = 0
        for item in self.ticket:
            linea += f"{item['nombre'][:18]:<18} {item['cantidad']:>4} "
            linea += f"${item['precio_unitario']:>6.2f} ${item['subtotal']:>7.2f}\n"
            total += item["subtotal"]

        linea += "─" * 40 + f"\nTOTAL: ${total:.2f}"
        self.lista_ticket.insert("end", linea)
        self.lista_ticket.configure(state="disabled")
        self.lbl_total.configure(text=f"Total:  ${total:.2f}")

    def _cobrar(self):
        if not self.ticket:
            self.lbl_estado.configure(text="⚠ El ticket está vacío.")
            return

        total = sum(i["subtotal"] for i in self.ticket)
        self._ventana_cobro(total)

    def _ventana_cobro(self, total):
        import re
        win = ctk.CTkToplevel(self)
        win.title("Cobrar venta")
        win.geometry("320x360")
        win.resizable(False, False)
        win.transient(self)

        ctk.CTkLabel(win, text="💳 Cobrar venta",
                     font=("Arial", 16, "bold"),
                     text_color="#1F497D").pack(pady=(20, 5))

        # Total a cobrar
        frame_total = ctk.CTkFrame(win, fg_color="#F0F4FA", corner_radius=8)
        frame_total.pack(fill="x", padx=25, pady=10)

        ctk.CTkLabel(frame_total, text="Total a cobrar:",
                     font=("Arial", 12), text_color="#666666").pack(anchor="w", padx=12, pady=(8, 0))
        ctk.CTkLabel(frame_total, text=f"${total:.2f}",
                     font=("Arial", 22, "bold"),
                     text_color="#1F497D").pack(anchor="w", padx=12, pady=(0, 8))

        # Pago del cliente
        ctk.CTkLabel(win, text="¿Con cuánto paga el cliente?",
                     font=("Arial", 12, "bold"),
                     text_color="#333333").pack(anchor="w", padx=25)

        # Validador: solo números, máx 4 dígitos enteros y 2 decimales
        def validar_input(P):
            if P == "":
                return True
            return bool(re.match(r'^\d{1,4}(\.\d{0,2})?$', P))

        vcmd = (win.register(validar_input), '%P')

        entry_pago = ctk.CTkEntry(win, height=42, font=("Arial", 16),
                                   validate="key", validatecommand=vcmd,
                                   placeholder_text="Ej: 50.00")
        entry_pago.pack(fill="x", padx=25, pady=(5, 5))
        entry_pago.focus()

        lbl_cambio = ctk.CTkLabel(win, text="Cambio: —",
                                   font=("Arial", 14, "bold"),
                                   text_color="#2E7D32")
        lbl_cambio.pack(pady=3)

        lbl_err = ctk.CTkLabel(win, text="", text_color="#C0392B",
                                font=("Arial", 11))
        lbl_err.pack()

        def calcular_cambio(*args):
            texto = entry_pago.get().strip()
            if not texto:
                lbl_cambio.configure(text="Cambio: —", text_color="#888888")
                return
            try:
                pago = float(texto)
                cambio = pago - total
                if cambio < 0:
                    lbl_cambio.configure(
                        text=f"Faltan: ${abs(cambio):.2f}",
                        text_color="#C0392B")
                else:
                    lbl_cambio.configure(
                        text=f"Cambio: ${cambio:.2f}",
                        text_color="#2E7D32")
            except ValueError:
                lbl_cambio.configure(text="Cambio: —", text_color="#888888")

        entry_pago._entry.bind("<KeyRelease>", calcular_cambio)

        def confirmar():
            texto = entry_pago.get().strip()
            if not texto:
                lbl_err.configure(text="⚠ Ingresa el monto recibido.")
                return
            try:
                pago = float(texto)
            except ValueError:
                lbl_err.configure(text="⚠ Solo se permiten números. Ej: 50 o 50.50")
                return
            if pago <= 0:
                lbl_err.configure(text="⚠ El monto debe ser mayor a cero.")
                return
            if pago > 5000:
                lbl_err.configure(text="⚠ El monto máximo aceptado es $5,000.00 MXN.")
                return
            if pago < total:
                lbl_err.configure(text="⚠ El pago es menor al total.")
                return

            cambio = pago - total
            win.destroy()
            self._guardar_venta(total, pago, cambio)

        ctk.CTkButton(win, text="✅ Confirmar cobro",
                      height=42, fg_color="#1F497D", hover_color="#16375e",
                      font=("Arial", 13, "bold"),
                      command=confirmar).pack(fill="x", padx=25, pady=(5, 0))

        win.bind("<Return>", lambda e: confirmar())

    def _guardar_venta(self, total, pago, cambio):
        con = get_conexion()
        cur = con.cursor()
        try:
            from datetime import datetime
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                "INSERT INTO venta(fecha_hora, total, id_usuario) VALUES(?, ?, ?)",
                (ahora, total, self.user["id_usuario"])
            )
            id_venta = cur.lastrowid

            for item in self.ticket:
                cur.execute("""
                    INSERT INTO detalle_venta(id_venta, id_producto, cantidad, precio_unitario, subtotal)
                    VALUES(?, ?, ?, ?, ?)
                """, (id_venta, item["id_producto"], item["cantidad"],
                      item["precio_unitario"], item["subtotal"]))
                cur.execute("""
                    UPDATE producto SET stock_actual = stock_actual - ?
                    WHERE id_producto = ?
                """, (item["cantidad"], item["id_producto"]))

            con.commit()
            self._mostrar_confirmacion(total, pago, cambio)
            self.ticket = []
            self._actualizar_ticket()
            self.lbl_estado.configure(text="")

        except Exception as e:
            con.rollback()
            self.lbl_estado.configure(text=f"❌ Error al guardar: {e}")
        finally:
            con.close()

    def _mostrar_confirmacion(self, total, pago, cambio):
        win = ctk.CTkToplevel(self)
        win.title("Venta registrada")
        win.geometry("300x220")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="✅", font=("Arial", 40)).pack(pady=(15, 5))

        frame = ctk.CTkFrame(win, fg_color="#F0F4FA", corner_radius=8)
        frame.pack(fill="x", padx=25, pady=5)

        for label, valor, color in [
            ("Total cobrado:", f"${total:.2f}",  "#1F497D"),
            ("Pago cliente:",  f"${pago:.2f}",   "#333333"),
            ("Cambio:",        f"${cambio:.2f}", "#2E7D32"),
        ]:
            fila = ctk.CTkFrame(frame, fg_color="transparent")
            fila.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(fila, text=label,
                         font=("Arial", 12), text_color="#666666").pack(side="left")
            ctk.CTkLabel(fila, text=valor,
                         font=("Arial", 13, "bold"),
                         text_color=color).pack(side="right")

        ctk.CTkButton(win, text="Nueva venta", fg_color="#1F497D",
                      command=win.destroy).pack(pady=12)

    
    def _cancelar_venta(self):
         # Cerrar ventana de cobro si está abierta
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkToplevel):
                w.destroy()
        self.ticket = []
        self._actualizar_ticket()
        self.lbl_estado.configure(text="🗑 Venta cancelada.", text_color="#888888")
        self.entry_buscar.delete(0, "end")
        self.producto_actual = None
        self.lbl_nombre.configure(text="—")
        self.lbl_precio.configure(text="Precio: —")
        self.lbl_stock.configure(text="Stock: —")
        self.entry_cantidad.delete(0, "end")
    def _abrir_catalogo(self):
        win = ctk.CTkToplevel(self)
        win.title("Catalogo de productos")
        win.geometry("700x520")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        ctk.CTkLabel(win, text="Catalogo de Productos",
                     font=("Arial", 16, "bold"),
                     text_color="#1F497D").pack(anchor="w", padx=20, pady=(15, 5))

        frame_filtro = ctk.CTkFrame(win, fg_color="transparent")
        frame_filtro.pack(fill="x", padx=20, pady=(0, 5))

        ctk.CTkLabel(frame_filtro, text="Categoria:",
                     font=("Arial", 12, "bold")).pack(side="left", padx=(0, 8))

        con = get_conexion()
        cur = con.cursor()
        cur.execute("SELECT nombre_categoria FROM categoria ORDER BY nombre_categoria")
        categorias = ["Todas"] + [r["nombre_categoria"] for r in cur.fetchall()]
        con.close()

        combo_cat = ctk.CTkComboBox(frame_filtro, values=categorias,
                                     width=180, height=34,
                                     font=("Arial", 12), state="readonly")
        combo_cat.set("Todas")
        combo_cat.pack(side="left", padx=(0, 10))

        entry_buscar_cat = ctk.CTkEntry(frame_filtro, height=34,
                                         placeholder_text="Buscar en catalogo...",
                                         font=("Arial", 12))
        entry_buscar_cat.pack(side="left", fill="x", expand=True)

        tabla = ctk.CTkTextbox(win, fg_color="white", font=("Courier New", 11),
                                state="disabled", activate_scrollbars=True)
        tabla.pack(fill="both", expand=True, padx=20, pady=(5, 5))

        frame_pag = ctk.CTkFrame(win, fg_color="transparent")
        frame_pag.pack(fill="x", padx=20, pady=(0, 10))

        estado_pag = {"pagina": 0, "por_pagina": 50, "filas": []}

        btn_prev = ctk.CTkButton(frame_pag, text="< Anterior", width=90, height=28,
                                  fg_color="#1F497D", hover_color="#16375e", font=("Arial", 11))
        btn_prev.pack(side="left")

        lbl_pag = ctk.CTkLabel(frame_pag, text="", font=("Arial", 11), text_color="#555555")
        lbl_pag.pack(side="left", padx=12)

        btn_next = ctk.CTkButton(frame_pag, text="Siguiente >", width=90, height=28,
                                  fg_color="#1F497D", hover_color="#16375e", font=("Arial", 11))
        btn_next.pack(side="left")

        ctk.CTkLabel(frame_pag, text="  Clic en producto para seleccionarlo",
                     font=("Arial", 10), text_color="#888888").pack(side="left", padx=10)

        HEADER = "{:<32}{:<14}{:>9}{:>7}\n".format("Nombre", "Categoria", "Precio", "Stock")
        SEP = "-" * 62 + "\n"

        def cargar_cat(pagina=0):
            cat = combo_cat.get()
            term = entry_buscar_cat.get().strip()
            estado_pag["pagina"] = pagina

            where = "WHERE (p.nombre LIKE ? OR p.codigo_barras LIKE ?)"
            params = ["%" + term + "%", "%" + term + "%"]
            if cat != "Todas":
                where += " AND c.nombre_categoria = ?"
                params.append(cat)

            con2 = get_conexion()
            cur2 = con2.cursor()
            cur2.execute(
                "SELECT COUNT(*) as total FROM producto p "
                "LEFT JOIN categoria c ON p.id_categoria = c.id_categoria " + where,
                params)
            total = cur2.fetchone()["total"]

            offset = pagina * estado_pag["por_pagina"]
            cur2.execute(
                "SELECT p.id_producto, p.nombre, "
                "COALESCE(c.nombre_categoria, '-') AS nombre_categoria, "
                "p.precio_venta, p.stock_actual "
                "FROM producto p "
                "LEFT JOIN categoria c ON p.id_categoria = c.id_categoria "
                + where + " ORDER BY p.nombre LIMIT ? OFFSET ?",
                params + [estado_pag["por_pagina"], offset])
            rows = cur2.fetchall()
            con2.close()

            estado_pag["filas"] = [dict(r) for r in rows]

            tabla.configure(state="normal")
            tabla.delete("1.0", "end")
            tabla.insert("end", HEADER)
            tabla.insert("end", SEP)

            for row in rows:
                linea = "{:<32}{:<14}{:>9}{:>7}\n".format(
                    row["nombre"][:31],
                    row["nombre_categoria"][:13],
                    "$" + "{:.2f}".format(row["precio_venta"]),
                    str(row["stock_actual"])
                )
                tabla.insert("end", linea)

            tabla.configure(state="disabled")

            total_pags = max(1, -(-total // estado_pag["por_pagina"]))
            lbl_pag.configure(text="Pag {}/{} | {} productos".format(pagina+1, total_pags, total))
            btn_prev.configure(state="normal" if pagina > 0 else "disabled")
            btn_next.configure(state="normal" if pagina < total_pags - 1 else "disabled")

        def anterior():
            cargar_cat(estado_pag["pagina"] - 1)

        def siguiente():
            cargar_cat(estado_pag["pagina"] + 1)

        btn_prev.configure(command=anterior)
        btn_next.configure(command=siguiente)

        def clic_tabla(event):
            index = tabla.index("@{},{}".format(event.x, event.y))
            linea_num = int(index.split(".")[0]) - 3
            if 0 <= linea_num < len(estado_pag["filas"]):
                r = estado_pag["filas"][linea_num]
                self.producto_actual = r
                self.entry_buscar.delete(0, "end")
                self.entry_buscar.insert(0, r["nombre"])
                self.lbl_nombre.configure(text=r["nombre"])
                self.lbl_precio.configure(text="Precio: ${}".format(r["precio_venta"]))
                self.lbl_stock.configure(
                    text="Stock: {} unidades".format(r["stock_actual"]),
                    text_color="#C0392B" if r["stock_actual"] <= 5 else "#333333"
                )
                self.lbl_resultado.configure(text="Producto seleccionado.", text_color="#2E7D32")
                self.lbl_estado.configure(text="")
                win.destroy()
                self.entry_cantidad.focus()

        # Resaltado de fila al pasar el cursor
        ultima_linea = [0]

        def hover_tabla(event):
            index = tabla.index("@{},{}".format(event.x, event.y))
            linea_num = int(index.split(".")[0])

            if linea_num == ultima_linea[0]:
                return
            ultima_linea[0] = linea_num

            tabla.configure(state="normal")
            # Quitar resaltado anterior en toda la tabla
            tabla.tag_remove("hover", "1.0", "end")

            # Solo resaltar si es una fila de datos (no header ni separador)
            if linea_num >= 3 and (linea_num - 2) <= len(estado_pag["filas"]):
                start = "{}.0".format(linea_num)
                end = "{}.end".format(linea_num)
                tabla.tag_add("hover", start, end)
                tabla.tag_config("hover", background="#D6EAF8")

            tabla.configure(state="disabled")

        tabla.bind("<Motion>", hover_tabla)
        tabla.bind("<Leave>", lambda e: [
            tabla.configure(state="normal"),
            tabla.tag_remove("hover", "1.0", "end"),
            tabla.configure(state="disabled")
        ])
        tabla.bind("<Button-1>", clic_tabla)
        combo_cat.configure(command=lambda v: cargar_cat())
        entry_buscar_cat.bind("<KeyRelease>", lambda e: cargar_cat())
        cargar_cat()