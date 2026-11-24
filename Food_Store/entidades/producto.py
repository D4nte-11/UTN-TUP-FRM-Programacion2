from entidades.base import Base
from entidades.categoria import Categoria
from excepciones.errores import DatoInvalidoError

class Producto(Base):
    def __init__(self, nombre: str, precio: float, descripcion: str, stock: int, imagen: str, disponible: bool, categoria: Categoria) -> None:
        super().__init__()
        self.nombre = nombre
        self.precio = precio
        self.descripcion = descripcion
        self.stock = stock
        self.imagen = imagen
        self.disponible = disponible
        self.categoria = categoria
    
    # == Getters ==
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio(self) -> float:
        return self._precio

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def stock(self) -> int:
        return self._stock

    @property
    def imagen(self) -> str:
        return self._imagen

    @property
    def disponible(self) -> bool:
        return self._disponible

    @property
    def categoria(self) -> Categoria:
        return self._categoria

    # == Setters ==
    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("Error: El nombre debe ser un texto no vacío.")
        self._nombre = valor
    
    @precio.setter
    def precio(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or valor < 0:
            raise DatoInvalidoError("Error: El precio del producto debe ser un número positivo.")
        self._precio = valor

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("Error: La descripción del producto debe ser un texto no vacío.")
        self._descripcion = valor

    @stock.setter
    def stock(self, valor: int) -> None:
        if not isinstance(valor, int) or valor < 0:
            raise DatoInvalidoError("Error: El stock del producto debe ser un número positivo.")
        self._stock = valor
    
    @imagen.setter
    def imagen(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("Error: La ruta o nombre de la imágen debe ser un texto no vacío.")
        self._imagen = valor

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise DatoInvalidoError("Error: La disponibilidad del producto debe ser un booleano.")
        self._disponible = valor

    @categoria.setter
    def categoria(self, valor: Categoria) -> None:
        if not isinstance(valor, Categoria):
            raise DatoInvalidoError("Error: La categoría debe ser una instancia válida de Categoría.")
        self._categoria = valor

# == Métodos Especiales ==
# Devuelve los datos del producto con formato de precio y disponibilidad legible
    def __str__(self) -> str:
        estado = "Disponible" if self.disponible else "No disponible"
        return (f"[{self.id}] {self.nombre} ({self.categoria.nombre}) | ${self.precio:,.2f} | Stock: {self.stock} | {estado}")