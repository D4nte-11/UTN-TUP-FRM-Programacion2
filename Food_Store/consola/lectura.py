from enum import Enum

# Lee un texto por consola; si permitir_vacio es True y se presiona Enter, devuelve None
def leer_texto(mensaje: str, permitir_vacio: bool = False) -> str | None:
    while True:
        valor = input(mensaje).strip()
        if not valor:
            if permitir_vacio:
                return None
            print("Error: El campo no puede estar vacío.")
            continue
        return valor

# Lee un número entero validando formato y rango opcional
def leer_entero(mensaje: str, minimo: int | None = None, maximo: int | None = None, permitir_vacio: bool = False) -> int | None:
    while True:
        texto = input(mensaje).strip()
        if not texto:
            if permitir_vacio:
                return None
            print("Error: Debe ingresar un número entero.")
            continue
        try:
            numero = int(texto)
        except ValueError:
            print("Error: Debe ingresar un número entero válido.")
            continue

        if minimo is not None and numero < minimo:
            print(f"Error: El valor debe ser mayor o igual a {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            print(f"Error: El valor debe ser menor o igual a {maximo}.")
            continue
        return numero

# Lee un número decimal (float) validando formato y mínimo opcional
def leer_flotante(mensaje: str, minimo: float | None = None, permitir_vacio: bool = False) -> float | None:
    while True:
        texto = input(mensaje).strip().replace(",", ".")
        if not texto:
            if permitir_vacio:
                return None
            print("Error: Debe ingresar un número.")
            continue
        try:
            numero = float(texto)
        except ValueError:
            print("Error: Debe ingresar un número válido.")
            continue

        if minimo is not None and numero < minimo:
            print(f"Error: El valor debe ser mayor o igual a {minimo}.")
            continue
        return numero

# Lee una confirmación S/N y devuelve True o False
def leer_confirmacion(mensaje: str, permitir_vacio: bool = False) -> bool | None:
    while True:
        texto = input(f"{mensaje} (S/N): ").strip().upper()
        if not texto and permitir_vacio:
            return None
        if texto == "S":
            return True
        if texto == "N":
            return False
        print("Error: Responda con 'S' o 'N'.")


# Muestra las opciones de un Enum numeradas y devuelve el miembro elegido
def leer_enum(mensaje: str, enum_clase: type[Enum], permitir_vacio: bool = False) -> Enum | None:
    opciones = list(enum_clase)
    print(mensaje)
    for i, l in enumerate(opciones, start=1):
        print(f"  {i}. {l.value}")

    while True:
        texto = input("Seleccione una opción por número: ").strip()
        if not texto:
            if permitir_vacio:
                return None
            print("Error: Debe elegir una opción.")
            continue
        try:
            indice = int(texto)
        except ValueError:
            print("Error: Debe ingresar un número válido.")
            continue

        if 1 <= indice <= len(opciones):
            return opciones[indice - 1]
        print(f"Error: Opción fuera de rango (1 a {len(opciones)}).")

# Lee una opción de menú validando que esté dentro del conjunto permitido
def leer_opcion_menu(opciones_validas: set[int]) -> int:
    while True:
        texto = input("Seleccione: ").strip()
        try:
            opcion = int(texto)
        except ValueError:
            print("Error: Debe ingresar un número de opción válido.")
            continue
        if opcion in opciones_validas:
            return opcion
        print("Error: Opción fuera de rango.")