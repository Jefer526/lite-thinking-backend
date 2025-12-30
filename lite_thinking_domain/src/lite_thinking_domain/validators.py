"""
Validadores de Negocio
Funciones de validación reutilizables para reglas de dominio
"""
import re
from typing import Optional
from decimal import Decimal


def validar_nit_colombiano(nit: str) -> bool:
    """
    Valida formato de NIT colombiano
    
    Args:
        nit: Número de Identificación Tributaria
    
    Returns:
        True si el NIT es válido
    
    Raises:
        ValueError: Si el NIT no cumple el formato
    """
    if not nit or len(nit.strip()) == 0:
        raise ValueError("El NIT no puede estar vacío")
    
    nit_limpio = nit.strip().replace("-", "").replace(".", "")
    
    if len(nit_limpio) < 9 or len(nit_limpio) > 15:
        raise ValueError("El NIT debe tener entre 9 y 15 dígitos")
    
    if not nit_limpio.isdigit():
        raise ValueError("El NIT debe contener solo números")
    
    return True


def validar_email(email: str) -> bool:
    """
    Valida formato de email
    
    Args:
        email: Dirección de correo electrónico
    
    Returns:
        True si el email es válido
    
    Raises:
        ValueError: Si el email no es válido
    """
    if not email or '@' not in email:
        raise ValueError("Email inválido")
    
    # Regex básico para email
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patron, email):
        raise ValueError("Formato de email inválido")
    
    return True


def validar_telefono(telefono: str) -> bool:
    """
    Valida formato de teléfono
    
    Args:
        telefono: Número de teléfono
    
    Returns:
        True si el teléfono es válido
    
    Raises:
        ValueError: Si el teléfono no es válido
    """
    if not telefono or len(telefono.strip()) == 0:
        raise ValueError("El teléfono no puede estar vacío")
    
    telefono_limpio = telefono.strip().replace(" ", "").replace("-", "")
    
    if len(telefono_limpio) < 7:
        raise ValueError("El teléfono debe tener al menos 7 dígitos")
    
    if len(telefono_limpio) > 20:
        raise ValueError("El teléfono no puede exceder 20 dígitos")
    
    return True


def validar_precio(precio: Decimal, min_precio: Optional[Decimal] = None, 
                   max_precio: Optional[Decimal] = None) -> bool:
    """
    Valida que un precio esté en el rango válido
    
    Args:
        precio: Precio a validar
        min_precio: Precio mínimo permitido
        max_precio: Precio máximo permitido
    
    Returns:
        True si el precio es válido
    
    Raises:
        ValueError: Si el precio no es válido
    """
    if precio <= 0:
        raise ValueError("El precio debe ser mayor a 0")
    
    if min_precio is not None and precio < min_precio:
        raise ValueError(f"El precio no puede ser menor a {min_precio}")
    
    if max_precio is not None and precio > max_precio:
        raise ValueError(f"El precio no puede ser mayor a {max_precio}")
    
    return True


def validar_cantidad(cantidad: int, permitir_cero: bool = False) -> bool:
    """
    Valida que una cantidad sea válida
    
    Args:
        cantidad: Cantidad a validar
        permitir_cero: Si se permite cantidad 0
    
    Returns:
        True si la cantidad es válida
    
    Raises:
        ValueError: Si la cantidad no es válida
    """
    if cantidad < 0:
        raise ValueError("La cantidad no puede ser negativa")
    
    if not permitir_cero and cantidad == 0:
        raise ValueError("La cantidad debe ser mayor a 0")
    
    return True


def validar_codigo_producto(codigo: str) -> bool:
    """
    Valida formato de código de producto
    
    Args:
        codigo: Código del producto
    
    Returns:
        True si el código es válido
    
    Raises:
        ValueError: Si el código no es válido
    """
    if not codigo or len(codigo.strip()) == 0:
        raise ValueError("El código no puede estar vacío")
    
    if len(codigo) > 50:
        raise ValueError("El código no puede exceder 50 caracteres")
    
    # El código debe empezar con al menos 2 letras
    if len(codigo) < 2 or not codigo[:2].isalpha():
        raise ValueError("El código debe empezar con al menos 2 letras")
    
    return True


def validar_rango_stock(cantidad_actual: int, cantidad_reservada: int) -> bool:
    """
    Valida que la cantidad reservada no exceda la cantidad actual
    
    Args:
        cantidad_actual: Cantidad total en stock
        cantidad_reservada: Cantidad reservada
    
    Returns:
        True si el rango es válido
    
    Raises:
        ValueError: Si el rango no es válido
    """
    if cantidad_actual < 0:
        raise ValueError("La cantidad actual no puede ser negativa")
    
    if cantidad_reservada < 0:
        raise ValueError("La cantidad reservada no puede ser negativa")
    
    if cantidad_reservada > cantidad_actual:
        raise ValueError(
            f"La cantidad reservada ({cantidad_reservada}) no puede ser mayor "
            f"a la cantidad actual ({cantidad_actual})"
        )
    
    return True


def validar_longitud_texto(texto: str, min_length: int = 1, 
                           max_length: Optional[int] = None, 
                           campo: str = "Campo") -> bool:
    """
    Valida la longitud de un texto
    
    Args:
        texto: Texto a validar
        min_length: Longitud mínima
        max_length: Longitud máxima
        campo: Nombre del campo (para el mensaje de error)
    
    Returns:
        True si la longitud es válida
    
    Raises:
        ValueError: Si la longitud no es válida
    """
    if not texto or len(texto.strip()) == 0:
        raise ValueError(f"{campo} no puede estar vacío")
    
    texto_limpio = texto.strip()
    
    if len(texto_limpio) < min_length:
        raise ValueError(f"{campo} debe tener al menos {min_length} caracteres")
    
    if max_length and len(texto_limpio) > max_length:
        raise ValueError(f"{campo} no puede exceder {max_length} caracteres")
    
    return True
