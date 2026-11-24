from entidades.base import Base
from entidades.producto import Producto
from excepciones.errores import DatoInvalidoError, OperacionNoPermitidaError

class DetallePedido(Base): 
    def __init__(self, producto: Producto, cantidad: int):
        super().__init__()
        self.producto = producto
        self.cantidad = cantidad
        self._subtotal: float = self._cantidad * self._producto.precio

    # == Getters ==
    @property
    def producto(self) -> Producto:
        return self._producto

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @property
    def subtotal(self) -> float:
        return self._subtotal

    # == Setters ==
    @producto.setter
    def producto(self, valor: Producto) -> None:
        if not isinstance(valor, Producto):
            raise DatoInvalidoError("Error: El producto debe ser una instancia válida de Producto.")
        if valor.eliminado:
            raise OperacionNoPermitidaError("Error: No se puede agregar un producto eliminado al pedido.")
        self._producto = valor
    
    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise DatoInvalidoError("Error: La cantidad debe ser un número entero mayor a cero.")
        self._cantidad = valor
        # Si ya existe el producto asignado (ej. al sumar cantidad en un pedido existente), actualiza el subtotal
        if hasattr(self, "_producto"):
            self._subtotal = self._cantidad * self._producto.precio

    # == Métodos Especiales ==
    def __str__(self) -> str:
        return(f"{self._producto.nombre} | Cantidad: {self._cantidad} | Subtotal: ${self._subtotal:,.2f}")
