"""
Modelos Django: Inventario y MovimientoInventario
Sistema completo de gestión de inventario con movimientos
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from decimal import Decimal
from ..validators import validar_cantidad, validar_rango_stock


class Inventario(models.Model):
    """
    Modelo Django para Inventario
    
    Reglas de negocio:
    - Relación OneToOne con Producto
    - Cantidad actual nunca negativa
    - Sistema de reservas (cantidad_reservada)
    - Cantidad disponible = actual - reservada
    - Ubicación física en bodega
    """
    
    producto = models.OneToOneField(
        'Producto',
        on_delete=models.PROTECT,
        related_name='inventario',
        verbose_name="Producto"
    )
    
    cantidad_actual = models.IntegerField(
        default=0,
        verbose_name="Cantidad en Stock",
        help_text="Cantidad total en inventario"
    )
    
    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Ubicación",
        help_text="Ubicación física en bodega (Ej: A-12-3)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"
        ordering = ['-created_at']
        db_table = 'inventarios'
        indexes = [
            models.Index(fields=['producto']),
            models.Index(fields=['cantidad_actual']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(cantidad_actual__gte=0),
                name='cantidad_actual_no_negativa'
            ),
        ]
    
    # ========================================
    # PROPIEDADES DE DOMINIO
    # ========================================
    
    @property
    def requiere_reabastecimiento(self) -> bool:
        """Verifica si requiere reabastecimiento"""
        return self.cantidad_actual <= self.producto.stock_minimo
    
    @property
    def estado_stock(self) -> str:
        """Retorna el estado del stock"""
        if self.cantidad_actual <= 0:
            return "SIN STOCK"
        elif self.requiere_reabastecimiento:
            return "BAJO"
        else:
            return "OK"
    
    # ========================================
    # MÉTODOS DE DOMINIO
    # ========================================
    
    def registrar_entrada(
        self,
        cantidad: int,
        motivo: str,
        usuario
    ) -> 'MovimientoInventario':
        """
        Registra una entrada de inventario
        
        Args:
            cantidad: Cantidad a ingresar
            motivo: Motivo del ingreso
            usuario: Usuario que registra
        
        Returns:
            MovimientoInventario creado
        """
        validar_cantidad(cantidad)
        
        movimiento = MovimientoInventario.objects.create(
            inventario=self,
            tipo='entrada',
            cantidad=cantidad,
            motivo=motivo,
            usuario=usuario
        )
        
        self.cantidad_actual += cantidad
        self.save(update_fields=['cantidad_actual', 'updated_at'])
        
        return movimiento
    
    def registrar_salida(
        self,
        cantidad: int,
        motivo: str,
        usuario
    ) -> 'MovimientoInventario':
        """
        Registra una salida de inventario
        
        Args:
            cantidad: Cantidad a retirar
            motivo: Motivo de la salida
            usuario: Usuario que registra
        
        Returns:
            MovimientoInventario creado
        
        Raises:
            ValidationError: Si no hay suficiente inventario
        """
        validar_cantidad(cantidad)
        
        if cantidad > self.cantidad_actual:
            raise ValidationError(
                f"No hay suficiente inventario disponible. "
                f"Disponible: {self.cantidad_actual}, Solicitado: {cantidad}"
            )
        
        movimiento = MovimientoInventario.objects.create(
            inventario=self,
            tipo='salida',
            cantidad=cantidad,
            motivo=motivo,
            usuario=usuario
        )
        
        self.cantidad_actual -= cantidad
        self.save(update_fields=['cantidad_actual', 'updated_at'])
        
        return movimiento
    
    def ajustar_inventario(
        self,
        nueva_cantidad: int,
        motivo: str,
        usuario
    ) -> 'MovimientoInventario':
        """
        Ajusta el inventario a una cantidad específica
        
        Args:
            nueva_cantidad: Nueva cantidad total
            motivo: Motivo del ajuste
            usuario: Usuario que registra
        
        Returns:
            MovimientoInventario creado
        """
        if nueva_cantidad < 0:
            raise ValidationError("La nueva cantidad no puede ser negativa")
        
        diferencia = nueva_cantidad - self.cantidad_actual
        
        movimiento = MovimientoInventario.objects.create(
            inventario=self,
            tipo='entrada' if diferencia > 0 else 'salida',
            cantidad=abs(diferencia),
            motivo=f"Ajuste: {motivo} (de {self.cantidad_actual} a {nueva_cantidad})",
            usuario=usuario
        )
        
        self.cantidad_actual = nueva_cantidad
        self.save(update_fields=['cantidad_actual', 'updated_at'])
        
        return movimiento
    
    # ========================================
    # VALIDACIONES
    # ========================================
    
    def clean(self) -> None:
        """Validaciones de modelo"""
        super().clean()
        
        if self.cantidad_actual < 0:
            raise ValidationError({
                'cantidad_actual': 'La cantidad actual no puede ser negativa'
            })
    
    def save(self, *args, **kwargs):
        """Override save para validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"Inventario: {self.producto.codigo} - Stock: {self.cantidad_actual}"
    
    def __repr__(self) -> str:
        return (
            f"Inventario(id={self.id}, producto_id={self.producto_id}, "
            f"cantidad_actual={self.cantidad_actual})"
        )


class MovimientoInventario(models.Model):
    """
    Modelo Django para MovimientoInventario
    
    Reglas de negocio:
    - Tipos: ENTRADA (aumenta) o SALIDA (disminuye)
    - Inmutables (no se pueden editar ni eliminar)
    - Registran usuario responsable
    - Auditoría completa con fecha
    """
    
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
    ]
    
    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.PROTECT,
        related_name='movimientos',
        verbose_name="Inventario"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name="Tipo de Movimiento"
    )
    
    cantidad = models.IntegerField(
        verbose_name="Cantidad"
    )
    
    motivo = models.TextField(
        blank=True,
        verbose_name="Motivo"
    )
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )
    
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del Movimiento"
    )
    
    class Meta:
        verbose_name = "Movimiento de Inventario"
        verbose_name_plural = "Movimientos de Inventario"
        ordering = ['-fecha']
        db_table = 'movimientos_inventario'
        indexes = [
            models.Index(fields=['inventario', '-fecha']),
            models.Index(fields=['tipo']),
            models.Index(fields=['fecha']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(cantidad__gt=0),
                name='cantidad_movimiento_positiva'
            ),
        ]
    
    # ========================================
    # PROPIEDADES
    # ========================================
    
    @property
    def es_entrada(self) -> bool:
        """Verifica si es una entrada"""
        return self.tipo == 'entrada'
    
    @property
    def es_salida(self) -> bool:
        """Verifica si es una salida"""
        return self.tipo == 'salida'
    
    # ========================================
    # VALIDACIONES
    # ========================================
    
    def clean(self) -> None:
        """Validaciones de modelo"""
        super().clean()
        
        # Validar cantidad
        try:
            validar_cantidad(self.cantidad)
        except ValueError as e:
            raise ValidationError({'cantidad': str(e)})
        
        # Validar motivo
        if not self.motivo or len(self.motivo.strip()) == 0:
            raise ValidationError({'motivo': 'El motivo es obligatorio'})
    
    def save(self, *args, **kwargs):
        """Override save para validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.get_tipo_display()} - {self.cantidad} - {self.inventario.producto.codigo}"
    
    def __repr__(self) -> str:
        return (
            f"MovimientoInventario(id={self.id}, tipo='{self.tipo}', "
            f"cantidad={self.cantidad}, fecha={self.fecha})"
        )
