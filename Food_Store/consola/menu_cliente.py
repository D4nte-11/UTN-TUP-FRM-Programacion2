from consola.lectura import leer_confirmacion, leer_entero, leer_opcion_menu
from consola.menu import Menu
from entidades.usuario import Usuario
from excepciones.errores import FoodStoreError
from servicios.categoria_servicio import CategoriaServicio
from servicios.pedido_servicio import PedidoServicio
from servicios.producto_servicio import ProductoServicio

class MenuCliente(Menu):
    def __init__(self, usuario: Usuario, categoria_servicio: CategoriaServicio, producto_servicio: ProductoServicio, pedido_servicio: PedidoServicio) -> None:
        super().__init__(usuario)
        self._categoria_servicio = categoria_servicio
        self._producto_servicio = producto_servicio
        self._pedido_servicio = pedido_servicio

    # Muestra el menú de solo consulta para el cliente; devuelve True para cerrar sesión o False para salir
    def mostrar(self) -> bool:
        while True:
            print(f"\n=== FOOD STORE - CLIENTE ({self._usuario.nombre} {self._usuario.apellido}) ===")
            print("1. Ver categorías")
            print("2. Ver productos disponibles")
            print("3. Mis pedidos")
            print("4. Mis datos")
            print("9. Cerrar sesión")
            print("0. Salir")
            opcion = leer_opcion_menu({1, 2, 3, 4, 9, 0})

            match opcion:
                case 1:
                    self._ver_categorias()
                case 2:
                    self._ver_productos_disponibles()
                case 3:
                    self._ver_mis_pedidos()
                case 4:
                    self._ver_mis_datos()
                case 9:
                    print("Cerrando sesión...")
                    return True
                case 0:
                    print("Saliendo del sistema...")
                    return False

    # Lista las categorías activas
    def _ver_categorias(self) -> None:
        print("\n--- CATEGORÍAS ---")
        categorias = self._categoria_servicio.listar_activas()
        if not categorias:
            print("No hay categorías cargadas.")
            return
        for l in categorias:
            print(l)

    # Lista únicamente los productos activos, disponibles y con stock mayor a 0
    def _ver_productos_disponibles(self) -> None:
        print("\n--- PRODUCTOS DISPONIBLES ---")
        productos = self._producto_servicio.listar_disponibles()
        if not productos:
            print("No hay productos disponibles en este momento.")
            return
        for l in productos:
            print(l)

    # Muestra los pedidos activos del cliente en sesión y permite consultar sus detalles por ID
    def _ver_mis_pedidos(self) -> None:
        print("\n--- MIS PEDIDOS ---")
        pedidos = self._pedido_servicio.listar_por_usuario(self._usuario.id)
        if not pedidos:
            print("No tenés pedidos registrados.")
            return
        for l in pedidos:
            print(l)

        if leer_confirmacion("\n¿Desea ver el detalle de algún pedido?"):
            id_pedido = leer_entero("Ingrese el ID del pedido: ", minimo=1)
            if id_pedido is None:
                return
            try:
                pedido = self._pedido_servicio.buscar_por_id_y_usuario(id_pedido, self._usuario.id)
                print(f"\n--- DETALLE DEL PEDIDO #{pedido.id} ---")
                for l in pedido.detalles:
                    print(f"  - {l}")
                print(f"Total: ${pedido.total:,.2f}")
            except FoodStoreError as e:
                print(e)

    # Muestra los datos personales del cliente en sesión sin exponer la contraseña
    def _ver_mis_datos(self) -> None:
        print("\n--- MIS DATOS ---")
        print(f"Nombre: {self._usuario.nombre}")
        print(f"Apellido: {self._usuario.apellido}")
        print(f"Mail: {self._usuario.mail}")
        print(f"Celular: {self._usuario.celular}")
        print(f"Rol: {self._usuario.rol.value}")