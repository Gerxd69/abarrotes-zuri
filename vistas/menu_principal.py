import customtkinter as ctk

class MenuPrincipal(ctk.CTkToplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user

        self.title(f'Abarrotes "Zuri" — {user["nombre"]}')
        self.geometry("1100x650")
        self.resizable(True, True)
        self._center_window()
        self.protocol("WM_DELETE_WINDOW", self._cerrar)
        self.bind("<F11>", lambda e: self._toggle_fullscreen())
        self.bind("<Escape>", lambda e: self._exit_fullscreen())

        self._build_ui()

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        x = (w - 1100) // 2
        y = (h - 650) // 2
        self.geometry(f"1100x650+{x}+{y}")

    def _toggle_fullscreen(self):
        if self.attributes('-fullscreen'):
            self.attributes('-fullscreen', False)
        else:
            self.attributes('-fullscreen', True)

    def _exit_fullscreen(self):
        self.attributes('-fullscreen', False)

    def _build_ui(self):
        # ── Barra lateral izquierda ──────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color="#1F497D", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / nombre
        ctk.CTkLabel(self.sidebar, text="🛒", font=("Arial", 40)).pack(pady=(30, 0))
        ctk.CTkLabel(self.sidebar, text='Abarrotes "Zuri"',
                     font=("Arial", 15, "bold"),
                     text_color="white").pack()
        ctk.CTkLabel(self.sidebar, text="─" * 22,
                     text_color="#4A7AAF").pack(pady=(10, 5))

        # Info del usuario
        ctk.CTkLabel(self.sidebar, text=f"👤 {self.user['nombre']}",
                     font=("Arial", 11), text_color="#BDD7EE").pack(pady=(0, 2))
        ctk.CTkLabel(self.sidebar, text=f"Rol: {self.user['rol']}",
                     font=("Arial", 10), text_color="#7FAACC").pack()
        ctk.CTkLabel(self.sidebar, text="─" * 22,
                     text_color="#4A7AAF").pack(pady=(10, 15))

        # Botones del menú
        self.botones = {}
        modulos = [
            ("🧾  Ventas",        "ventas"),
            ("📦  Inventario",    "inventario"),
            ("🚚  Proveedores",   "proveedores"),
            ("🛒  Compras",       "compras"),
            ("💰  Caja",          "caja"),
            ("📊  Reportes",      "reportes"),
        ]

        # Solo dueño ve caja y reportes completos
        for label, key in modulos:
            btn = ctk.CTkButton(
                self.sidebar, text=label,
                font=("Arial", 13), height=42,
                fg_color="transparent",
                hover_color="#16375e",
                anchor="w",
                command=lambda k=key: self._abrir_modulo(k)
            )
            btn.pack(fill="x", padx=10, pady=3)
            self.botones[key] = btn

        # Deshabilitar reportes y caja para cajero
        if self.user["rol"] == "cajero":
            self.botones["caja"].configure(state="disabled", text_color="#7FAACC")
            self.botones["reportes"].configure(state="disabled", text_color="#7FAACC")

        # Botón cerrar sesión abajo
        ctk.CTkLabel(self.sidebar, text="").pack(expand=True)
        ctk.CTkButton(self.sidebar, text="🚪  Cerrar sesión",
                      font=("Arial", 12),
                      fg_color="#C0392B", hover_color="#922B21",
                      height=38,
                      command=self._cerrar).pack(fill="x", padx=10, pady=(0, 20))

        # ── Panel principal derecho ──────────────────────────
        self.panel = ctk.CTkFrame(self, fg_color="#F0F4FA", corner_radius=0)
        self.panel.pack(side="left", fill="both", expand=True)

        self._mostrar_bienvenida()

    def _mostrar_bienvenida(self):
        for widget in self.panel.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.panel, text="👋", font=("Arial", 60)).pack(pady=(80, 10))
        ctk.CTkLabel(self.panel,
                     text=f"Bienvenido, {self.user['nombre']}",
                     font=("Arial", 22, "bold"),
                     text_color="#1F497D").pack()
        ctk.CTkLabel(self.panel,
                     text="Selecciona un módulo del menú para comenzar.",
                     font=("Arial", 13),
                     text_color="#666666").pack(pady=10)

        # Tarjetas de acceso rápido (solo las principales)
        frame_cards = ctk.CTkFrame(self.panel, fg_color="transparent")
        frame_cards.pack(pady=30)

        accesos = [
            ("🧾", "Nueva Venta",    "ventas"),
            ("📦", "Inventario",     "inventario"),
            ("🚚", "Proveedores",    "proveedores"),
        ]
        for icon, nombre, key in accesos:
            card = ctk.CTkButton(
                frame_cards, text=f"{icon}\n{nombre}",
                font=("Arial", 13), width=130, height=100,
                fg_color="white", text_color="#1F497D",
                hover_color="#D5E8F0",
                border_width=1, border_color="#BDD7EE",
                corner_radius=12,
                command=lambda k=key: self._abrir_modulo(k)
            )
            card.pack(side="left", padx=12)

   
    def _abrir_modulo(self, modulo):
     for widget in self.panel.winfo_children():
        widget.destroy()

     if modulo == "ventas":
        from vistas.ventas import VentasFrame
        VentasFrame(self.panel, self.user).pack(fill="both", expand=True)

     elif modulo == "inventario":
        from vistas.inventario import InventarioFrame
        InventarioFrame(self.panel, self.user).pack(fill="both", expand=True)

     elif modulo == "proveedores":
         from vistas.proveedores import ProveedoresFrame
         ProveedoresFrame(self.panel, self.user).pack(fill="both", expand=True)
         
     elif modulo == "reportes":
        from vistas.reportes import ReportesFrame
        ReportesFrame(self.panel, self.user).pack(fill="both", expand=True)
    
     elif modulo == "caja":
        from vistas.caja import CajaFrame
        CajaFrame(self.panel, self.user).pack(fill="both", expand=True)
        
     elif modulo == "compras":
        from vistas.compras import ComprasFrame
        ComprasFrame(self.panel, self.user).pack(fill="both", expand=True)
        
     else:   
        ctk.CTkLabel(self.panel,
                     text=f"Módulo: {modulo.upper()}",
                     font=("Arial", 20, "bold"),
                     text_color="#1F497D").pack(pady=(80, 10))
        ctk.CTkLabel(self.panel,
                     text="Este módulo está en construcción.",
                     font=("Arial", 13),
                     text_color="#888888").pack()
    

    def _cerrar(self):
        self.master.destroy()