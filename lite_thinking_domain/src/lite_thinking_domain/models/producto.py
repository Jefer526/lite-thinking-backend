"""
Modelo Django: Producto
Productos con código automático y precios multi-moneda
"""
from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from ..validators import validar_precio, validar_codigo_producto


def generar_codigo_producto(nombre: str) -> str:
    """
    Genera código automático: 2 letras del nombre + número secuencial
    Ejemplo: "Laptop" -> "LA-001", "Mouse" -> "MO-002"
    
    Args:
        nombre: Nombre del producto
    
    Returns:
        Código generado
    """
    # Obtener las 2 primeras letras del nombre (en mayúsculas)
    prefijo = nombre[:2].upper() if len(nombre) >= 2 else nombre.upper()
    
    # Buscar el último código con ese prefijo
    from django.db.models import Max
    from .producto import Producto
    
    ultimo_codigo = Producto.objects.filter(
        codigo__startswith=f"{prefijo}-"
    ).aggregate(Max('codigo'))['codigo__max']
    
    if ultimo_codigo:
        # Extraer el número y sumar 1
        try:
            ultimo_numero = int(ultimo_codigo.split('-')[1])
            nuevo_numero = ultimo_numero + 1
        except (IndexError, ValueError):
            nuevo_numero = 1
    else:
        nuevo_numero = 1
    
    # Generar código con formato: XX-NNN
    return f"{prefijo}-{nuevo_numero:03d}"


class Producto(models.Model):
    """
    Modelo Django para Producto
    
    Reglas de negocio:
    - Código único generado automáticamente si está vacío
    - Precios en USD con conversión automática a COP y EUR
    - Tipos: Físico, Digital, Servicio
    - Stock mínimo para alertas de reabastecimiento
    """
    
    TIPO_CHOICES = [
        ('fisico', 'Físico'),
        ('digital', 'Digital'),
        ('servicio', 'Servicio'),
    ]
    
    # Relación con Empresa
    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.PROTECT,
        related_name='productos',
        verbose_name="Empresa",
        help_text="Empresa a la que pertenece el producto"
    )
    
    codigo = models.CharField(
        max_length=50,
        unique=True,
        blank=True,  # Permitir vacío para generación automática
        verbose_name="Código",
        help_text="Código único del producto (se genera automáticamente si está vacío)"
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        help_text="Nombre descriptivo del producto"
    )
    
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción detallada del producto"
    )
    
    precio_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Precio USD",
        help_text="Precio del producto en dólares estadounidenses"
    )
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='fisico',
        verbose_name="Tipo de Producto"
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
        help_text="Indica si el producto está activo para venta"
    )
    
    stock_minimo = models.IntegerField(
        default=0,
        verbose_name="Stock Mínimo",
        help_text="Cantidad mínima de stock antes de reabastecimiento"
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-created_at']
        db_table = 'productos'
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
            models.Index(fields=['empresa', 'activo']),
            models.Index(fields=['tipo']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(precio_usd__gt=0),
                name='precio_usd_positivo'
            ),
            models.CheckConstraint(
                check=models.Q(stock_minimo__gte=0),
                name='stock_minimo_no_negativo'
            ),
        ]
    
    # ========================================
    # MÉTODOS DE DOMINIO - PRECIOS
    # ========================================
    
    def calcular_precio_cop(self, tasa_cambio: Decimal = Decimal('4000')) -> Decimal:
        """
        Calcula el precio en pesos colombianos
        
        Args:
            tasa_cambio: Tasa de cambio USD a COP (default: 4000)
        
        Returns:
            Precio en COP
        """
        if tasa_cambio <= 0:
            raise ValueError("La tasa de cambio debe ser mayor a 0")
        return self.precio_usd * tasa_cambio
    
    def calcular_precio_eur(self, tasa_cambio_usd_eur: Decimal = Decimal('0.92')) -> Decimal:
        """
        Calcula el precio en euros
        
        Args:
            tasa_cambio_usd_eur: Tasa de cambio USD a EUR (default: 0.92)
        
        Returns:
            Precio en EUR
        """
        if tasa_cambio_usd_eur <= 0:
            raise ValueError("La tasa de cambio debe ser mayor a 0")
        return self.precio_usd * tasa_cambio_usd_eur
    
    def actualizar_precio(self, nuevo_precio_usd: Decimal) -> None:
        """
        Actualiza el precio del producto
        
        Args:
            nuevo_precio_usd: Nuevo precio en USD
        """
        validar_precio(nuevo_precio_usd)
        self.precio_usd = nuevo_precio_usd
        self.save(update_fields=['precio_usd', 'updated_at'])
    
    # ========================================
    # MÉTODOS DE DOMINIO - ESTADO
    # ========================================
    
    def activar(self) -> None:
        """Activa el producto"""
        self.activo = True
        self.save(update_fields=['activo', 'updated_at'])
    
    def desactivar(self) -> None:
        """Desactiva el producto"""
        self.activo = False
        self.save(update_fields=['activo', 'updated_at'])
    
    def requiere_reabastecimiento(self, stock_actual: int) -> bool:
        """
        Verifica si el producto requiere reabastecimiento
        
        Args:
            stock_actual: Cantidad actual en inventario
        
        Returns:
            True si requiere reabastecimiento
        """
        return stock_actual <= self.stock_minimo
    
    # ========================================
    # PROPIEDADES
    # ========================================
    
    @property
    def es_fisico(self) -> bool:
        """Verifica si es un producto físico"""
        return self.tipo == 'fisico'
    
    @property
    def es_digital(self) -> bool:
        """Verifica si es un producto digital"""
        return self.tipo == 'digital'
    
    @property
    def es_servicio(self) -> bool:
        """Verifica si es un servicio"""
        return self.tipo == 'servicio'
    
    # ========================================
    # VALIDACIONES
    # ========================================
    
    def clean(self) -> None:
        """Validaciones de modelo"""
        super().clean()
        
        # Validar código si está presente
        if self.codigo:
            try:
                validar_codigo_producto(self.codigo)
            except ValueError as e:
                raise ValidationError({'codigo': str(e)})
        
        # Validar nombre
        if not self.nombre or len(self.nombre.strip()) == 0:
            raise ValidationError({'nombre': 'El nombre es obligatorio'})
        
        if len(self.nombre) > 200:
            raise ValidationError({'nombre': 'El nombre no puede exceder 200 caracteres'})
        
        # Validar descripción
        if not self.descripcion or len(self.descripcion.strip()) == 0:
            raise ValidationError({'descripcion': 'La descripción es obligatoria'})
        
        # Validar precio
        try:
            validar_precio(self.precio_usd, max_precio=Decimal('999999999.99'))
        except ValueError as e:
            raise ValidationError({'precio_usd': str(e)})
        
        # Validar stock mínimo
        if self.stock_minimo < 0:
            raise ValidationError({'stock_minimo': 'El stock mínimo no puede ser negativo'})
    
    def save(self, *args, **kwargs):
        """Override save para generación automática de código y validaciones"""
        # 1. Generar código automático si está vacío
        if not self.codigo:
            self.codigo = generar_codigo_producto(self.nombre)
        
        # 2. Limpiar y formatear datos
        self.codigo = self.codigo.strip().upper()
        self.nombre = self.nombre.strip()
        
        # 3. Validar
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.codigo} - {self.nombre}"
    
    def __repr__(self) -> str:
        return (
            f"Producto(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}', "
            f"precio_usd={self.precio_usd}, activo={self.activo})"
        )
