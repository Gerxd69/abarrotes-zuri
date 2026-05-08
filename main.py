from database.conexion import inicializar_bd
from vistas.login import LoginVentana

if __name__ == "__main__":
    inicializar_bd()       # crea la BD si no existe
    app = LoginVentana()
    app.mainloop()