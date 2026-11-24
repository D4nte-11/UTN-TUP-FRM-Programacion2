from entidades.base import Base
from enums.rol import Rol
from excepciones.errores import DatoInvalidoError

class Usuario(Base):
    def __init__(self, nombre: str, apellido: str, mail: str, celular: str, contrasenia: str, rol: Rol) -> None:
        super().__init__()
        self.nombre = nombre
        self.apellido = apellido
        self.mail = mail
        self.celular = celular
        self.rol = rol
        self._validar_asignar_contrasenia(contrasenia)

    # == Getters ==

    @property
    def nombre(self):
        return self._nombre

    @property
    def apellido(self) -> str:
        return self._apellido

    @property
    def mail(self) -> str:
        return self._mail

    @property
    def celular(self) -> str:
        return self._celular

    @property
    def rol(self) -> Rol:
        return self._rol

    # == Setters ==

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("Error: El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @apellido.setter
    def apellido(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("Error: El apellido no puede estar vacío.")
        self._apellido = valor.strip()

    @mail.setter
    def mail(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("Error: El mail no puede estar vacío.")
        mail_limpio = valor.strip()
        if "@" not in mail_limpio or "." not in mail_limpio:
            raise DatoInvalidoError("Error: El formato del mail es inválido (tiene que contener '@' y '.').")
        self._mail = mail_limpio

    @celular.setter
    def celular(self, valor: str) -> None:
        if not isinstance(valor,str) or not valor.strip():
            raise DatoInvalidoError("Error: El celular no puede estar vacio")
        self._celular = valor.strip()

    @rol.setter
    def rol(self, valor: Rol) -> None:
        if not isinstance(valor, Rol):
            raise DatoInvalidoError("Error: Debe ser un Rol válido")
        self._rol = valor

# == Métodos ==
    def _validar_asignar_contrasenia(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise DatoInvalidoError("Error: La contraseña no puede estar vacia")
        self._contrasenia = valor

    def verificar_contrasenia(self, contrasenia: str) -> bool:
        return self._contrasenia == contrasenia

# == Métodos Especiales ==
    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} {self.apellido} | {self.mail} | {self.rol.name}"