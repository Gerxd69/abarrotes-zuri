import customtkinter as ctk
from database.conexion import get_conexion

def _confirmar(parent, mensaje):
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Confirmar")
    dialog.geometry("300x150")
    dialog.resizable(False, False)
    dialog.grab_set()

    resultado = [False]

    ctk.CTkLabel(dialog, text=mensaje,
                 font=("Arial", 13), wraplength=260).pack(pady=(25, 15))

    frame_btn = ctk.CTkFrame(dialog, fg_color="transparent")
    frame_btn.pack()

    def si():
        resultado[0] = True
        dialog.destroy()

    ctk.CTkButton(frame_btn, text="Si, eliminar",
                  fg_color="#C0392B", hover_color="#922B21",
                  width=120, command=si).pack(side="left", padx=8)
    ctk.CTkButton(frame_btn, text="Cancelar",
                  fg_color="#555555", hover_color="#333333",
                  width=120, command=dialog.destroy).pack(side="left", padx=8)

    dialog.wait_window()
    return resultado[0]


# Anchos de columna en caracteres — un solo lugar para ajustar
COL = [5, 14, 26, 10, 10, 6, 12, 10]
# ID  Codigo  Nombre  PVenta  PCosto  Stock  Cat  Estado

def _fila(vals):
    id_, cod, nom, pv, pc, st, cat, est = vals
    return (
        f"{str(id_):<{COL[0]}} "
        f"{str(cod)[:COL[1]]:<{COL[1]}} "
        f"{str(nom)[:COL[2]]:<{COL[2]}} "
        f"{str(pv):>{COL[3]}} "
        f"{str(pc):>{COL[4]}} "
        f"{str(st):>{COL[5]}} "
        f"{str(cat)[:COL[6]]:<{COL[6]}} "
        f"{str(est)}\n"
    )

HEADER = _fila(["ID", "Codigo", "Nombre", "P.Venta", "P.Costo", "Stock", "Categoria", "Estado"])
SEPARADOR = "-" * (sum(COL) + len(COL)) + "\n"


