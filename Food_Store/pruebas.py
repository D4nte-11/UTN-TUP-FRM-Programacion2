from calculable import Calculable
from consola.menu import Menu, crear_menu
from consola.menu_admin import MenuAdministrador
from consola.menu_cliente import MenuCliente
from entidades.base import Base
from entidades.categoria import Categoria
from entidades.producto import Producto
from enums.estado import Estado
from enums.forma_pago import FormaPago
from enums.rol import Rol
from excepciones.errores import (CredencialesInvalidasError, DatoInvalidoError, DuplicadoError, EntidadNoEncontradaError, OperacionNoPermitidaError, StockInsuficienteError)
from servicios.categoria_servicio import CategoriaServicio
from servicios.pedido_servicio import PedidoServicio
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio


# Función auxiliar para verificar que una operación lance la excepción esperada
def verificar_error(tipo_error: type[Exception], funcion, *args) -> None:
    try:
        funcion(*args)
    except tipo_error:
        return
    raise AssertionError(f"Se esperaba {tipo_error.__name__}, pero no se lanzó ninguna excepción.")


# 1. Prueba clases abstractas, generación de IDs y __eq__ en Base
def probar_base_y_abstraccion() -> None:
    verificar_error(TypeError, Base)
    verificar_error(TypeError, Calculable)
    verificar_error(TypeError, Menu, None)

    cat1 = Categoria("Pizzas", "Pizzas a la piedra")
    cat2 = Categoria("Empanadas", "Empanadas al horno")
    prod1 = Producto("Muzzarella", 9000.0, "Clásica", 10, "muzza.jpg", True, cat1)

    assert cat1 == cat1
    assert cat1 != cat2
    # Mismo tipo diferente nunca debe dar True aunque coincida el ID
    assert cat1 != prod1
    print("[OK] Base, abstracción e igualdad lógica (__eq__)")


# 2. Prueba CRUD, duplicados case-insensitive y restricción de baja en Categorías
def probar_categorias() -> None:
    cat_srv = CategoriaServicio()
    prod_srv = ProductoServicio()

    bebidas = cat_srv.crear("Bebidas", "Gaseosas y aguas")
    assert len(cat_srv.listar_activas()) == 1

    # Nombre duplicado sin importar mayúsculas/minúsculas
    verificar_error(DuplicadoError, cat_srv.crear, "  bebidas ", "Otra descripción")

    # Edición conservando descripción con None
    cat_srv.editar(bebidas.id, "Bebidas Frías", None)
    assert bebidas.nombre == "Bebidas Frías"
    assert bebidas.descripcion == "Gaseosas y aguas"

    # No se puede eliminar si tiene productos activos
    prod = prod_srv.crear("Agua 500ml", 1500.0, "Sin gas", 10, "agua.jpg", True, bebidas)
    cant = prod_srv.contar_activos_por_categoria(bebidas.id)
    verificar_error(OperacionNoPermitidaError, cat_srv.eliminar, bebidas.id, cant)

    # Al eliminar el producto, recién se permite eliminar la categoría
    prod_srv.eliminar(prod.id)
    cant = prod_srv.contar_activos_por_categoria(bebidas.id)
    cat_srv.eliminar(bebidas.id, cant)

    assert bebidas.eliminado is True
    assert len(cat_srv.listar_activas()) == 0
    verificar_error(EntidadNoEncontradaError, cat_srv.buscar_por_id, bebidas.id)
    print("[OK] CategoriaServicio")


# 3. Prueba validaciones, disponibilidad para cliente y baja lógica en Productos
def probar_productos() -> None:
    cat_srv = CategoriaServicio()
    prod_srv = ProductoServicio()

    cat = cat_srv.crear("Postres", "Dulces caseros")
    p1 = prod_srv.crear("Flan", 3500.0, "Con dulce de leche", 5, "flan.jpg", True, cat)
    p2 = prod_srv.crear("Helado", 4000.0, "Sin stock", 0, "helado.jpg", True, cat)
    p3 = prod_srv.crear("Tiramisú", 4500.0, "No disponible", 8, "tiramisu.jpg", False, cat)

    # Validación de datos inválidos
    verificar_error(DatoInvalidoError, prod_srv.crear, "", 1000.0, "Desc", 5, "img.jpg", True, cat)
    verificar_error(DatoInvalidoError, prod_srv.crear, "Torta", -500.0, "Desc", 5, "img.jpg", True, cat)

    # Admin ve los 3 activos; cliente solo ve el disponible con stock > 0
    assert len(prod_srv.listar_activos()) == 3
    disponibles = prod_srv.listar_disponibles()
    assert len(disponibles) == 1
    assert disponibles[0] == p1

    prod_srv.eliminar(p2.id)
    assert p2.eliminado is True
    assert len(prod_srv.listar_activos()) == 2
    assert p3 in prod_srv.listar_activos()
    print("[OK] ProductoServicio")


