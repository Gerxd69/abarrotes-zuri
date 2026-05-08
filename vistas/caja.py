import customtkinter as ctk
from database.conexion import get_conexion
from datetime import date


class CajaFrame(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color="#F0F4FA", corner_radius=0)
        self.user = user
        self._build_ui()
        self._cargar_resumen()

    def _build_ui(self):
        ctk.CTkLabel(self, text="💰 Control de Caja",
                     font=("Arial", 20, "bold"),
                     text_color="#1F497D").pack(anchor="w", padx=20, pady=(20, 10))

        cuerpo = ctk.CTkFrame(self, fg_color="transparent")
        cuerpo.pack(fill="both", expand=True, padx=20, pady=5)

        self._panel_resumen(cuerpo)
        self._panel_historial(cuerpo)

    def _panel_resumen(self, parent):
        # ScrollableFrame para que el botón nunca se corte
        panel = ctk.CTkScrollableFrame(parent, fg_color="white",
                                        corner_radius=10, width=280)
        panel.pack(side="left", fill="y", padx=(0, 10))

        ctk.CTkLabel(panel, text=f"📅 {date.today().strftime('%d/%m/%Y')}",
                     font=("Arial", 13, "bold"),
                     text_color="#1F497D").pack(pady=(20, 5))

        ctk.CTkLabel(panel, text="Resumen del día",
                     font=("Arial", 12),
                     text_color="#666666").pack()

        ctk.CTkLabel(panel, text="─" * 28,
                     text_color="#DDDDDD").pack(pady=5)

        self.lbl_ventas = self._tarjeta(panel, "Total ventas", "$0.00", "#2E7D32")
        self.lbl_gastos = self._tarjeta(panel, "Total gastos", "$0.00", "#C0392B")
        self.lbl_saldo  = self._tarjeta(panel, "Saldo final",  "$0.00", "#1F497D")

        ctk.CTkLabel(panel, text="─" * 28,
                     text_color="#DDDDDD").pack(pady=5)

        ctk.CTkLabel(panel, text="Registrar gasto:",
                     font=("Arial", 12, "bold"),
                     text_color="#333333").pack(anchor="w", padx=15)

        self.entry_gasto = ctk.CTkEntry(panel, height=36,
                                         placeholder_text="Monto del gasto...",
                                         font=("Arial", 12))
        self.entry_gasto.pack(fill="x", padx=15, pady=(5, 5))

        self.entry_concepto = ctk.CTkEntry(panel, height=36,
                                            placeholder_text="Concepto (opcional)",
                                            font=("Arial", 12))
        self.entry_concepto.pack(fill="x", padx=15, pady=(0, 8))

        self.lbl_err = ctk.CTkLabel(panel, text="", text_color="#C0392B",
                                     font=("Arial", 11))
        self.lbl_err.pack()

        ctk.CTkButton(panel, text="➕ Agregar gasto",
                      height=36, fg_color="#E65100", hover_color="#BF360C",
                      font=("Arial", 12),
                      command=self._agregar_gasto).pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(panel, text="─" * 28,
                     text_color="#DDDDDD").pack(pady=5)

        ctk.CTkButton(panel, text="🖨 Generar corte de caja",
                      height=42, fg_color="#1F497D", hover_color="#16375e",
                      font=("Arial", 13, "bold"),
                      command=self._generar_corte).pack(fill="x", padx=15, pady=(0, 20))

    def _tarjeta(self, parent, titulo, valor, color):
        frame = ctk.CTkFrame(parent, fg_color="#F0F4FA", corner_radius=8)
        frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(frame, text=titulo,
                     font=("Arial", 11), text_color="#666666").pack(anchor="w", padx=12, pady=(8, 0))
        lbl = ctk.CTkLabel(frame, text=valor,
                            font=("Arial", 18, "bold"), text_color=color)
        lbl.pack(anchor="w", padx=12, pady=(0, 8))
        return lbl

    def _panel_historial(self, parent):
        panel = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        panel.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(panel, text="📋 Historial de cortes",
                     font=("Arial", 13, "bold"),
                     text_color="#333333").pack(anchor="w", padx=15, pady=(15, 10))

        headers = ["Fecha", "Ventas", "Gastos", "Saldo", "Usuario"]
        anchos  = [80,      90,       90,       90,      120]

        header_frame = ctk.CTkFrame(panel, fg_color="#1F497D",
                                     corner_radius=0, height=36)
        header_frame.pack(fill="x", padx=10)
        header_frame.pack_propagate(False)

        for i, (h, w) in enumerate(zip(headers, anchos)):
            ctk.CTkLabel(header_frame, text=h, width=w,
                         font=("Arial", 11, "bold"),
                         text_color="white").grid(row=0, column=i, padx=4, pady=6)

        self.scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _cargar_resumen(self):
        hoy = date.today().isoformat()
        con = get_conexion()
        cur = con.cursor()

        # Total ventas del día
        cur.execute("""
            SELECT COALESCE(SUM(total), 0) FROM venta
            WHERE substr(fecha_hora, 1, 10) = ?
        """, (hoy,))
        total_ventas = cur.fetchone()[0]

        # Total gastos del día
        cur.execute("""
            SELECT COALESCE(SUM(total_gastos), 0) FROM caja
            WHERE fecha = ?
        """, (hoy,))
        total_gastos = cur.fetchone()[0]

        saldo = total_ventas - total_gastos

        self.lbl_ventas.configure(text=f"${total_ventas:.2f}")
        self.lbl_gastos.configure(text=f"${total_gastos:.2f}")
        self.lbl_saldo.configure(text=f"${saldo:.2f}")

        # Historial de cortes
        cur.execute("""
            SELECT c.fecha, c.total_ventas, c.total_gastos,
                   c.saldo_final, u.nombre
            FROM caja c
            JOIN usuario u ON c.id_usuario = u.id_usuario
            ORDER BY c.fecha DESC
            LIMIT 30
        """)
        rows = cur.fetchall()
        con.close()

        for widget in self.scroll.winfo_children():
            widget.destroy()

        anchos = [80, 90, 90, 90, 120]
        for i, row in enumerate(rows):
            bg = "#F7F9FC" if i % 2 == 0 else "white"
            fila = ctk.CTkFrame(self.scroll, fg_color=bg, height=32, corner_radius=0)
            fila.pack(fill="x")
            fila.pack_propagate(False)

            valores = [
                row["fecha"],
                f"${row['total_ventas']:.2f}",
                f"${row['total_gastos']:.2f}",
                f"${row['saldo_final']:.2f}",
                row["nombre"],
            ]
            colores = ["#333333", "#2E7D32", "#C0392B", "#1F497D", "#333333"]

            for j, (val, w, col) in enumerate(zip(valores, anchos, colores)):
                ctk.CTkLabel(fila, text=val, width=w,
                             font=("Arial", 11),
                             text_color=col).grid(row=0, column=j, padx=4, pady=4)
    def _agregar_gasto(self):
        try:
            monto = float(self.entry_gasto.get().strip())
            if monto <= 0:
                raise ValueError
        except ValueError:
            self.lbl_err.configure(text="⚠ Ingresa un monto válido.")
            return

        hoy = date.today().isoformat()
        con = get_conexion()
        cur = con.cursor()
        try:
            cur.execute("SELECT id_corte, total_gastos FROM caja WHERE fecha = ?", (hoy,))
            corte = cur.fetchone()
            if corte:
                nuevos_gastos = corte["total_gastos"] + monto
                cur.execute("""
                    UPDATE caja SET total_gastos = ?, saldo_final = total_ventas - ?
                    WHERE id_corte = ?
                """, (nuevos_gastos, nuevos_gastos, corte["id_corte"]))
            else:
                cur.execute("""
                    SELECT COALESCE(SUM(total), 0) FROM venta
                    WHERE date(fecha_hora) = ?
                """, (hoy,))
                ventas = cur.fetchone()[0]
                cur.execute("""
                    INSERT INTO caja(fecha, total_ventas, total_gastos, saldo_final, id_usuario)
                    VALUES(?, ?, ?, ?, ?)
                """, (hoy, ventas, monto, ventas - monto, self.user["id_usuario"]))

            con.commit()
            self.entry_gasto.delete(0, "end")
            self.entry_concepto.delete(0, "end")
            self.lbl_err.configure(text="✅ Gasto registrado.", text_color="#2E7D32")
            self._cargar_resumen()
        except Exception as e:
            self.lbl_err.configure(text=f"❌ Error: {e}")
        finally:
            con.close()

    def _generar_corte(self):
        hoy = date.today().isoformat()
        con = get_conexion()
        cur = con.cursor()
        try:
            cur.execute("""
                SELECT COALESCE(SUM(total), 0) FROM venta
                WHERE date(fecha_hora) = ?
            """, (hoy,))
            total_ventas = cur.fetchone()[0]

            cur.execute("""
                SELECT COALESCE(SUM(total_gastos), 0) FROM caja WHERE fecha = ?
            """, (hoy,))
            total_gastos = cur.fetchone()[0]

            saldo = total_ventas - total_gastos

            cur.execute("SELECT id_corte FROM caja WHERE fecha = ?", (hoy,))
            existente = cur.fetchone()

            if existente:
                cur.execute("""
                    UPDATE caja SET total_ventas=?, saldo_final=?
                    WHERE fecha=?
                """, (total_ventas, saldo, hoy))
            else:
                cur.execute("""
                    INSERT INTO caja(fecha, total_ventas, total_gastos, saldo_final, id_usuario)
                    VALUES(?, ?, 0, ?, ?)
                """, (hoy, total_ventas, saldo, self.user["id_usuario"]))

            con.commit()
            self._cargar_resumen()
            self._mostrar_corte(total_ventas, total_gastos, saldo)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            con.close()

    def _mostrar_corte(self, ventas, gastos, saldo):
        win = ctk.CTkToplevel(self)
        win.title("Corte de caja")
        win.geometry("320x280")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="💰 Corte de Caja",
                     font=("Arial", 16, "bold"),
                     text_color="#1F497D").pack(pady=(20, 5))
        ctk.CTkLabel(win, text=date.today().strftime("%d/%m/%Y"),
                     font=("Arial", 12), text_color="#666666").pack()

        frame = ctk.CTkFrame(win, fg_color="#F0F4FA", corner_radius=8)
        frame.pack(fill="x", padx=30, pady=15)

        for label, valor, color in [
            ("Total ventas:", f"${ventas:.2f}", "#2E7D32"),
            ("Total gastos:", f"${gastos:.2f}", "#C0392B"),
            ("Saldo final:",  f"${saldo:.2f}",  "#1F497D"),
        ]:
            fila = ctk.CTkFrame(frame, fg_color="transparent")
            fila.pack(fill="x", padx=15, pady=4)
            ctk.CTkLabel(fila, text=label,
                         font=("Arial", 12), text_color="#333333").pack(side="left")
            ctk.CTkLabel(fila, text=valor,
                         font=("Arial", 13, "bold"),
                         text_color=color).pack(side="right")

        ctk.CTkButton(win, text="Cerrar",
                      fg_color="#1F497D", hover_color="#16375e",
                      command=win.destroy).pack(pady=10)