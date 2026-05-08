import customtkinter as ctk
from database.conexion import get_conexion

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class LoginVentana(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Abarrotes "Zuri" — Sistema de Gestión v1.0')
        self.geometry("420x500")
        self.resizable(True, True)
        self._center_window()
        self._build_ui()
        self.bind("<F11>", lambda e: self._toggle_fullscreen())
        self.bind("<Escape>", lambda e: self._exit_fullscreen())

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        x = (w - 420) // 2
        y = (h - 500) // 2
        self.geometry(f"420x500+{x}+{y}")

    def _toggle_fullscreen(self):
        if self.attributes('-fullscreen'):
            self.attributes('-fullscreen', False)
        else:
            self.attributes('-fullscreen', True)

    def _exit_fullscreen(self):
        self.attributes('-fullscreen', False)

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="#1F497D", corner_radius=0, height=140)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="🛒", font=("Arial", 48)).pack(pady=(20, 0))
        ctk.CTkLabel(header, text='Abarrotes "Zuri"',
                     font=("Arial", 22, "bold"), text_color="white").pack()
        ctk.CTkLabel(header, text="Sistema de Gestión",
                     font=("Arial", 12), text_color="#BDD7EE").pack()

        form = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        form.pack(fill="both", expand=True, padx=40, pady=30)

        ctk.CTkLabel(form, text="Usuario",
                     font=("Arial", 13, "bold"), text_color="#333333").pack(anchor="w", pady=(10, 2))
        self.entry_usuario = ctk.CTkEntry(form, height=40,
                                          placeholder_text="Ingresa tu usuario",
                                          font=("Arial", 13))
        self.entry_usuario.pack(fill="x")

        ctk.CTkLabel(form, text="Contraseña",
                     font=("Arial", 13, "bold"), text_color="#333333").pack(anchor="w", pady=(16, 2))
        self.entry_contra = ctk.CTkEntry(form, height=40,
                                         placeholder_text="Ingresa tu contraseña",
                                         font=("Arial", 13), show="*")
        self.entry_contra.pack(fill="x")

        self.lbl_error = ctk.CTkLabel(form, text="", text_color="#C0392B",
                                      font=("Arial", 12))
        self.lbl_error.pack(pady=(8, 0))

        ctk.CTkButton(form, text="Ingresar", height=44,
                      font=("Arial", 14, "bold"),
                      fg_color="#1F497D", hover_color="#16375e",
                      command=self._login).pack(fill="x", pady=(16, 0))

        ctk.CTkLabel(self, text="Ixtepec, Oaxaca — 2026",
                     font=("Arial", 10), text_color="#999999").pack(pady=(0, 10))

        self.bind("<Return>", lambda e: self._login_event())
        self.entry_usuario.focus()

    def _login_event(self):
        self._login()

    def _login(self):
        usuario    = self.entry_usuario.get().strip()
        contrasena = self.entry_contra.get().strip()

        if not usuario or not contrasena:
            self.lbl_error.configure(text="⚠ Completa todos los campos.")
            return

        con = get_conexion()
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM usuario WHERE usuario = ? AND contrasena = ?",
            (usuario, contrasena)
        )
        user = cur.fetchone()
        con.close()

        if user:
            self.lbl_error.configure(text="")
            self._abrir_menu_principal(dict(user))
        else:
            self.lbl_error.configure(text="❌ Usuario o contraseña incorrectos.")
            self.entry_contra.delete(0, "end")

    def _abrir_menu_principal(self, user):
        from vistas.menu_principal import MenuPrincipal
        self.withdraw()
        MenuPrincipal(self, user)