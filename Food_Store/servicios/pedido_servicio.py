from datetime import date
from entidades.pedido import Pedido
from entidades.producto import Producto
from entidades.usuario import Usuario
from enums.estado import Estado
from enums.forma_pago import FormaPago
from excepciones.errores import (DatoInvalidoError,EntidadNoEncontradaError,OperacionNoPermitidaError,StockInsuficienteError)

class PedidoServicio:
    # Mapa de transiciones de estado válidas según las reglas de negocio
    _TRANSICIONES_VALIDAS: dict[Estado, set[Estado]] = {
        Estado.PENDIENTE: {Estado.CONFIRMADO, Estado.CANCELADO},
        Estado.CONFIRMADO: {Estado.TERMINADO, Estado.CANCELADO},
        Estado.TERMINADO: set(),
        Estado.CANCELADO: set(),
    }

    def __init__(self) -> None:
        self._pedidos: list[Pedido] = []

    def listar_activos(self) -> list[Pedido]:
        #Devuelve todos los pedidos no eliminados.
        return [l for l in self._pedidos if not l.eliminado]

    def listar_por_usuario(self, id_usuario: int) -> list[Pedido]:
        #Devuelve los pedidos activos pertenecientes a un usuario específico.
        return [l for l in self._pedidos if not l.eliminado and l.usuario.id == id_usuario]

    def buscar_por_id(self, id_pedido: int) -> Pedido:
        #Busca un pedido activo por su ID; lanza error si no existe o está eliminado.
        for l in self._pedidos:
            if l.id == id_pedido and not l.eliminado:
                return l
        raise EntidadNoEncontradaError(f"Error: No se encontró un pedido activo con ID {id_pedido}.")

    def buscar_por_id_y_usuario(self, id_pedido: int, id_usuario: int) -> Pedido:
        #Busca un pedido asegurando que pertenezca al usuario indicado.
        pedido = self.buscar_por_id(id_pedido)
        if pedido.usuario.id != id_usuario:
            # La consigna exige informarlo como inexistente si es de otro usuario
            raise EntidadNoEncontradaError(f"Error: No se encontró un pedido activo con ID {id_pedido}.")
        return pedido

    def crear(self,usuario: Usuario,forma_pago: FormaPago,items: list[tuple[Producto, int]]) -> Pedido:
        #Crea un pedido con sus detalles de forma atómica.
        #'items' es una lista de tuplas (producto, cantidad).

        if usuario is None or usuario.eliminado:
            raise OperacionNoPermitidaError("Error: No se puede crear un pedido para un usuario inexistente o eliminado.")
        if not items:
            raise DatoInvalidoError("Error: El pedido debe contener al menos un producto.")
        # 1. Creamos el pedido en estado PENDIENTE con fecha de hoy
        nuevo_pedido = Pedido(usuario, forma_pago)
        # 2. Agregamos los detalles (si alguno falla por stock o producto eliminado, se aborta todo)
        for producto, cantidad in items:
            if producto.eliminado:
                raise OperacionNoPermitidaError(f"Error: El producto '{producto.nombre}' está eliminado.")
            # Verificamos el stock acumulado si el mismo producto viene repetido en 'items'
            detalle_existente = nuevo_pedido.buscar_detalle_por_producto(producto)
            cantidad_total_pedida = cantidad + (detalle_existente.cantidad if detalle_existente else 0)
            if cantidad_total_pedida > producto.stock:
                raise StockInsuficienteError(f"Error: Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock}, solicitado: {cantidad_total_pedida}.")
            nuevo_pedido.agregar_detalle(cantidad, producto)

        # 3. Calculamos el total usando obligatoriamente la interfaz Calculable
        nuevo_pedido.calcular_total()

        # 4. Como todo salió bien, recién ahora descontamos el stock real de cada producto
        for detalle in nuevo_pedido.detalles:
            detalle.producto.stock -= detalle.cantidad
        self._pedidos.append(nuevo_pedido)
        return nuevo_pedido

    def _devolver_stock(self, pedido: Pedido) -> None:
        #Restituye el stock de los productos asociados a los detalles del pedido.
        for detalle in pedido.detalles:
            detalle.producto.stock += detalle.cantidad

    def actualizar_estado(self, id_pedido: int, nuevo_estado: Estado) -> Pedido:
        #Valida y aplica el cambio de estado, devolviendo stock si se cancela.
        pedido = self.buscar_por_id(id_pedido)
        if pedido.estado is nuevo_estado:
            return pedido
        permitidos = self._TRANSICIONES_VALIDAS.get(pedido.estado, set())
        if nuevo_estado not in permitidos:
            raise OperacionNoPermitidaError(f"Eror: Transición inválida: no se puede pasar de {pedido.estado.name} a {nuevo_estado.name}.")
        pedido.estado = nuevo_estado
        if nuevo_estado is Estado.CANCELADO:
            self._devolver_stock(pedido)
        return pedido

    def actualizar_forma_pago(self, id_pedido: int, nueva_forma_pago: FormaPago) -> Pedido:
        #Actualiza la forma de pago si el pedido sigue abierto.
        pedido = self.buscar_por_id(id_pedido)
        if pedido.estado in (Estado.TERMINADO, Estado.CANCELADO):
            raise OperacionNoPermitidaError(f"Error: No se puede modificar la forma de pago de un pedido {pedido.estado.name}.")
        pedido.forma_pago = nueva_forma_pago
        return pedido

    def eliminar(self, id_pedido: int) -> None:
        #Realiza la baja lógica del pedido y sus detalles, devolviendo stock si corresponde.
        pedido = self.buscar_por_id(id_pedido)
        if pedido.estado not in (Estado.TERMINADO, Estado.CANCELADO):
            self._devolver_stock(pedido)
        pedido.eliminado = True
        for detalle in pedido.detalles:
            detalle.eliminado = True