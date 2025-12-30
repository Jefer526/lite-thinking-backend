"""
Modelo Django: Usuario
Extiende AbstractUser de Django con tipos Administrador/Externo
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class Usuario(AbstractUser):
    """
    Modelo Django para Usuario
    Extiende AbstractUser agregando:
    - Tipo de usuario (Administrador/Externo)
    - Estado activo
    - Fecha de último acceso
    
    Reglas de negocio:
    - Administrador: Acceso completo (CRUD)
    - Externo: Solo lectura
    """
    
    TIPO_CHOICES = [
        ('administrador', 'Administrador'),
        ('externo', 'Externo'),
    ]
    
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='administrador',
        verbose_name="Tipo de Usuario",
        help_text="Administrador: acceso completo | Externo: solo visualización"
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Usuario Activo",
        help_text="Indica si el usuario puede acceder al sistema"
    )
    
    fecha_ultimo_acceso = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último Acceso"
    )
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = 'usuarios'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['email']),
            models.Index(fields=['activo']),
        ]
        # Constraint para asegurar email único si no está vacío
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                name='unique_email',
                condition=models.Q(email__gt='')
            )
        ]
    
    # ========================================
    # PROPIEDADES DE DOMINIO
    # ========================================
    
    @property
    def nombre_completo(self) -> str:
        """Retorna nombre completo del usuario"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def es_administrador(self) -> bool:
        """Verifica si es administrador"""
        return self.tipo == 'administrador'
    
    @property
    def es_externo(self) -> bool:
        """Verifica si es externo"""
        return self.tipo == 'externo'
    
    # ========================================
    # MÉTODOS DE DOMINIO
    # ========================================
    
    def activar(self) -> None:
        """Activa el usuario"""
        self.activo = True
        self.save(update_fields=['activo'])
    
    def desactivar(self) -> None:
        """Desactiva el usuario"""
        self.activo = False
        self.save(update_fields=['activo'])
    
    def registrar_acceso(self) -> None:
        """Registra el último acceso del usuario"""
        from django.utils import timezone
        self.fecha_ultimo_acceso = timezone.now()
        self.save(update_fields=['fecha_ultimo_acceso'])
    
    def puede_gestionar_empresa(self, empresa_id: int) -> bool:
        """
        Verifica si el usuario puede gestionar una empresa específica
        
        Args:
            empresa_id: ID de la empresa
        
        Returns:
            True si puede gestionar
        """
        # Administradores pueden gestionar cualquier empresa
        return self.es_administrador
    
    def tiene_permiso_crud(self) -> bool:
        """
        Verifica si el usuario tiene permisos de escritura
        
        Returns:
            True si puede crear/actualizar/eliminar
        """
        return self.es_administrador and self.activo
    
    def tiene_permiso_lectura(self) -> bool:
        """
        Verifica si el usuario tiene permisos de lectura
        
        Returns:
            True si puede leer
        """
        return self.activo
    
    # ========================================
    # VALIDACIONES
    # ========================================
    
    def clean(self) -> None:
        """Validaciones de modelo"""
        super().clean()
        
        # Validar email si está presente
        if self.email and '@' not in self.email:
            raise ValidationError({
                'email': 'Email inválido'
            })
        
        # Validar que username no esté vacío
        if not self.username or len(self.username.strip()) == 0:
            raise ValidationError({
                'username': 'El username es obligatorio'
            })
    
    def save(self, *args, **kwargs):
        """Override save para validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.username} ({self.get_tipo_display()})"
    
    def __repr__(self) -> str:
        return (
            f"Usuario(id={self.id}, username='{self.username}', "
            f"email='{self.email}', tipo='{self.tipo}', activo={self.activo})"
        )
