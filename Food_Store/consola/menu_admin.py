from consola.lectura import (leer_confirmacion, leer_entero, leer_enum, leer_flotante, leer_opcion_menu, leer_texto)
from consola.menu import Menu
from entidades.producto import Producto
from entidades.usuario import Usuario
from enums.estado import Estado
from enums.forma_pago import FormaPago
from enums.rol import Rol
from excepciones.errores import FoodStoreError
from servicios.categoria_servicio import CategoriaServicio
from servicios.pedido_servicio import PedidoServicio
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio

class MenuAdministrador(Menu):
    def __init__(self, usuario: Usuario, categoria_servicio: CategoriaServicio, producto_servicio: ProductoServicio, usuario_servicio: UsuarioServicio, pedido_servicio: PedidoServicio) -> None:
        super().__init__(usuario)
        self._categoria_servicio = categoria_servicio
        self._producto_servicio = producto_servicio
        self._usuario_servicio = usuario_servicio
        self._pedido_servicio = pedido_servicio

    # Muestra el menú principal del administrador; devuelve True para cerrar sesión o False para salir
    def mostrar(self) -> bool:
        while True:
            print(f"\n=== FOOD STORE - ADMINISTRADOR ({self._usuario.nombre} {self._usuario.apellido}) ===")
            print("1. Categorías")
            print("2. Productos")
            print("3. Usuarios")
            print("4. Pedidos")
            print("9. Cerrar sesión")
            print("0. Salir")
            opcion = leer_opcion_menu({1, 2, 3, 4, 9, 0})

            if opcion == 1:
                self._submenu_categorias()
            elif opcion == 2:
                self._submenu_productos()
            elif opcion == 3:
                self._submenu_usuarios()
            elif opcion == 4:
                self._submenu_pedidos()
            elif opcion == 9:
                print("Cerrando sesión...")
                return True
            elif opcion == 0:
                print("Saliendo del sistema...")
                return False

    # ==================== SUBMENÚ CATEGORÍAS ====================
    def _submenu_categorias(self) -> None:
        while True:
            print("\n--- CATEGORÍAS ---")
            print("1. Listar")
            print("2. Crear")
            print("3. Editar")
            print("4. Eliminar")
            print("0. Volver")
            opcion = leer_opcion_menu({1, 2, 3, 4, 0})

            if opcion == 1:
                self._listar_categorias()
            elif opcion == 2:
                self._crear_categoria()
            elif opcion == 3:
                self._editar_categoria()
            elif opcion == 4:
                self._eliminar_categoria()
            elif opcion == 0:
                return

    def _listar_categorias(self) -> None:
        categorias = self._categoria_servicio.listar_activas()
        if not categorias:
            print("No hay categorías cargadas.")
            return
        for l in categorias:
            print(l)

    def _crear_categoria(self) -> None:
        nombre = leer_texto("Nombre: ")
        descripcion = leer_texto("Descripción: ")
        if nombre is None or descripcion is None:
            return
        try:
            categoria = self._categoria_servicio.crear(nombre, descripcion)
            print(f"Categoría creada correctamente con ID {categoria.id}.")
        except FoodStoreError as e:
            print(e)

    def _editar_categoria(self) -> None:
        self._listar_categorias()
        id_cat = leer_entero("Ingrese el ID de la categoría a editar: ", minimo=1)
        if id_cat is None:
            return
        try:
            self._categoria_servicio.buscar_por_id(id_cat)
            print("(Presione Enter para conservar el valor actual)")
            nuevo_nombre = leer_texto("Nuevo nombre: ", permitir_vacio=True)
            nueva_desc = leer_texto("Nueva descripción: ", permitir_vacio=True)
            self._categoria_servicio.editar(id_cat, nuevo_nombre, nueva_desc)
            print("Categoría actualizada correctamente.")
        except FoodStoreError as e:
            print(e)

    def _eliminar_categoria(self) -> None:
        self._listar_categorias()
        id_cat = leer_entero("Ingrese el ID de la categoría a eliminar: ", minimo=1)
        if id_cat is None:
            return
        try:
            categoria = self._categoria_servicio.buscar_por_id(id_cat)
            if not leer_confirmacion(f"¿Confirma eliminar la categoría '{categoria.nombre}'?"):
                print("Operación cancelada.")
                return
            cant_productos = self._producto_servicio.contar_activos_por_categoria(id_cat)
            self._categoria_servicio.eliminar(id_cat, cant_productos)
            print("Categoría eliminada correctamente.")
        except FoodStoreError as e:
            print(e)

    # ==================== SUBMENÚ PRODUCTOS ====================
    def _submenu_productos(self) -> None:
        while True:
            print("\n--- PRODUCTOS ---")
            print("1. Listar")
            print("2. Crear")
            print("3. Editar")
            print("4. Eliminar")
            print("0. Volver")
            opcion = leer_opcion_menu({1, 2, 3, 4, 0})

            if opcion == 1:
                self._listar_productos()
            elif opcion == 2:
                self._crear_producto()
            elif opcion == 3:
                self._editar_producto()
            elif opcion == 4:
                self._eliminar_producto()
            elif opcion == 0:
                return

    def _listar_productos(self) -> None:
        productos = self._producto_servicio.listar_activos()
        if not productos:
            print("No hay productos cargados.")
            return
        for l in productos:
            print(l)

    def _crear_producto(self) -> None:
        categorias = self._categoria_servicio.listar_activas()
        if not categorias:
            print("Error: Debe crear al menos una categoría antes de cargar productos.")
            return

        nombre = leer_texto("Nombre: ")
        descripcion = leer_texto("Descripción: ")
        precio = leer_flotante("Precio: ", minimo=0.0)
        stock = leer_entero("Stock: ", minimo=0)
        imagen = leer_texto("Imagen (ruta o nombre): ")
        disponible = leer_confirmacion("¿Está disponible?")

        print("\nCategorías disponibles:")
        for l in categorias:
            print(l)
        id_cat = leer_entero("ID de categoría: ", minimo=1)

        if (nombre is None or descripcion is None or precio is None or stock is None or imagen is None or disponible is None or id_cat is None):
            return

        try:
            categoria = self._categoria_servicio.buscar_por_id(id_cat)
            producto = self._producto_servicio.crear(nombre, precio, descripcion, stock, imagen, disponible, categoria)
            print(f"Producto creado correctamente con ID {producto.id}.")
        except FoodStoreError as e:
            print(e)

    def _editar_producto(self) -> None:
        self._listar_productos()
        id_prod = leer_entero("Ingrese el ID del producto a editar: ", minimo=1)
        if id_prod is None:
            return
        try:
            self._producto_servicio.buscar_por_id(id_prod)
            print("(Presione Enter para conservar el valor actual)")
            nuevo_nombre = leer_texto("Nuevo nombre: ", permitir_vacio=True)
            nueva_desc = leer_texto("Nueva descripción: ", permitir_vacio=True)
            nuevo_precio = leer_flotante("Nuevo precio: ", minimo=0.0, permitir_vacio=True)
            nuevo_stock = leer_entero("Nuevo stock: ", minimo=0, permitir_vacio=True)
            nueva_imagen = leer_texto("Nueva imagen: ", permitir_vacio=True)
            nueva_disp = leer_confirmacion("¿Está disponible?", permitir_vacio=True)
            nueva_categoria = None
            if leer_confirmacion("¿Desea cambiar la categoría?"):
                self._listar_categorias()
                id_cat = leer_entero("Nuevo ID de categoría: ", minimo=1)
                if id_cat is not None:
                    nueva_categoria = self._categoria_servicio.buscar_por_id(id_cat)

            self._producto_servicio.editar(id_prod, nuevo_nombre, nuevo_precio, nueva_desc, nuevo_stock, nueva_imagen, nueva_disp, nueva_categoria)
            print("Producto actualizado correctamente.")
        except FoodStoreError as e:
            print(e)

    def _eliminar_producto(self) -> None:
        self._listar_productos()
        id_prod = leer_entero("Ingrese el ID del producto a eliminar: ", minimo=1)
        if id_prod is None:
            return
        try:
            producto = self._producto_servicio.buscar_por_id(id_prod)
            if not leer_confirmacion(f"¿Confirma eliminar el producto '{producto.nombre}'?"):
                print("Operación cancelada.")
                return
            self._producto_servicio.eliminar(id_prod)
            print("Producto eliminado correctamente.")
        except FoodStoreError as e:
            print(e)

    # ==================== SUBMENÚ USUARIOS ====================
    def _submenu_usuarios(self) -> None:
        while True:
            print("\n--- USUARIOS ---")
            print("1. Listar")
            print("2. Crear")
            print("3. Editar")
            print("4. Eliminar")
            print("0. Volver")
            opcion = leer_opcion_menu({1, 2, 3, 4, 0})

            if opcion == 1:
                self._listar_usuarios()
            elif opcion == 2:
                self._crear_usuario()
            elif opcion == 3:
                self._editar_usuario()
            elif opcion == 4:
                self._eliminar_usuario()
            elif opcion == 0:
                return

    def _listar_usuarios(self) -> None:
        usuarios = self._usuario_servicio.listar_activos()
        if not usuarios:
            print("No hay usuarios cargados.")
            return
        for l in usuarios:
            print(l)

    def _crear_usuario(self) -> None:
        nombre = leer_texto("Nombre: ")
        apellido = leer_texto("Apellido: ")
        mail = leer_texto("Mail: ")
        celular = leer_texto("Celular: ")
        contrasenia = leer_texto("Contraseña: ")
        rol = leer_enum("Seleccione el rol:", Rol)

        if (nombre is None or apellido is None or mail is None or celular is None or contrasenia is None or not isinstance(rol, Rol)):
            return
        try:
            usuario = self._usuario_servicio.crear(nombre, apellido, mail, celular, contrasenia, rol)
            print(f"Usuario creado correctamente con ID {usuario.id}.")
        except FoodStoreError as e:
            print(e)

    def _editar_usuario(self) -> None:
        self._listar_usuarios()
        id_usr = leer_entero("Ingrese el ID del usuario a editar: ", minimo=1)
        if id_usr is None:
            return
        try:
            self._usuario_servicio.buscar_por_id(id_usr)
            print("(Presione Enter para conservar el valor actual)")
            nuevo_nombre = leer_texto("Nuevo nombre: ", permitir_vacio=True)
            nuevo_apellido = leer_texto("Nuevo apellido: ", permitir_vacio=True)
            nuevo_mail = leer_texto("Nuevo mail: ", permitir_vacio=True)
            nuevo_celular = leer_texto("Nuevo celular: ", permitir_vacio=True)
            nueva_contra = leer_texto("Nueva contraseña: ", permitir_vacio=True)
            nuevo_rol = leer_enum("Nuevo rol (Enter para conservar):", Rol, permitir_vacio=True)
            rol_valido = nuevo_rol if isinstance(nuevo_rol, Rol) else None
            self._usuario_servicio.editar(id_usr, nuevo_nombre, nuevo_apellido, nuevo_mail, nuevo_celular, nueva_contra, rol_valido)
            print("Usuario actualizado correctamente.")
        except FoodStoreError as e:
            print(e)

    def _eliminar_usuario(self) -> None:
        self._listar_usuarios()
        id_usr = leer_entero("Ingrese el ID del usuario a eliminar: ", minimo=1)
        if id_usr is None:
            return
        try:
            usuario = self._usuario_servicio.buscar_por_id(id_usr)
            if not leer_confirmacion(f"¿Confirma eliminar al usuario '{usuario.nombre} {usuario.apellido}'?"):
                print("Operación cancelada.")
                return
            self._usuario_servicio.eliminar(id_usr, self._usuario.id)
            print("Usuario eliminado correctamente.")
        except FoodStoreError as e:
            print(e)

    # ==================== SUBMENÚ PEDIDOS ====================
    def _submenu_pedidos(self) -> None:
        while True:
            print("\n--- PEDIDOS ---")
            print("1. Listar")
            print("2. Crear")
            print("3. Actualizar estado / forma de pago")
            print("4. Eliminar")
            print("0. Volver")
            opcion = leer_opcion_menu({1, 2, 3, 4, 0})

            if opcion == 1:
                self._listar_pedidos()
            elif opcion == 2:
                self._crear_pedido()
            elif opcion == 3:
                self._editar_pedido()
            elif opcion == 4:
                self._eliminar_pedido()
            elif opcion == 0:
                return

    def _listar_pedidos(self) -> None:
        pedidos = self._pedido_servicio.listar_activos()
        if not pedidos:
            print("No hay pedidos cargados.")
            return
        for l in pedidos:
            print(l)

        if leer_confirmacion("\n¿Desea ver los detalles de algún pedido?"):
            id_ped = leer_entero("Ingrese el ID del pedido: ", minimo=1)
            if id_ped is None:
                return
            try:
                pedido = self._pedido_servicio.buscar_por_id(id_ped)
                print(f"\n--- DETALLE DEL PEDIDO #{pedido.id} ---")
                for l in pedido.detalles:
                    print(f"  - {l}")
                print(f"Total: ${pedido.total:,.2f}")
            except FoodStoreError as e:
                print(e)

    def _crear_pedido(self) -> None:
        usuarios = self._usuario_servicio.listar_activos()
        if not usuarios:
            print("Error: No hay usuarios activos para asociar al pedido.")
            return
        productos = self._producto_servicio.listar_activos()
        if not productos:
            print("Error: No hay productos activos para agregar al pedido.")
            return
        print("\nUsuarios disponibles:")
        for l in usuarios:
            print(l)
        id_usr = leer_entero("ID del usuario: ", minimo=1)
        if id_usr is None:
            return
        try:
            usuario = self._usuario_servicio.buscar_por_id(id_usr)
        except FoodStoreError as e:
            print(e)
            return
        forma_pago = leer_enum("Seleccione la forma de pago:", FormaPago)
        if not isinstance(forma_pago, FormaPago):
            return
        items: list[tuple[Producto, int]] = []
        while True:
            print("\nProductos disponibles:")
            for l in self._producto_servicio.listar_activos():
                print(l)
            id_prod = leer_entero("ID del producto a agregar: ", minimo=1)
            if id_prod is None:
                break
            try:
                producto = self._producto_servicio.buscar_por_id(id_prod)
            except FoodStoreError as e:
                print(e)
                if not leer_confirmacion("¿Desea intentar con otro producto?"):
                    break
                continue
            cantidad = leer_entero("Cantidad: ", minimo=1)
            if cantidad is not None:
                items.append((producto, cantidad))
            if not leer_confirmacion("¿Desea agregar otro producto al pedido?"):
                break
        try:
            pedido = self._pedido_servicio.crear(usuario, forma_pago, items)
            print(f"Pedido creado correctamente con ID {pedido.id} | Total: ${pedido.total:,.2f}")
        except FoodStoreError as e:
            print(e)

    def _editar_pedido(self) -> None:
        pedidos = self._pedido_servicio.listar_activos()
        if not pedidos:
            print("No hay pedidos cargados.")
            return
        for l in pedidos:
            print(l)
        id_ped = leer_entero("Ingrese el ID del pedido a actualizar: ", minimo=1)
        if id_ped is None:
            return
        try:
            self._pedido_servicio.buscar_por_id(id_ped)
            nuevo_estado = leer_enum("Nuevo estado (Enter para conservar):", Estado, permitir_vacio=True)
            nueva_forma = leer_enum("Nueva forma de pago (Enter para conservar):", FormaPago, permitir_vacio=True)
            if isinstance(nueva_forma, FormaPago):
                self._pedido_servicio.actualizar_forma_pago(id_ped, nueva_forma)
            if isinstance(nuevo_estado, Estado):
                self._pedido_servicio.actualizar_estado(id_ped, nuevo_estado)
            print("Pedido actualizado correctamente.")
        except FoodStoreError as e:
            print(e)

    def _eliminar_pedido(self) -> None:
        pedidos = self._pedido_servicio.listar_activos()
        if not pedidos:
            print("No hay pedidos cargados.")
            return
        for l in pedidos:
            print(l)
        id_ped = leer_entero("Ingrese el ID del pedido a eliminar: ", minimo=1)
        if id_ped is None:
            return
        try:
            self._pedido_servicio.buscar_por_id(id_ped)
            if not leer_confirmacion(f"¿Confirma eliminar el pedido #{id_ped}?"):
                print("Operación cancelada.")
                return
            self._pedido_servicio.eliminar(id_ped)
            print("Pedido eliminado correctamente.")
        except FoodStoreError as e:
            print(e)