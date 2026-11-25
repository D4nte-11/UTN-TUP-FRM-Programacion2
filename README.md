# Food Store — Sistema de Gestión de Pedidos de Comida (Consola)

Trabajo Práctico Integrador de Programación II — Tecnicatura Universitaria en Programación a Distancia (UTN – Facultad Regional Mendoza).

Aplicación de consola desarrollada en Python aplicando el paradigma de Programación Orientada a Objetos (POO), arquitectura en tres capas, colecciones en memoria, manejo de excepciones propias, interfaz `Calculable`, polimorfismo por rol y anotaciones de tipo (*type hints*).

---

## Enlaces del proyecto

* Repositorio GitHub: [Food_Store en UTN-TUP-FRM-Programacion2](https://github.com/D4nte-11/UTN-TUP-FRM-Programacion2/tree/main/Food_Store)
* Informe en PDF: [Informe_TPI_FoodStore.pdf](./Informe_TPI_FoodStore.pdf)
* Video demostración (No listado): `[https://youtu.be/Z93BMlOwo8Q]`

---

## Requisitos y ejecución

* Lenguaje: Python 3.12 o superior.
* Dependencias: Ninguna externa. Se utiliza únicamente la biblioteca estándar de Python (`abc`, `enum`, `datetime`).

### Cómo ejecutar el sistema

1. Clonar o descargar el repositorio y ubicarse en la carpeta raíz del proyecto (`Food_Store/`):

 bash
cd Food_Store


2. Ejecutar la aplicación principal:

 bash
python main.py


3. *(Opcional)* Ejecutar la batería de pruebas automatizadas del modelo, servicios y polimorfismo de menús:

 bash
python pruebas.py


> Nota sobre persistencia: Toda la información vive en memoria dentro de colecciones mientras el programa está en ejecución. Al salir del programa, los datos se reinician; al seleccionar Cerrar sesión, los datos creados se conservan en memoria para el siguiente usuario que ingrese.

---

## Credenciales iniciales

Al iniciar el sistema, `main.py` precarga usuarios y datos de ejemplo para poder operar de inmediato:

 Rol  Mail  Contraseña  Permisos 
 Rol: Administrador (`ADMIN`)  Mail: `admin@foodstore.com`  Contraseña: `admin123` Permisos Gestión completa (alta, baja lógica, modificación y consulta) de categorías, productos, usuarios y pedidos. 
 Rol: Cliente (`USUARIO`)  Mail: `cliente@foodstore.com` Contraseña `cliente123` Permisos: Solo consulta: ver categorías activas, productos disponibles con stock, sus propios pedidos/detalles y sus datos personales. 

* El inicio de sesión permite hasta 3 intentos fallidos antes de finalizar el programa de forma controlada.
* Por seguridad, ante mail inexistente, usuario eliminado o contraseña incorrecta se informa siempre el mismo mensaje: `Mail o contraseña incorrectos`.

---

## Arquitectura del proyecto

El proyecto sigue una arquitectura en tres capas con dependencia unidireccional (`consola → servicios → entidades`), sin variables globales y sin lógica de negocio en la capa de presentación:

 text
Food_Store/
├── main.py                     # Punto de entrada: carga datos iniciales, sesión y bucle de menús
├── pruebas.py                  # Pruebas automatizadas con assert sobre entidades, servicios y menús
├── calculable.py               # Interfaz abstracta Calculable (método calcular_total)
├── README.md                   # Documentación de uso y entrega del proyecto
├── Informe_TPI_FoodStore.pdf   # Informe técnico del TPI
├── entidades/                  # Capa de modelo (clases del UML y validaciones en setters)
│   ├── __init__.py
│   ├── base.py                 # Clase abstracta Base (id automático por clase, eliminado, creado_en, __eq__, __str__)
│   ├── categoria.py            # Entidad Categoria (agregación 1..N con Producto)
│   ├── producto.py             # Entidad Producto (N..1 con Categoria)
│   ├── usuario.py              # Entidad Usuario (contrasenia encapsulada sin getter, verificar_contrasenia)
│   ├── pedido.py               # Entidad Pedido (hereda de Base e implementa Calculable; composición con DetallePedido)
│   └── detalle_pedido.py       # Entidad DetallePedido (creada y gestionada exclusivamente por Pedido)
├── enums/                      # Enumerados del dominio (enum.Enum)
│   ├── __init__.py
│   ├── rol.py                  # Rol: ADMIN, USUARIO
│   ├── estado.py               # Estado: PENDIENTE, CONFIRMADO, TERMINADO, CANCELADO
│   └── forma_pago.py           # FormaPago: TARJETA, TRANSFERENCIA, EFECTIVO
├── excepciones/                # Jerarquía de excepciones de dominio
│   ├── __init__.py
│   └── errores.py              # FoodStoreError y subclases específicas
├── servicios/                  # Capa de lógica de negocio y colecciones en memoria
│   ├── __init__.py
│   ├── categoria_servicio.py   # CRUD de categorías, unicidad case-insensitive, control de productos activos
│   ├── producto_servicio.py    # CRUD de productos y filtrado de disponibles con stock > 0
│   ├── usuario_servicio.py     # CRUD de usuarios, mail único, autenticación y protección de auto-eliminación
│   └── pedido_servicio.py      # Creación atómica de pedidos, cálculo de totales, estados y devolución de stock
└── consola/                    # Capa de presentación por consola
    ├── __init__.py
    ├── lectura.py              # Funciones de lectura validada (textos, números, confirmaciones, enums y opciones)
    ├── menu.py                 # Clase abstracta Menu y fábrica polimórfica crear_menu()
    ├── menu_admin.py           # Subclase MenuAdministrador (gestión completa por submenús)
    └── menu_cliente.py         # Subclase MenuCliente (solo consulta)


---

## Principales reglas de negocio implementadas

* Baja lógica universal: Ninguna entidad se borra físicamente de las colecciones; se marca `eliminado = True` preservando el historial de pedidos.
* Composición real en `Pedido`: `Pedido` es el único responsable de instanciar y administrar sus `DetallePedido` mediante `agregar_detalle`, `buscar_detalle_por_producto`, `eliminar_detalle_por_producto` y `calcular_total()`.
* Atomicidad de stock: Al crear un pedido se valida disponibilidad y stock de todos los ítems antes de confirmar; si algún producto no tiene stock suficiente, se lanza `StockInsuficienteError`, se cancela la operación y no se descuenta stock de ningún producto.
* Transiciones de estado controladas: `PENDIENTE → CONFIRMADO → TERMINADO`, y `PENDIENTE` / `CONFIRMADO → CANCELADO`. Los estados `TERMINADO` y `CANCELADO` son finales. Cancelar o eliminar un pedido abierto devuelve automáticamente el stock.
* Polimorfismo por rol: La selección del menú se realiza una sola vez en `crear_menu()`, eliminando condicionales por rol en la capa de consola.
* Protección de integridad: Nombres de categoría únicos sin distinguir mayúsculas, correos electrónicos únicos, restricción para eliminar categorías con productos activos y bloqueo para que un administrador no pueda eliminarse a sí mismo durante su sesión.