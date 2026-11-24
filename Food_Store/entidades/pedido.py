from datetime import date
from calculable import Calculable
from entidades.base import Base
from entidades.detalle_pedido import DetallePedido
from entidades.producto import Producto
from entidades.usuario import Usuario
from enums.estado import Estado
from enums.forma_pago import FormaPago
from excepciones.errores import (DatoInvalidoError, EntidadNoEncontradaError, StockInsuficienteError)

class Pedido(Base, Calculable):
    def __init__(self, usuario: Usuario, forma_pago: FormaPago) -> None:
        super().__init__()
        self.usuario = usuario
        self.forma_pago = forma_pago
        self._fecha: date = date.today()
        self._estado: Estado = Estado.PENDIENTE
        self._total: float = 0.0
        self._detalles: list[DetallePedido] = []

#== Getters ==
    @property
    def usuario(self) -> Usuario:
        return self._usuario

    @property
    def fecha(self) -> date:
        return self._fecha

    @property
    def estado(self) -> Estado:
        return self._estado

    @property
    def total(self) -> float:
        return self._total

    @property
    def forma_pago(self) -> FormaPago:
        return self._forma_pago

    @property
    def detalles(self) -> tuple[DetallePedido, ...]:
        return tuple(self._detalles)

# == Setters ==
    @usuario.setter
    def usuario(self, valor: Usuario) -> None:
        if not isinstance(valor, Usuario) or valor.eliminado:
            raise DatoInvalidoError("Error: El pedido debe pertenecer a un usuario válido y activo.")
        self._usuario = valor

    @estado.setter
    def estado(self, valor: Estado) -> None:
        if not isinstance(valor, Estado):
            raise DatoInvalidoError("Error: El estado debe ser una instancia válida de Estado.")
        self._estado = valor

    @forma_pago.setter
    def forma_pago(self, valor: FormaPago) -> None:
        if not isinstance(valor, FormaPago):
            raise DatoInvalidoError("Error: La forma de pago debe ser un metodo válido")
        self._forma_pago = valor

# == Métodos ==
    def agregar_detalle(self, cantidad: int, producto: Producto) -> None:
        if not isinstance(producto, Producto) or producto.eliminado:
            raise DatoInvalidoError("Error: Debe ser un producto valido")
        if cantidad <= 0:
            raise DatoInvalidoError("Error: La cantidad debe ser mayor a 0")
        detalle_existente = self.buscar_detalle_por_producto(producto)
        if detalle_existente is not None:
            nueva_cantidad = detalle_existente.cantidad + cantidad
            if nueva_cantidad > producto.stock:
                raise StockInsuficienteError(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}")
            detalle_existente.cantidad = nueva_cantidad
        else:
            if cantidad > producto.stock:
                raise StockInsuficienteError(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}")
            nuevo_detalle = DetallePedido(producto = producto, cantidad = cantidad)
            self._detalles.append(nuevo_detalle)
        self.calcular_total()

    def buscar_detalle_por_producto(self, producto: Producto) -> DetallePedido | None:
        for detalle in self._detalles:
            if detalle.producto == producto:
                return detalle
        return None

    def eliminar_detalle_por_producto(self, producto: Producto) -> None:
        detalle = self.buscar_detalle_por_producto(producto)
        if detalle is None:
            raise EntidadNoEncontradaError("Error: El producto no se encuentra en el pedido")
        self._detalles.remove(detalle)
        self.calcular_total()

    def calcular_total(self) -> None:
        self._total = sum(detalle.subtotal for detalle in self._detalles)

# == Metodos Especiales ==
    def __str__(self) -> str:
        return f"[{self.id}] Usuario: {self.usuario.nombre} {self.usuario.apellido} | Estado: {self.estado.name} | Pago: {self.forma_pago.name} | Total: ${self.total:.2f} | Fecha: {self.fecha} |"