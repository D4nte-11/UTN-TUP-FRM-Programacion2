from abc import ABC, abstractmethod
from entidades.usuario import Usuario
from enums.rol import Rol
from servicios.categoria_servicio import CategoriaServicio
from servicios.pedido_servicio import PedidoServicio
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio

# Clase abstracta base para aplicar polimorfismo en los menús según el rol
class Menu(ABC):
    def __init__(self, usuario: Usuario) -> None:
        self._usuario = usuario

    # Devuelve True para cerrar sesión o False para salir del programa
    @abstractmethod
    def mostrar(self) -> bool:
        pass

# Crea y devuelve el menú correspondiente al rol del usuario (único lugar donde se pregunta el rol)
def crear_menu(usuario: Usuario, categoria_servicio: CategoriaServicio, producto_servicio: ProductoServicio, usuario_servicio: UsuarioServicio, pedido_servicio: PedidoServicio) -> Menu:
    # Se importan aquí adentro para evitar importaciones circulares con menu_admin y menu_cliente
    from consola.menu_admin import MenuAdministrador
    from consola.menu_cliente import MenuCliente

    if usuario.rol is Rol.ADMIN:
        return MenuAdministrador(usuario, categoria_servicio, producto_servicio, usuario_servicio, pedido_servicio)
    return MenuCliente(usuario, categoria_servicio, producto_servicio, pedido_servicio)