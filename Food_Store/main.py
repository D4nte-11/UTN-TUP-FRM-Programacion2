from consola.lectura import leer_texto
from consola.menu import crear_menu
from entidades.usuario import Usuario
from enums.forma_pago import FormaPago
from enums.rol import Rol
from excepciones.errores import CredencialesInvalidasError
from servicios.categoria_servicio import CategoriaServicio
from servicios.pedido_servicio import PedidoServicio
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio


# Carga el administrador obligatorio y datos iniciales de ejemplo en memoria
def cargar_datos_iniciales(categoria_servicio: CategoriaServicio, producto_servicio: ProductoServicio, usuario_servicio: UsuarioServicio, pedido_servicio: PedidoServicio) -> None:
    # Usuarios iniciales (ADMIN obligatorio + un CLIENTE de prueba)
    usuario_servicio.crear("Ana", "Pérez", "admin@foodstore.com", "2615550001", "admin123", Rol.ADMIN)
    cliente = usuario_servicio.crear("Juan", "Gómez", "cliente@foodstore.com", "2615550002", "cliente123", Rol.USUARIO)

    # Categorías de ejemplo
    cat_hamburguesas = categoria_servicio.crear("Hamburguesas", "Hamburguesas caseras a la parrilla")
    cat_bebidas = categoria_servicio.crear("Bebidas", "Gaseosas, aguas y cervezas frías")

    # Productos de ejemplo
    prod_clasica = producto_servicio.crear("Hamburguesa Clásica", 8500.0, "Medallón de carne, queso cheddar, lechuga y tomate", 20, "hamburguesa_clasica.jpg", True, cat_hamburguesas)
    prod_doble = producto_servicio.crear("Hamburguesa Doble", 11000.0, "Doble carne, doble cheddar y panceta", 15, "hamburguesa_doble.jpg", True, cat_hamburguesas)
    prod_gaseosa = producto_servicio.crear("Gaseosa 500ml", 2500.0, "Bebida sabor cola bien fría", 30, "gaseosa_500.jpg", True, cat_bebidas)

    # Pedido inicial de ejemplo para el cliente
    pedido_servicio.crear(cliente, FormaPago.TARJETA, [(prod_clasica, 2), (prod_gaseosa, 2)])


# Gestiona el inicio de sesión con hasta 3 intentos fallidos
def iniciar_sesion(usuario_servicio: UsuarioServicio) -> Usuario | None:
    print("\n=== FOOD STORE - INICIO DE SESIÓN ===")
    for l in range(1, 4):
        mail = leer_texto("Mail: ")
        contrasenia = leer_texto("Contraseña: ")
        if mail is None or contrasenia is None:
            continue
        try:
            usuario = usuario_servicio.autenticar(mail, contrasenia)
            print(f"\nBienvenido/a, {usuario.nombre} {usuario.apellido} [{usuario.rol.name}]")
            return usuario
        except CredencialesInvalidasError as e:
            print(e)
            intentos_restantes = 3 - l
            if intentos_restantes > 0:
                print(f"Intentos restantes: {intentos_restantes}\n")
    print("Error: Se agotaron los 3 intentos de inicio de sesión. El programa finalizará.")
    return None


# Punto de entrada principal: instancia servicios, maneja la sesión local y delega al menú polimórfico.
def main() -> None:
    categoria_servicio = CategoriaServicio()
    producto_servicio = ProductoServicio()
    usuario_servicio = UsuarioServicio()
    pedido_servicio = PedidoServicio()

    cargar_datos_iniciales(categoria_servicio, producto_servicio, usuario_servicio, pedido_servicio)
    while True:
        usuario_sesion = iniciar_sesion(usuario_servicio)
        if usuario_sesion is None:
            break

        menu = crear_menu(usuario_sesion, categoria_servicio, producto_servicio, usuario_servicio, pedido_servicio)
        # True vuelve al inicio de sesión manteniendo los datos en memoria; False termina el programa.
        cerrar_sesion = menu.mostrar()
        if not cerrar_sesion:
            break


if __name__ == "__main__":
    main()