# 4. Prueba alta, mail único, login y protección de auto-eliminación en Usuarios
def probar_usuarios() -> None:
    usr_srv = UsuarioServicio()

    admin = usr_srv.crear("Ana", "Pérez", "admin@test.com", "2610001", "admin123", Rol.ADMIN)
    cliente = usr_srv.crear("Luis", "Díaz", "luis@test.com", "2610002", "clave123", Rol.USUARIO)

    # Mail duplicado
    verificar_error(DuplicadoError, usr_srv.crear, "Otro", "User", "ADMIN@test.com", "123", "abc", Rol.USUARIO)

    # Autenticación correcta e incorrecta
    assert usr_srv.autenticar("luis@test.com", "clave123") == cliente
    verificar_error(CredencialesInvalidasError, usr_srv.autenticar, "luis@test.com", "incorrecta")
    verificar_error(CredencialesInvalidasError, usr_srv.autenticar, "noexiste@test.com", "clave123")

    # El administrador en sesión no puede eliminarse a sí mismo
    verificar_error(OperacionNoPermitidaError, usr_srv.eliminar, admin.id, admin.id)

    # Eliminar cliente e impedir que vuelva a iniciar sesión
    usr_srv.eliminar(cliente.id, admin.id)
    assert cliente.eliminado is True
    verificar_error(CredencialesInvalidasError, usr_srv.autenticar, "luis@test.com", "clave123")
    print("[OK] UsuarioServicio")


# 5. Prueba atomicidad de stock, cálculo de total, estados, devolución de stock y aislamiento por usuario
def probar_pedidos() -> None:
    cat_srv = CategoriaServicio()
    prod_srv = ProductoServicio()
    usr_srv = UsuarioServicio()
    ped_srv = PedidoServicio()

    cat = cat_srv.crear("Minutas", "Comida rápida")
    p1 = prod_srv.crear("Lomo", 10000.0, "Completo", 10, "lomo.jpg", True, cat)
    p2 = prod_srv.crear("Papas", 4000.0, "Porción grande", 3, "papas.jpg", True, cat)

    c1 = usr_srv.crear("Juan", "Gómez", "juan@test.com", "111", "1234", Rol.USUARIO)
    c2 = usr_srv.crear("Sofía", "Ruiz", "sofia@test.com", "222", "1234", Rol.USUARIO)

    # Atomicidad: p1 tiene stock pero p2 no alcanza -> no debe descontar stock de p1 ni crear el pedido
    verificar_error(StockInsuficienteError, ped_srv.crear, c1, FormaPago.EFECTIVO, [(p1, 2), (p2, 5)])
    assert p1.stock == 10
    assert p2.stock == 3
    assert len(ped_srv.listar_activos()) == 0

    # Creación exitosa: descuenta stock y calcula total (2 * 10000 + 2 * 4000 = 28000)
    pedido1 = ped_srv.crear(c1, FormaPago.TARJETA, [(p1, 2), (p2, 2)])
    assert pedido1.total == 28000.0
    assert p1.stock == 8
    assert p2.stock == 1
    assert pedido1.estado is Estado.PENDIENTE

    # Aislamiento: c2 no puede ver el pedido de c1
    verificar_error(EntidadNoEncontradaError, ped_srv.buscar_por_id_y_usuario, pedido1.id, c2.id)
    assert ped_srv.buscar_por_id_y_usuario(pedido1.id, c1.id) == pedido1

    # Transiciones de estado válidas e inválidas
    verificar_error(OperacionNoPermitidaError, ped_srv.actualizar_estado, pedido1.id, Estado.TERMINADO)
    ped_srv.actualizar_estado(pedido1.id, Estado.CONFIRMADO)
    ped_srv.actualizar_estado(pedido1.id, Estado.TERMINADO)
    # Estado final no admite cambios
    verificar_error(OperacionNoPermitidaError, ped_srv.actualizar_estado, pedido1.id, Estado.CANCELADO)
    verificar_error(OperacionNoPermitidaError, ped_srv.actualizar_forma_pago, pedido1.id, FormaPago.EFECTIVO)

    # Cancelar pedido devuelve stock
    pedido2 = ped_srv.crear(c2, FormaPago.TRANSFERENCIA, [(p1, 3)])
    assert p1.stock == 5
    ped_srv.actualizar_estado(pedido2.id, Estado.CANCELADO)
    assert p1.stock == 8

    # Eliminar pedido abierto devuelve stock y marca eliminados el pedido y sus detalles
    pedido3 = ped_srv.crear(c2, FormaPago.EFECTIVO, [(p1, 2)])
    assert p1.stock == 6
    ped_srv.eliminar(pedido3.id)
    assert p1.stock == 8
    assert pedido3.eliminado is True
    for l in pedido3.detalles:
        assert l.eliminado is True

    print("[OK] PedidoServicio")


# 6. Prueba polimorfismo de menús según el rol del usuario
def probar_polimorfismo_menus() -> None:
    cat_srv = CategoriaServicio()
    prod_srv = ProductoServicio()
    usr_srv = UsuarioServicio()
    ped_srv = PedidoServicio()

    admin = usr_srv.crear("Ana", "Admin", "a@test.com", "111", "123", Rol.ADMIN)
    cliente = usr_srv.crear("Leo", "Cliente", "c@test.com", "222", "123", Rol.USUARIO)

    menu_admin = crear_menu(admin, cat_srv, prod_srv, usr_srv, ped_srv)
    menu_cliente = crear_menu(cliente, cat_srv, prod_srv, usr_srv, ped_srv)

    assert isinstance(menu_admin, Menu)
    assert isinstance(menu_admin, MenuAdministrador)
    assert isinstance(menu_cliente, Menu)
    assert isinstance(menu_cliente, MenuCliente)
    print("[OK] Polimorfismo de menús")

if __name__ == "__main__":
    print("=== EJECUTANDO PRUEBAS DE FOOD STORE ===")
    probar_base_y_abstraccion()
    probar_categorias()
    probar_productos()
    probar_usuarios()
    probar_pedidos()
    probar_polimorfismo_menus()
    print("=== TODAS LAS PRUEBAS PASARON CORRECTAMENTE ===")