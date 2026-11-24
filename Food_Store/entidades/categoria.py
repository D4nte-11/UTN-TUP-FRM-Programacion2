from entidades.base import Base
from excepciones.errores import DatoInvalidoError

class Categoria(Base):
    def __init__(self, nombre: str, descripcion: str) -> None:
        super().__init__()
        self.nombre = nombre
        self.descripcion = descripcion

# == Getters ==
    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def descripcion(self) -> str:
        return self._descripcion

# == Setters ==
    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise DatoInvalidoError("Error: El nombre de la categoría debe ser una cadena de texto.")
        self._nombre = valor

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise DatoInvalidoError("Error: La descripción de la categoría no puede estar vacia.")
        self._descripcion = valor.strip()

# == Métodos Especiales ==
    def __str__(self) -> str:
        return f"[{self.id}] | {self.nombre}: {self.descripcion}"

