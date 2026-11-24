from entidades.usuario import Usuario
from enums.rol import Rol
from excepciones.errores import (CredencialesInvalidasError, DuplicadoError, EntidadNoEncontradaError, OperacionNoPermitidaError)


class UsuarioServicio:
    def __init__(self) -> None:
        self._usuarios: list[Usuario] = []

    # Devuelve todos los usuarios que no tienen baja lógica.
    def listar_activos(self) -> list[Usuario]:
        return [l for l in self._usuarios if not l.eliminado]

    # Busca un usuario activo por su ID.
    def buscar_por_id(self, id_usuario: int) -> Usuario:
        for l in self._usuarios:
            if l.id == id_usuario and not l.eliminado:
                return l
        raise EntidadNoEncontradaError(f"Error: No se encontró un usuario activo con ID {id_usuario}.")

    # Verifica si ya existe otro usuario con el mismo mail (sin distinguir mayúsculas).
    def _existe_mail(self, mail: str, ignorar_id: int | None = None) -> bool:
        mail_normalizado = mail.strip().lower()
        for l in self._usuarios:
            if l.id != ignorar_id and l.mail.strip().lower() == mail_normalizado:
                return True
        return False

    # Valida credenciales de inicio de sesión usando verificar_contrasenia.
    def autenticar(self, mail: str, contrasenia: str) -> Usuario:
        mail_normalizado = mail.strip().lower()
        for l in self._usuarios:
            if l.mail.strip().lower() == mail_normalizado:
                if not l.eliminado and l.verificar_contrasenia(contrasenia):
                    return l
                break
        raise CredencialesInvalidasError("Error: Mail o contraseña incorrectos.")

    # Crea y agrega un nuevo usuario validando que el mail sea único.
    def crear(self, nombre: str, apellido: str, mail: str, celular: str, contrasenia: str, rol: Rol) -> Usuario:
        if self._existe_mail(mail):
            raise DuplicadoError(f"Error: Ya existe un usuario registrado con el mail '{mail.strip()}'.")
        nuevo_usuario = Usuario(nombre, apellido, mail, celular, contrasenia, rol)
        self._usuarios.append(nuevo_usuario)
        return nuevo_usuario

    # Actualiza los datos de un usuario conservando los valores si se pasa None o vacío.
    def editar(self,id_usuario: int, nuevo_nombre: str | None = None, nuevo_apellido: str | None = None, nuevo_mail: str | None = None, nuevo_celular: str | None = None, nueva_contrasenia: str | None = None, nuevo_rol: Rol | None = None) -> Usuario:
        usuario = self.buscar_por_id(id_usuario)

        if nuevo_mail is not None and nuevo_mail.strip():
            if self._existe_mail(nuevo_mail, ignorar_id=usuario.id):
                raise DuplicadoError(f"Error: Ya existe otro usuario registrado con el mail '{nuevo_mail.strip()}'.")
            usuario.mail = nuevo_mail
        if nuevo_nombre is not None and nuevo_nombre.strip():
            usuario.nombre = nuevo_nombre
        if nuevo_apellido is not None and nuevo_apellido.strip():
            usuario.apellido = nuevo_apellido
        if nuevo_celular is not None and nuevo_celular.strip():
            usuario.celular = nuevo_celular
        if nueva_contrasenia is not None and nueva_contrasenia.strip():
            usuario.contrasenia = nueva_contrasenia
        if nuevo_rol is not None:
            usuario.rol = nuevo_rol
        return usuario

    # Realiza la baja lógica impidiendo que el administrador en sesión se elimine a sí mismo.
    def eliminar(self, id_usuario: int, id_usuario_sesion: int) -> None:
        usuario = self.buscar_por_id(id_usuario)
        if usuario.id == id_usuario_sesion:
            raise OperacionNoPermitidaError("Error: Un administrador no puede eliminarse a sí mismo mientras tiene la sesión iniciada.")
        usuario.eliminado = True