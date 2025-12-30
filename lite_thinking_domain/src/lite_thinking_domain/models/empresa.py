"""
Modelo Django: Empresa
Gestión de empresas con validación de NIT colombiano
"""
from django.db import models
from django.core.exceptions import ValidationError
from ..validators import validar_nit_colombiano, validar_email, validar_telefono


class Empresa(models.Model):
    """
    Modelo Django para Empresa
    
    Reglas de negocio:
    - NIT único de 9-15 dígitos
    - Email válido y único
    - Teléfono de al menos 7 dígitos
    - Soft delete (desactivar en lugar de eliminar)
    """
    
    nit = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="NIT",
        help_text="Número de Identificación Tributaria (9-15 dígitos)"
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre",
        help_text="Razón social de la empresa"
    )
    
    direccion = models.TextField(
        verbose_name="Dirección",
        help_text="Dirección física de la empresa"
    )
    
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono",
        help_text="Número de contacto principal"
    )
    
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Correo electrónico de contacto"
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa",
        help_text="Indica si la empresa está activa en el sistema"
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
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['-created_at']
        db_table = 'empresas'
        indexes = [
            models.Index(fields=['nit']),
            models.Index(fields=['nombre']),
            models.Index(fields=['activa']),
            models.Index(fields=['email']),
        ]
    
    # ========================================
    # MÉTODOS DE DOMINIO
    # ========================================
    
    def activar(self) -> None:
        """Activa la empresa"""
        self.activa = True
        self.save(update_fields=['activa', 'updated_at'])
    
    def desactivar(self) -> None:
        """Desactiva la empresa (soft delete)"""
        self.activa = False
        self.save(update_fields=['activa', 'updated_at'])
    
    def actualizar_informacion(
        self,
        nombre: str = None,
        direccion: str = None,
        telefono: str = None,
        email: str = None
    ) -> None:
        """
        Actualiza la información de la empresa
        Solo actualiza los campos proporcionados
        
        Args:
            nombre: Nuevo nombre (opcional)
            direccion: Nueva dirección (opcional)
            telefono: Nuevo teléfono (opcional)
            email: Nuevo email (opcional)
        """
        campos_actualizados = []
        
        if nombre is not None:
            self.nombre = nombre
            campos_actualizados.append('nombre')
        
        if direccion is not None:
            self.direccion = direccion
            campos_actualizados.append('direccion')
        
        if telefono is not None:
            self.telefono = telefono
            campos_actualizados.append('telefono')
        
        if email is not None:
            self.email = email
            campos_actualizados.append('email')
        
        if campos_actualizados:
            campos_actualizados.append('updated_at')
            self.full_clean()
            self.save(update_fields=campos_actualizados)
    
    def tiene_productos(self) -> bool:
        """
        Verifica si la empresa tiene productos asociados
        
        Returns:
            True si tiene productos
        """
        return self.productos.exists()
    
    def contar_productos(self) -> int:
        """
        Cuenta la cantidad de productos de la empresa
        
        Returns:
            Cantidad de productos
        """
        return self.productos.count()
    
    def productos_activos(self):
        """
        Retorna los productos activos de la empresa
        
        Returns:
            QuerySet de productos activos
        """
        return self.productos.filter(activo=True)
    
    # ========================================
    # VALIDACIONES
    # ========================================
    
    def clean(self) -> None:
        """Validaciones de modelo usando validators del dominio"""
        super().clean()
        
        # Validar NIT
        try:
            validar_nit_colombiano(self.nit)
        except ValueError as e:
            raise ValidationError({'nit': str(e)})
        
        # Validar email
        try:
            validar_email(self.email)
        except ValueError as e:
            raise ValidationError({'email': str(e)})
        
        # Validar teléfono
        try:
            validar_telefono(self.telefono)
        except ValueError as e:
            raise ValidationError({'telefono': str(e)})
        
        # Validar nombre
        if not self.nombre or len(self.nombre.strip()) == 0:
            raise ValidationError({'nombre': 'El nombre es obligatorio'})
        
        if len(self.nombre) > 200:
            raise ValidationError({'nombre': 'El nombre no puede exceder 200 caracteres'})
        
        # Validar dirección
        if not self.direccion or len(self.direccion.strip()) == 0:
            raise ValidationError({'direccion': 'La dirección es obligatoria'})
    
    def save(self, *args, **kwargs):
        """Override save para validaciones"""
        # Limpiar y formatear datos
        self.nit = self.nit.strip()
        self.nombre = self.nombre.strip()
        self.email = self.email.lower().strip()
        self.telefono = self.telefono.strip()
        
        # Validar
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.nit} - {self.nombre}"
    
    def __repr__(self) -> str:
        return (
            f"Empresa(id={self.id}, nit='{self.nit}', nombre='{self.nombre}', "
            f"activa={self.activa})"
        )
