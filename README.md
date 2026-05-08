# 🏪 Abarrotes "Zuri" - Sistema de Gestión de Inventario

Un sistema completo de gestión para tiendas de abarrotes, desarrollado con **Python**, **CustomTkinter** e **SQLite**. Diseñado para manejar inventario, ventas, compras y reportes de forma eficiente.

## 📋 Características Principales

✅ **Autenticación de Usuarios** - Sistema de login seguro  
✅ **Gestión de Inventario** - Crear, actualizar y monitorear productos  
✅ **Módulo de Ventas** - Registro y procesamiento de ventas  
✅ **Módulo de Compras** - Control de compras a proveedores  
✅ **Gestión de Proveedores** - Base de datos de proveedores  
✅ **Caja/POS** - Punto de venta integrado  
✅ **Reportes** - Análisis de ventas e inventario  
✅ **Actualización Automática de Stock** - Sistema que mantiene sincronizado el inventario  
✅ **Base de Datos SQLite** - Almacenamiento persistente y seguro  

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Uso |
|-----------|-----|
| **Python 3.x** | Lenguaje principal |
| **CustomTkinter** | Interfaz gráfica moderna |
| **SQLite3** | Base de datos |
| **Excel (.xls)** | Importación/exportación de datos |

---

## 📁 Estructura del Proyecto

```
abarrotes_zuri/
├── main.py                    # Punto de entrada de la aplicación
├── actualizar_stock.py        # Script para actualizar inventario
├── migrar_inventario.py       # Migración de datos de Excel
├── inventariobd.xls           # Base de datos de inventario en Excel
│
├── database/
│   └── conexion.py           # Configuración de BD SQLite
│
├── modelos/
│   ├── usuario.py            # Modelo de usuarios/clientes
│   ├── producto.py           # Modelo de productos
│   ├── venta.py              # Modelo de transacciones de venta
│   └── compra.py             # Modelo de compras
│
└── vistas/
    ├── login.py              # Interfaz de autenticación
    ├── menu_principal.py     # Menú principal
    ├── inventario.py         # Gestión de inventario
    ├── ventas.py             # Módulo de ventas
    ├── compras.py            # Módulo de compras
    ├── caja.py               # Sistema POS/Caja
    ├── proveedores.py        # Gestión de proveedores
    └── reportes.py           # Generación de reportes
```

---

## 🚀 Instalación y Uso

### Requisitos Previos
- **Python 3.7+**
- **pip** (gestor de paquetes)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/Gerxd69/abarrotes-zuri.git
cd abarrotes_zuri
```

2. **Crear entorno virtual** (recomendado)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install customtkinter
pip install openpyxl  # Para manejo de Excel
```

4. **Ejecutar la aplicación**
```bash
python main.py
```

---

## 💡 Funcionalidades Principales

### 🔐 Sistema de Login
- Autenticación de usuarios
- Gestión de roles y permisos
- Interfaz segura y amigable

### 📦 Gestión de Inventario
- Crear y editar productos
- Monitoreo de stock en tiempo real
- Alertas de bajo inventario
- Categorización de productos

### 💳 Módulo de Ventas
- Registro de transacciones
- Cálculo automático de totales
- Historial de ventas
- Métodos de pago

### 🛒 Módulo de Compras
- Registro de compras a proveedores
- Control de proveedores
- Actualización automática de stock

### 📊 Reportes
- Análisis de ventas
- Reportes de inventario
- Estadísticas de movimientos
- Exportación de datos

### 💰 Caja (POS)
- Interfaz de punto de venta
- Carrito de compras
- Cálculo de cambio
- Generación de recibos

---

## 📊 Base de Datos

El proyecto utiliza **SQLite** con las siguientes tablas principales:

- **usuarios** - Gestión de usuarios del sistema
- **productos** - Catálogo de productos
- **ventas** - Registro de transacciones
- **compras** - Registro de compras
- **proveedores** - Base de datos de proveedores
- **inventario** - Estado actual del stock

---

## 🔄 Workflow de Desarrollo

```
Usuario → Login → Menú Principal → Seleccionar Módulo
                                  ├─ Inventario
                                  ├─ Ventas/Caja
                                  ├─ Compras
                                  ├─ Proveedores
                                  └─ Reportes
```

---

## 👤 Autor

**Gerxd69** - Desarrollador Full Stack  
📧 [zvenmon32@gmail.com](mailto:zvenmon32@gmail.com)  
🔗 [GitHub](https://github.com/Gerxd69)

---

## 📝 Licencia

Este proyecto está bajo licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios mayores, abre un issue primero para discutir los cambios propuestos.

---

## 📝 Notas de Versión

### v1.0 (Actual)
- ✅ Sistema de autenticación
- ✅ Módulo de inventario
- ✅ Módulo de ventas
- ✅ Módulo de compras
- ✅ Sistema de reportes
- ✅ Integración con Excel

---

## 🐛 Reporte de Errores

Si encuentras algún error o tienes sugerencias, por favor abre un **issue** en el repositorio.

---

**¡Gracias por usar Abarrotes Zuri!** 🙏
