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

    ctk.CTkButton(frame_btn, text="Sí, eliminar",
                  fg_color="#C0392B", hover_color="#922B21",
                  width=120, command=si).pack(side="left", padx=8)
    ctk.CTkButton(frame_btn, text="Cancelar",
                  fg_color="#555555", hover_color="#333333",
                  width=120, command=dialog.destroy).pack(side="left", padx=8)

    dialog.wait_window()
    return resultado[0]


class ProveedoresFrame(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="#F0F4FA", corner_radius=0)
        self.user = user
        self._build_ui()
        self._cargar_proveedores()

    def _build_ui(self):
        # ── Título ───────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(top, text="🚚 Proveedores",
                     font=("Arial", 20, "bold"),
                     text_color="#1F497D").pack(side="left")

        if self.user["rol"] == "dueño":
            ctk.CTkButton(top, text="➕ Nuevo proveedor",
                          width=160, height=36,
                          fg_color="#2E7D32", hover_color="#1B5E20",
                          font=("Arial", 12),
                          command=self._form_proveedor).pack(side="right")

        # ── Búsqueda ─────────────────────────────────────────
        frame_busq = ctk.CTkFrame(self, fg_color="transparent")
        frame_busq.pack(fill="x", padx=20, pady=(0, 10))

        self.entry_buscar = ctk.CTkEntry(frame_busq, height=36,
                                          placeholder_text="Buscar proveedor...",
                                          font=("Arial", 12))
        self.entry_buscar.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_buscar.bind("<KeyRelease>", lambda e: self._cargar_proveedores())

        ctk.CTkButton(frame_busq, text="🔄 Actualizar", width=110, height=36,
                      fg_color="#1F497D", hover_color="#16375e",
                      command=self._cargar_proveedores).pack(side="left")

        # ── Tabla ────────────────────────────────────────────
        tabla_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        tabla_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        headers = ["ID", "Nombre",          "Teléfono",    "Productos que surte"]
        anchos  = [40,   220,               120,           360]

        header_frame = ctk.CTkFrame(tabla_frame, fg_color="#1F497D",
                                     corner_radius=0, height=36)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        for i, (h, w) in enumerate(zip(headers, anchos)):
            ctk.CTkLabel(header_frame, text=h, width=w,
                         font=("Arial", 11, "bold"),
                         text_color="white").grid(row=0, column=i, padx=4, pady=6)

        self.scroll = ctk.CTkScrollableFrame(tabla_frame, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

    def _cargar_proveedores(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        termino = self.entry_buscar.get().strip()
        con = get_conexion()
        cur = con.cursor()
        cur.execute("""
            SELECT * FROM proveedor
            WHERE nombre LIKE ? OR productos_que_surte LIKE ?
            ORDER BY nombre
        """, (f"%{termino}%", f"%{termino}%"))
        rows = cur.fetchall()
        con.close()

        anchos = [40, 220, 120, 360]

        for i, row in enumerate(rows):
            bg = "#F7F9FC" if i % 2 == 0 else "white"
            fila = ctk.CTkFrame(self.scroll, fg_color=bg, height=34, corner_radius=0)
            fila.pack(fill="x")
            fila.pack_propagate(False)

            valores = [
                str(row["id_proveedor"]),
                row["nombre"],
                row["telefono"] or "—",
                row["productos_que_surte"] or "—",
            ]

            for j, (val, w) in enumerate(zip(valores, anchos)):
                ctk.CTkLabel(fila, text=val, width=w,
                             font=("Arial", 11),
                             text_color="#333333").grid(row=0, column=j, padx=4, pady=4)

            if self.user["rol"] == "dueño":
                def bind_fila(f, r):
                    f.bind("<Double-Button-1>", lambda e, x=r: self._form_proveedor(x))
                    for child in f.winfo_children():
                        child.bind("<Double-Button-1>", lambda e, x=r: self._form_proveedor(x))
                bind_fila(fila, dict(row))

    def _form_proveedor(self, proveedor=None):
        win = ctk.CTkToplevel(self)
        win.title("Nuevo proveedor" if not proveedor else "Editar proveedor")
        win.geometry("400x420")
        win.resizable(False, False)
        win.grab_set()

        scroll = ctk.CTkScrollableFrame(win, fg_color="white")
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(scroll,
                     text="Nuevo proveedor" if not proveedor else "Editar proveedor",
                     font=("Arial", 16, "bold"),
                     text_color="#1F497D").pack(pady=(10, 15))

        campos = {}
        definicion = [
            ("Nombre",              "nombre",               proveedor["nombre"]               if proveedor else ""),
            ("Teléfono",            "telefono",             proveedor["telefono"]              if proveedor else ""),
            ("Productos que surte", "productos_que_surte",  proveedor["productos_que_surte"]   if proveedor else ""),
        ]

        for label, key, valor in definicion:
            ctk.CTkLabel(scroll, text=label,
                         font=("Arial", 12), text_color="#333333").pack(anchor="w", padx=20)
            entry = ctk.CTkEntry(scroll, height=36, font=("Arial", 12))
            entry.insert(0, valor or "")
            entry.pack(fill="x", padx=20, pady=(0, 10))
            campos[key] = entry

        lbl_err = ctk.CTkLabel(scroll, text="", text_color="#C0392B", font=("Arial", 11))
        lbl_err.pack()

        def guardar():
            nombre   = campos["nombre"].get().strip()
            telefono = campos["telefono"].get().strip() or None
            productos = campos["productos_que_surte"].get().strip() or None

            if not nombre:
                lbl_err.configure(text="⚠ El nombre es obligatorio.")
                return

            con = get_conexion()
            cur = con.cursor()
            try:
                if proveedor:
                    cur.execute("""
                        UPDATE proveedor SET nombre=?, telefono=?, productos_que_surte=?
                        WHERE id_proveedor=?
                    """, (nombre, telefono, productos, proveedor["id_proveedor"]))
                else:
                    cur.execute("""
                        INSERT INTO proveedor(nombre, telefono, productos_que_surte)
                        VALUES(?,?,?)
                    """, (nombre, telefono, productos))
                con.commit()
                win.destroy()
                self._cargar_proveedores()
            except Exception as e:
                lbl_err.configure(text=f"❌ Error: {e}")
            finally:
                con.close()

        ctk.CTkButton(scroll, text="💾 Guardar",
                      height=42, fg_color="#1F497D", hover_color="#16375e",
                      font=("Arial", 13, "bold"),
                      command=guardar).pack(fill="x", padx=20, pady=(5, 5))

        if proveedor:
            def eliminar():
                if not _confirmar(win, "¿Eliminar este proveedor?"):
                    return
                con = get_conexion()
                cur = con.cursor()
                try:
                    cur.execute("DELETE FROM proveedor WHERE id_proveedor=?",
                                (proveedor["id_proveedor"],))
                    con.commit()
                    win.destroy()
                    self._cargar_proveedores()
                except Exception as e:
                    lbl_err.configure(text=f"❌ No se puede eliminar: {e}")
                finally:
                    con.close()

            ctk.CTkButton(scroll, text="🗑 Eliminar proveedor",
                          height=42, fg_color="#C0392B", hover_color="#922B21",
                          font=("Arial", 13, "bold"),
                          command=eliminar).pack(fill="x", padx=20, pady=(0, 20))