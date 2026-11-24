from entidades.categoria import Categoria
from entidades.producto import Producto
from excepciones.errores import DatoInvalidoError, EntidadNoEncontradaError

class ProductoServicio:
    def __init__(self) -> None:
        self._productos: list[Producto] = []

    def crear(self, nombre: str, precio: float, descripcion: str, stock: int, imagen: str, disponible: bool, categoria: Categoria) -> Producto:
        if categoria is None or categoria.eliminado:
            raise DatoInvalidoError("Error: Debe elegir una categoria valida")

        producto = Producto(nombre=nombre, precio=precio, descripcion=descripcion, stock=stock, imagen=imagen, disponible=disponible, categoria=categoria)
        self._productos.append(producto)
        return producto

    def buscar_por_id(self, id_producto: int) -> Producto:
        for producto in self._productos:
            if producto.id == id_producto and not producto.eliminado:
                return producto
        raise EntidadNoEncontradaError("Error: No se encontró el producto con esa id")

    def listar_activos(self) -> list[Producto]:
        return [l for l in self._productos if not l.eliminado]

    def listar_disponibles(self) -> list[Producto]:
        return [l for l in self._productos if not l.eliminado and l.disponible and l.stock > 0]

    def listar_por_categoria(self, id_categoria: int, solo_disponibles: bool = False) -> list[Producto]:
        base = self.listar_disponibles() if solo_disponibles else self.listar_activos()
        return [l for l in base if l.categoria.id == id_categoria]

    def contar_activos_por_categoria(self, id_categoria: int) -> int:
        return sum(1 for l in self._productos if not l.eliminado and l.categoria.id == id_categoria)

    def editar(self,id_producto: int, nombre: str | None = None, precio: float | None = None, descripcion: str | None = None, stock: int | None = None, imagen: str | None = None, disponible: bool | None = None, categoria: Categoria | None = None) -> Producto:
        producto = self.buscar_por_id(id_producto)
        if categoria is not None:
            if categoria.eliminado:
                raise DatoInvalidoError("Error: No se puede asignar una categoría eliminada.")
            producto.categoria = categoria
        if nombre is not None:
            producto.nombre = nombre
        if precio is not None:
            producto.precio = precio
        if descripcion is not None:
            producto.descripcion = descripcion
        if stock is not None:
            producto.stock = stock
        if imagen is not None:
            producto.imagen = imagen
        if disponible is not None:
            producto.disponible = disponible

        return producto

    def eliminar(self, id_producto: int) -> None:
        producto = self.buscar_por_id(id_producto)
        producto.eliminado = True