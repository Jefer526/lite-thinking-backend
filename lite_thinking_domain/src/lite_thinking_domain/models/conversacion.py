"""
Modelos Django: Conversacion y Mensaje
Sistema de chatbot conversacional con historial
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings


class Conversacion(models.Model):
    """
    Modelo Django para Conversación del chatbot
    
    Reglas de negocio:
    - Cada usuario puede tener múltiples conversaciones
    - Título generado automáticamente del primer mensaje
    - Se pueden archivar (activa=False)
    - Conversación ordenada por última actualización
    """
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversaciones',
        verbose_name="Usuario"
    )
    
    titulo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Título",
        help_text="Título generado automáticamente del primer mensaje"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    activa = models.BooleanField(
        default=True,
        verbose_name="Conversación Activa"
    )
    
    class Meta:
        verbose_name = "Conversación"
        verbose_name_plural = "Conversaciones"
        ordering = ['-updated_at']
        db_table = 'conversaciones_chatbot'
        indexes = [
            models.Index(fields=['usuario', '-created_at']),
            models.Index(fields=['activa']),
        ]
    
    # ========================================
    # PROPIEDADES DE DOMINIO
    # ========================================
    
    @property
    def total_mensajes(self) -> int:
        """Cuenta el total de mensajes"""
        return self.mensajes.count()
    
    @property
    def total_mensajes_usuario(self) -> int:
        """Cuenta mensajes del usuario"""
        return self.mensajes.filter(rol='user').count()
    
    @property
    def total_mensajes_asistente(self) -> int:
        """Cuenta mensajes del asistente"""
        return self.mensajes.filter(rol='assistant').count()
    
    # ========================================
    # MÉTODOS DE DOMINIO
    # ========================================
    
    def agregar_mensaje_usuario(self, contenido: str) -> 'Mensaje':
        """
        Crea y agrega un mensaje del usuario
        
        Args:
            contenido: Contenido del mensaje
        
        Returns:
            Mensaje creado
        """
        mensaje = Mensaje.objects.create(
            conversacion=self,
            rol='user',
            contenido=contenido
        )
        
        # Generar título automático si no existe
        if not self.titulo:
            self.generar_titulo_automatico()
        
        return mensaje
    
    def agregar_mensaje_asistente(self, contenido: str) -> 'Mensaje':
        """
        Crea y agrega un mensaje del asistente
        
        Args:
            contenido: Contenido del mensaje
        
        Returns:
            Mensaje creado
        """
        return Mensaje.objects.create(
            conversacion=self,
            rol='assistant',
            contenido=contenido
        )
    
    def obtener_historial(self) -> list:
        """
        Obtiene el historial de mensajes en formato para APIs de IA
        
        Returns:
            Lista de diccionarios con rol y contenido
        """
        return [
            {
                "role": msg.rol,
                "content": msg.contenido
            }
            for msg in self.mensajes.all()
        ]
    
    def obtener_ultimo_mensaje(self) -> 'Mensaje':
        """
        Obtiene el último mensaje de la conversación
        
        Returns:
            Último mensaje o None
        """
        return self.mensajes.last()
    
    def generar_titulo_automatico(self) -> None:
        """
        Genera un título automático basado en el primer mensaje del usuario
        """
        primer_mensaje = self.mensajes.filter(rol='user').first()
        if primer_mensaje and not self.titulo:
            # Usar los primeros 50 caracteres del primer mensaje
            self.titulo = primer_mensaje.contenido[:50]
            self.save(update_fields=['titulo'])
    
    def archivar(self) -> None:
        """Archiva la conversación (la marca como inactiva)"""
        self.activa = False
        self.save(update_fields=['activa'])
    
    def reactivar(self) -> None:
        """Reactiva una conversación archivada"""
        self.activa = True
        self.save(update_fields=['activa'])
    
    # ========================================
    # VALIDACIONES
    # ========================================
    
    def clean(self) -> None:
        """Validaciones de modelo"""
        super().clean()
        
        if self.titulo and len(self.titulo) > 200:
            raise ValidationError({
                'titulo': 'El título no puede exceder 200 caracteres'
            })
    
    def __str__(self) -> str:
        return f"{self.usuario.username} - {self.titulo or 'Nueva conversación'}"
    
    def __repr__(self) -> str:
        return (
            f"Conversacion(id={self.id}, usuario_id={self.usuario_id}, "
            f"titulo='{self.titulo}', mensajes={self.total_mensajes}, "
            f"activa={self.activa})"
        )


class Mensaje(models.Model):
    """
    Modelo Django para Mensaje del chatbot
    
    Reglas de negocio:
    - Tipos: user (usuario) o assistant (asistente)
    - Inmutables (no se editan después de creados)
    - Ordenados cronológicamente
    - Máximo 5000 caracteres por mensaje
    """
    
    ROL_CHOICES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
    ]
    
    conversacion = models.ForeignKey(
        Conversacion,
        on_delete=models.CASCADE,
        related_name='mensajes',
        verbose_name="Conversación"
    )
    
    rol = models.CharField(
        max_length=10,
        choices=ROL_CHOICES,
        verbose_name="Rol"
    )
    
    contenido = models.TextField(
        verbose_name="Contenido del Mensaje"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora"
    )
    
    class Meta:
        verbose_name = "Mensaje"
        verbose_name_plural = "Mensajes"
        ordering = ['timestamp']
        db_table = 'mensajes_chatbot'
        indexes = [
            models.Index(fields=['conversacion', 'timestamp']),
            models.Index(fields=['rol']),
        ]
    
    # ========================================
    # PROPIEDADES
    # ========================================
    
    @property
    def es_mensaje_usuario(self) -> bool:
        """Verifica si el mensaje es del usuario"""
        return self.rol == 'user'
    
    @property
    def es_mensaje_asistente(self) -> bool:
        """Verifica si el mensaje es del asistente"""
        return self.rol == 'assistant'
    
    @property
    def contenido_corto(self) -> str:
        """Retorna una versión corta del contenido"""
        if len(self.contenido) > 100:
            return self.contenido[:100] + "..."
        return self.contenido
    
    # ========================================
    # VALIDACIONES
    # ========================================
    
    def clean(self) -> None:
        """Validaciones de modelo"""
        super().clean()
        
        # Validar contenido
        if not self.contenido or len(self.contenido.strip()) == 0:
            raise ValidationError({
                'contenido': 'El contenido del mensaje no puede estar vacío'
            })
        
        if len(self.contenido) > 5000:
            raise ValidationError({
                'contenido': 'El mensaje no puede exceder 5000 caracteres'
            })
    
    def save(self, *args, **kwargs):
        """Override save para validaciones"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.get_rol_display()}: {self.contenido_corto}"
    
    def __repr__(self) -> str:
        return (
            f"Mensaje(id={self.id}, rol='{self.rol}', "
            f"contenido='{self.contenido[:30]}...', timestamp={self.timestamp})"
        )