class InventarioFrame(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="#F0F4FA", corner_radius=0)
        self.user = user
        self._pagina = 0
        self._por_pagina = 50
        self._filas_data = []
        self._build_ui()
        self._cargar_productos()

    def _build_ui(self):
        # Titulo
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(top, text="Inventario",
                     font=("Arial", 20, "bold"),
                     text_color="#1F497D").pack(side="left")

        if self.user["rol"] in ("dueno", "dueño"):
            ctk.CTkButton(top, text="➕ Nuevo producto",
                          width=150, height=36,
                          fg_color="#2E7D32", hover_color="#1B5E20",
                          font=("Arial", 12),
                          command=self._form_producto).pack(side="right")

        # Busqueda
        frame_busq = ctk.CTkFrame(self, fg_color="transparent")
        frame_busq.pack(fill="x", padx=20, pady=(0, 5))

        self.entry_buscar = ctk.CTkEntry(frame_busq, height=36,
                                          placeholder_text="Buscar producto...",
                                          font=("Arial", 12))
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_buscar.bind("<KeyRelease>", lambda e: self._resetear_y_cargar())

        ctk.CTkButton(frame_busq, text="Actualizar", width=110, height=36,
                      fg_color="#1F497D", hover_color="#16375e",
                      command=self._cargar_productos).pack(side="left")

        # Alerta stock bajo
        self.lbl_alerta = ctk.CTkLabel(self, text="",
                                        font=("Arial", 11, "bold"),
                                        text_color="#C0392B")
        self.lbl_alerta.pack(anchor="w", padx=20)

        # Paginacion
        frame_pag = ctk.CTkFrame(self, fg_color="transparent")
        frame_pag.pack(fill="x", padx=20, pady=(2, 5))

        self.btn_prev = ctk.CTkButton(frame_pag, text="< Anterior", width=100, height=28,
                                       fg_color="#1F497D", hover_color="#16375e",
                                       font=("Arial", 11),
                                       command=self._pagina_anterior)
        self.btn_prev.pack(side="left")

        self.lbl_pagina = ctk.CTkLabel(frame_pag, text="",
                                        font=("Arial", 11), text_color="#555555")
        self.lbl_pagina.pack(side="left", padx=15)

        self.btn_next = ctk.CTkButton(frame_pag, text="Siguiente >", width=100, height=28,
                                       fg_color="#1F497D", hover_color="#16375e",
                                       font=("Arial", 11),
                                       command=self._pagina_siguiente)
        self.btn_next.pack(side="left")

        # Tabla — todo en un solo textbox con fuente monoespaciada
        tabla_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        tabla_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self.tabla_txt = ctk.CTkTextbox(
            tabla_frame,
            fg_color="white",
            font=("Courier New", 11),
            state="disabled",
            activate_scrollbars=True
        )
        self.tabla_txt.pack(fill="both", expand=True, padx=5, pady=5)
        self.tabla_txt.bind("<Double-Button-1>", self._doble_clic_tabla)

        # Resaltado hover al pasar cursor
        ultima_linea_inv = [0]

        def hover_inv(event):
            index = self.tabla_txt.index("@{},{}".format(event.x, event.y))
            linea_num = int(index.split(".")[0])
            if linea_num == ultima_linea_inv[0]:
                return
            ultima_linea_inv[0] = linea_num
            self.tabla_txt.configure(state="normal")
            self.tabla_txt.tag_remove("hover", "1.0", "end")
            if linea_num >= 3:
                self.tabla_txt.tag_add("hover", "{}.0".format(linea_num), "{}.end".format(linea_num))
                self.tabla_txt.tag_config("hover", background="#D6EAF8")
            self.tabla_txt.configure(state="disabled")

        def leave_inv(event):
            self.tabla_txt.configure(state="normal")
            self.tabla_txt.tag_remove("hover", "1.0", "end")
            self.tabla_txt.configure(state="disabled")

        self.tabla_txt.bind("<Motion>", hover_inv)
        self.tabla_txt.bind("<Leave>", leave_inv)

    def _resetear_y_cargar(self):
        self._pagina = 0
        self._cargar_productos()

    def _cargar_productos(self):
        termino = self.entry_buscar.get().strip()

        con = get_conexion()
        cur = con.cursor()

        cur.execute("""
            SELECT COUNT(*) as total FROM producto p
            WHERE p.nombre LIKE ? OR p.codigo_barras LIKE ?
        """, (f"%{termino}%", f"%{termino}%"))
        total = cur.fetchone()["total"]

        cur.execute("SELECT COUNT(*) as total FROM producto WHERE stock_actual <= stock_minimo")
        bajo_stock = cur.fetchone()["total"]

        offset = self._pagina * self._por_pagina
        cur.execute("""
            SELECT p.id_producto, p.codigo_barras, p.nombre,
                   p.precio_venta, p.precio_costo,
                   p.stock_actual, p.stock_minimo,
                   COALESCE(c.nombre_categoria, '-') AS categoria
            FROM producto p
            LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
            WHERE p.nombre LIKE ? OR p.codigo_barras LIKE ?
            ORDER BY p.nombre
            LIMIT ? OFFSET ?
        """, (f"%{termino}%", f"%{termino}%", self._por_pagina, offset))
        rows = cur.fetchall()
        con.close()

        self._filas_data = []
        self.tabla_txt.configure(state="normal")
        self.tabla_txt.delete("1.0", "end")

        # Encabezado dentro del mismo textbox
        self.tabla_txt.insert("end", HEADER)
        self.tabla_txt.insert("end", SEPARADOR)

        for row in rows:
            stock_ok = row["stock_actual"] > row["stock_minimo"]
            estado = "OK" if stock_ok else "Bajo stock"
            linea = _fila([
                row["id_producto"],
                row["codigo_barras"] or "-",
                row["nombre"],
                f"${row['precio_venta']:.2f}",
                f"${row['precio_costo']:.2f}",
                row["stock_actual"],
                row["categoria"],
                estado,
            ])
            self.tabla_txt.insert("end", linea)
            self._filas_data.append(dict(row))

        self.tabla_txt.configure(state="disabled")

        total_paginas = max(1, -(-total // self._por_pagina))
        self.lbl_pagina.configure(
            text=f"Pagina {self._pagina + 1} de {total_paginas}  |  {total} productos")
        self.btn_prev.configure(state="normal" if self._pagina > 0 else "disabled")
        self.btn_next.configure(state="normal" if self._pagina < total_paginas - 1 else "disabled")

        if bajo_stock:
            self.lbl_alerta.configure(text=f"{bajo_stock} producto(s) con stock bajo o agotado.")
        else:
            self.lbl_alerta.configure(text="")

    def _pagina_anterior(self):
        if self._pagina > 0:
            self._pagina -= 1
            self._cargar_productos()

    def _pagina_siguiente(self):
        self._pagina += 1
        self._cargar_productos()

    def _doble_clic_tabla(self, event):
        if self.user["rol"] not in ("dueno", "dueño"):
            return
        index = self.tabla_txt.index(f"@{event.x},{event.y}")
        linea_num = int(index.split(".")[0]) - 3  # descontar header + separador + base1
        if 0 <= linea_num < len(self._filas_data):
            self._form_producto(self._filas_data[linea_num])

    def _form_producto(self, producto=None):
        win = ctk.CTkToplevel(self)
        win.title("Nuevo producto" if not producto else "Editar producto")
        win.geometry("400x620")
        win.resizable(False, False)
        win.grab_set()

        scroll = ctk.CTkScrollableFrame(win, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll,
                     text="Nuevo producto" if not producto else "Editar producto",
                     font=("Arial", 16, "bold"),
                     text_color="#1F497D").pack(pady=(10, 15))

        campos = {}
        definicion = [
            ("Nombre",        "nombre",        producto["nombre"]            if producto else ""),
            ("Codigo barras", "codigo_barras",  producto["codigo_barras"]     if producto else ""),
            ("Precio venta",  "precio_venta",   str(producto["precio_venta"]) if producto else ""),
            ("Precio costo",  "precio_costo",   str(producto["precio_costo"]) if producto else ""),
            ("Stock actual",  "stock_actual",   str(producto["stock_actual"]) if producto else "0"),
            ("Stock minimo",  "stock_minimo",   str(producto["stock_minimo"]) if producto else "5"),
        ]

        for label, key, valor in definicion:
            ctk.CTkLabel(scroll, text=label,
                         font=("Arial", 12), text_color="#333333").pack(anchor="w", padx=20)
            entry = ctk.CTkEntry(scroll, height=36, font=("Arial", 12))
            entry.insert(0, valor)
            entry.pack(fill="x", padx=20, pady=(0, 10))
            campos[key] = entry

        lbl_err = ctk.CTkLabel(scroll, text="", text_color="#C0392B", font=("Arial", 11))
        lbl_err.pack(pady=(0, 5))

        def guardar():
            try:
                nombre       = campos["nombre"].get().strip()
                codigo       = campos["codigo_barras"].get().strip() or None
                p_venta      = float(campos["precio_venta"].get())
                p_costo      = float(campos["precio_costo"].get())
                stock_actual = int(campos["stock_actual"].get())
                stock_min    = int(campos["stock_minimo"].get())

                if not nombre:
                    lbl_err.configure(text="El nombre es obligatorio.")
                    return

                con = get_conexion()
                cur = con.cursor()

                if producto:
                    cur.execute("""
                        UPDATE producto SET
                            nombre=?, codigo_barras=?, precio_venta=?,
                            precio_costo=?, stock_actual=?, stock_minimo=?
                        WHERE id_producto=?
                    """, (nombre, codigo, p_venta, p_costo,
                          stock_actual, stock_min, producto["id_producto"]))
                else:
                    cur.execute("""
                        INSERT INTO producto(nombre, codigo_barras, precio_venta,
                        precio_costo, stock_actual, stock_minimo)
                        VALUES(?,?,?,?,?,?)
                    """, (nombre, codigo, p_venta, p_costo, stock_actual, stock_min))

                con.commit()
                con.close()
                win.destroy()
                self._cargar_productos()

            except ValueError:
                lbl_err.configure(text="Precios y stock deben ser numeros.")
            except Exception as e:
                lbl_err.configure(text=f"Error: {e}")

        ctk.CTkButton(scroll, text="Guardar",
                      height=42, fg_color="#1F497D", hover_color="#16375e",
                      font=("Arial", 13, "bold"),
                      command=guardar).pack(fill="x", padx=20, pady=(5, 5))

        if producto:
            def eliminar():
                if not _confirmar(win, "Eliminar este producto?"):
                    return
                con = get_conexion()
                cur = con.cursor()
                try:
                    cur.execute("DELETE FROM producto WHERE id_producto=?",
                                (producto["id_producto"],))
                    con.commit()
                    win.destroy()
                    self._cargar_productos()
                except Exception as e:
                    lbl_err.configure(text=f"No se puede eliminar: {e}")
                finally:
                    con.close()

            ctk.CTkButton(scroll, text="Eliminar producto",
                          height=42, fg_color="#C0392B", hover_color="#922B21",
                          font=("Arial", 13, "bold"),
                          command=eliminar).pack(fill="x", padx=20, pady=(0, 20))