from entidades.categoria import Categoria
from excepciones.errores import (DuplicadoError, EntidadNoEncontradaError, OperacionNoPermitidaError)

class CategoriaServicio():
    def __init__(self) -> None:
        self._categorias: list[Categoria] = []
    
    def listar_activas(self) -> list[Categoria]:
        #Devuelve todas las categorías que no tieen baja lógica.
        return [cat for cat in self._categorias if not cat.eliminado]

    def buscar_por_id(self, id_categoria: int) -> Categoria:
        #Busca una categoría actoiva por su ID; lanza error si no existe o está eliminada.
        for cat in self._categorias:
            if cat.id == id_categoria and not cat.eliminado:
                return cat
        raise EntidadNoEncontradaError(f"Error: No se encontró una categoría activa con ID {id_categoria}.")

    def _existe_nombre(self, nombre: str, ignorar_id: int | None = None) -> bool:
        #Verifica si ya existe otra categoría activa con el mismo nombre (sin distinguir mayúsculas).
        nombre_normalizado = nombre.strip().lower()
        for cat in self._categorias:
            if not cat.eliminado and cat.id != ignorar_id:
                if cat.nombre.strip().lower() == nombre_normalizado:
                    return True
        return False

    def crear(self, nombre: str, descripcion: str) -> Categoria:
        #Crea y agrega una nueva categoría validando que el nombre no esté repetido.
        if self._existe_nombre(nombre):
            raise DuplicadoError(f"Error: Ya existe una categoría activa con el nombre '{nombre.strip()}.")
        
        #Al instanciar Categoria, sus setters validan que nombre y descripción no estén vacíos
        nueva_categoria = Categoria(nombre, descripcion)
        self._categorias.append(nueva_categoria)
        return nueva_categoria
    
    def editar(self, id_categoria: int, nuevo_nombre: str | None = None, nueva_descripcion: str | None = None) -> Categoria:
        #Actualiza nombre y/o descripción conservando los valores si se pasa None o vacío (HU-CAT-03).
        categoria = self.buscar_por_id(id_categoria)
        if nuevo_nombre is not None and nuevo_nombre.strip():
            if self._existe_nombre(nuevo_nombre, ignorar_id=categoria.id):
                raise DuplicadoError(f"Error: Ya existe otra categoría activa con el nombre '{nuevo_nombre.strip()}'.")
            categoria.nombre = nuevo_nombre
        if nueva_descripcion is not None and nueva_descripcion.strip():
            categoria.descripcion = nueva_descripcion
        return categoria

    def eliminar(self, id_categoria: int, cantidad_productos_activos: int = 0) -> None:
        #Realiza la baja lógica si la categoría no tiene productos activos asociados.
        categoria = self.buscar_por_id(id_categoria)
        if cantidad_productos_activos > 0:
            raise OperacionNoPermitidaError(f"Error: No se puede eliminar la categoría '{categoria.nombre}' porque tiene {cantidad_productos_activos} producto(s) activo(s) asociado(s).")
        categoria.eliminado = True