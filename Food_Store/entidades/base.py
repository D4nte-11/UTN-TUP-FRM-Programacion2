from abc import ABC, abstractmethod
from datetime import datetime

class Base(ABC):
    _contador_id: int = 0

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        #Cada clase hija recibe su propio contador independiente en 0
        cls._contador_id = 0

    def __init__(self) -> None:
        # type(self) apunta a la clase hija exacta (ej. Producto o Usuario)
        clase = type(self)
        clase._contador_id += 1
        self._id: int = clase._contador_id 
        self._eliminado: bool = False
        self._creado_en: datetime = datetime.now()

    @abstractmethod
    def __str__(self) -> str:
        pass

    # == Getters ==
    @property
    def id(self) -> int:
        return self._id

    @property
    def eliminado(self) -> bool:
        return self._eliminado

    @property
    def creado_en(self) -> datetime:
        return self._creado_en

    # == Setter ==
    @eliminado.setter
    def eliminado(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise TypeError("El atributo 'eliminado' debe ser un booleano.")
        self._eliminado = valor

    # == Métodos Especiales ==
    #Compara dos productos o usuarios
    def __eq__(self, otro: object) -> bool:
        if type(self) is not type(otro):
            return False
        return self._id == otro._id