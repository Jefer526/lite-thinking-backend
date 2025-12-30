"""
Excepciones de Negocio del Dominio
Excepciones específicas para reglas de negocio
"""


class DomainException(Exception):
    """Excepción base para todas las excepciones de dominio"""
    pass


# ========================================
# EXCEPCIONES DE EMPRESA
# ========================================

class EmpresaException(DomainException):
    """Excepción base para errores relacionados con Empresa"""
    pass


class NITInvalidoException(EmpresaException):
    """El NIT proporcionado es inválido"""
    pass


class EmpresaDuplicadaException(EmpresaException):
    """Ya existe una empresa con ese NIT"""
    pass


# ========================================
# EXCEPCIONES DE PRODUCTO
# ========================================

class ProductoException(DomainException):
    """Excepción base para errores relacionados con Producto"""
    pass


class CodigoProductoDuplicadoException(ProductoException):
    """Ya existe un producto con ese código"""
    pass


class PrecioInvalidoException(ProductoException):
    """El precio proporcionado es inválido"""
    pass


class TipoProductoInvalidoException(ProductoException):
    """El tipo de producto no es válido"""
    pass


# ========================================
# EXCEPCIONES DE INVENTARIO
# ========================================

class InventarioException(DomainException):
    """Excepción base para errores relacionados con Inventario"""
    pass


class StockInsuficienteException(InventarioException):
    """No hay suficiente stock disponible"""
    pass


class CantidadInvalidaException(InventarioException):
    """La cantidad proporcionada es inválida"""
    pass


class ReservaInvalidaException(InventarioException):
    """Error en la operación de reserva"""
    pass


class MovimientoInventarioException(InventarioException):
    """Error al registrar movimiento de inventario"""
    pass


# ========================================
# EXCEPCIONES DE USUARIO
# ========================================

class UsuarioException(DomainException):
    """Excepción base para errores relacionados con Usuario"""
    pass


class CredencialesInvalidasException(UsuarioException):
    """Las credenciales proporcionadas son inválidas"""
    pass


class UsuarioInactivoException(UsuarioException):
    """El usuario está inactivo"""
    pass


class PermisosDenegadosException(UsuarioException):
    """El usuario no tiene permisos suficientes"""
    pass


# ========================================
# EXCEPCIONES DE CONVERSACIÓN (IA)
# ========================================

class ConversacionException(DomainException):
    """Excepción base para errores relacionados con Conversación"""
    pass


class MensajeInvalidoException(ConversacionException):
    """El mensaje proporcionado es inválido"""
    pass


class ConversacionInactivaException(ConversacionException):
    """La conversación está archivada/inactiva"""
    pass
