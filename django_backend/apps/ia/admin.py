"""
Admin para IA (Conversaciones y Mensajes)
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from lite_thinking_domain.models import Conversacion, Mensaje


# ==========================================
# INLINE PARA MENSAJES
# ==========================================
class MensajeInline(admin.TabularInline):
    """Inline para ver mensajes dentro de conversación"""
    model = Mensaje
    extra = 0
    can_delete = False
    
    fields = ['rol_badge', 'contenido_preview', 'timestamp']
    readonly_fields = ['rol_badge', 'contenido_preview', 'timestamp']
    
    def has_add_permission(self, request, obj=None):
        """No permitir agregar mensajes desde aquí"""
        return False
    
    @admin.display(description='Rol')
    def rol_badge(self, obj):
        """Badge visual para el rol"""
        if obj.rol == 'usuario':
            return format_html(
                '<span style="background: #007bff; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">👤 Usuario</span>'
            )
        return format_html(
            '<span style="background: #28a745; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">🤖 Asistente</span>'
        )
    
    @admin.display(description='Contenido')
    def contenido_preview(self, obj):
        """Preview del contenido limitado a 100 caracteres"""
        if len(obj.contenido) > 100:
            return format_html(
                '<div style="max-width: 500px; white-space: pre-wrap;">{}<em>...</em></div>',
                obj.contenido[:100]
            )
        return format_html(
            '<div style="max-width: 500px; white-space: pre-wrap;">{}</div>',
            obj.contenido
        )
    
    verbose_name = "Mensaje"
    verbose_name_plural = "💬 Historial de Mensajes"


# ==========================================
# ADMIN CONVERSACIÓN
# ==========================================
@admin.register(Conversacion)
class ConversacionAdmin(admin.ModelAdmin):
    """Admin para Conversacion con permisos y visualización mejorada"""
    
    list_display = [
        'id',
        'usuario',
        'titulo_display',
        'total_mensajes_display',
        'ultimo_mensaje_tiempo',
        'estado_badge',
        'created_at'
    ]
    list_filter = ['activa', 'created_at', 'usuario']
    search_fields = ['titulo', 'usuario__username', 'usuario__email']
    readonly_fields = ['created_at', 'updated_at', 'total_mensajes_display', 'ultimo_mensaje_info']
    inlines = [MensajeInline]
    ordering = ['-updated_at']  # Más recientes primero
    
    fieldsets = (
        ('Conversación', {
            'fields': ('usuario', 'titulo', 'activa')
        }),
        ('Estadísticas', {
            'fields': ('total_mensajes_display', 'ultimo_mensaje_info'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_conversaciones', 'desactivar_conversaciones']
    
    # ==========================================
    # MÉTODOS DE AYUDA PARA LIST_DISPLAY
    # ==========================================
    
    @admin.display(description='Título', ordering='titulo')
    def titulo_display(self, obj):
        """Muestra título truncado"""
        if len(obj.titulo) > 50:
            return format_html(
                '<strong>{}</strong><em>...</em>',
                obj.titulo[:50]
            )
        return format_html('<strong>{}</strong>', obj.titulo)
    
    @admin.display(description='Mensajes', ordering='mensaje_count')
    def total_mensajes_display(self, obj):
        """Muestra total de mensajes con badge"""
        count = obj.mensaje_set.count()
        if count == 0:
            return format_html('<span style="color: #999;">0</span>')
        elif count < 5:
            color = '#ffc107'
        elif count < 20:
            color = '#28a745'
        else:
            color = '#007bff'
        
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; '
            'border-radius: 10px; font-size: 11px; font-weight: bold;">{}</span>',
            color, count
        )
    
    @admin.display(description='Último Mensaje')
    def ultimo_mensaje_tiempo(self, obj):
        """Muestra cuándo fue el último mensaje"""
        ultimo = obj.mensaje_set.order_by('-timestamp').first()
        if not ultimo:
            return format_html('<em style="color: #999;">Sin mensajes</em>')
        
        from django.utils import timezone
        ahora = timezone.now()
        diferencia = ahora - ultimo.timestamp
        
        if diferencia.days == 0:
            if diferencia.seconds < 3600:
                minutos = diferencia.seconds // 60
                return format_html('<span style="color: #28a745;">Hace {} min</span>', minutos)
            horas = diferencia.seconds // 3600
            return format_html('<span style="color: #28a745;">Hace {} h</span>', horas)
        elif diferencia.days == 1:
            return format_html('<span style="color: #ffc107;">Ayer</span>')
        elif diferencia.days < 7:
            return format_html('<span style="color: #ffc107;">Hace {} días</span>', diferencia.days)
        else:
            return ultimo.timestamp.strftime('%d/%m/%Y')
    
    @admin.display(description='Estado', ordering='activa')
    def estado_badge(self, obj):
        """Badge visual para estado activo/inactivo"""
        if obj.activa:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">✓ ACTIVA</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">○ ARCHIVADA</span>'
        )
    
    @admin.display(description='Información del Último Mensaje')
    def ultimo_mensaje_info(self, obj):
        """Muestra información detallada del último mensaje"""
        ultimo = obj.mensaje_set.order_by('-timestamp').first()
        if not ultimo:
            return format_html('<em>No hay mensajes en esta conversación</em>')
        
        rol_emoji = '👤' if ultimo.rol == 'usuario' else '🤖'
        preview = ultimo.contenido[:150] + '...' if len(ultimo.contenido) > 150 else ultimo.contenido
        
        return format_html(
            '<div style="border-left: 3px solid #007bff; padding-left: 10px; margin: 5px 0;">'
            '<strong>{} {}</strong><br>'
            '<span style="color: #666; font-size: 12px;">{}</span><br>'
            '<em style="color: #999; font-size: 11px;">{}</em>'
            '</div>',
            rol_emoji,
            'Usuario' if ultimo.rol == 'usuario' else 'Asistente',
            preview,
            ultimo.timestamp.strftime('%d/%m/%Y %H:%M')
        )
    
    # ==========================================
    # OPTIMIZACIÓN DE QUERIES
    # ==========================================
    
    def get_queryset(self, request):
        """Optimizar queries y filtrar por usuario"""
        queryset = super().get_queryset(request)
        
        # Optimizar con count de mensajes
        queryset = queryset.annotate(mensaje_count=Count('mensaje'))
        
        # Filtrar por usuario si no es admin
        if not request.user.is_superuser:
            if hasattr(request.user, 'tipo') and request.user.tipo == 'administrador':
                # Administradores ven todo
                pass
            else:
                # Usuarios normales solo ven sus conversaciones
                queryset = queryset.filter(usuario=request.user)
        
        return queryset
    
    # ==========================================
    # ACCIONES PERSONALIZADAS
    # ==========================================
    
    @admin.action(description='✅ Activar conversaciones seleccionadas')
    def activar_conversaciones(self, request, queryset):
        """Activa múltiples conversaciones"""
        count = queryset.update(activa=True)
        self.message_user(
            request,
            f'✅ {count} conversación(es) activada(s) exitosamente.'
        )
    
    @admin.action(description='📦 Archivar conversaciones seleccionadas')
    def desactivar_conversaciones(self, request, queryset):
        """Desactiva/archiva múltiples conversaciones"""
        count = queryset.update(activa=False)
        self.message_user(
            request,
            f'📦 {count} conversación(es) archivada(s) exitosamente.'
        )
    
    # ==========================================
    # CONTROL DE PERMISOS
    # ==========================================
    
    def has_add_permission(self, request):
        """Todos pueden crear conversaciones"""
        return True
    
    def has_change_permission(self, request, obj=None):
        """Solo puede editar sus propias conversaciones"""
        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'tipo') and request.user.tipo == 'administrador':
            return True
        
        # Usuario normal solo edita sus conversaciones
        if obj and obj.usuario != request.user:
            return False
        
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Solo admin o dueño pueden eliminar"""
        if request.user.is_superuser:
            return True
        
        if hasattr(request.user, 'tipo') and request.user.tipo == 'administrador':
            return True
        
        # Usuario normal solo elimina sus conversaciones
        if obj and obj.usuario != request.user:
            return False
        
        return True
    
    def get_actions(self, request):
        """Usuarios normales tienen acciones limitadas"""
        actions = super().get_actions(request)
        
        # Externos solo pueden archivar sus conversaciones
        if hasattr(request.user, 'tipo') and request.user.tipo == 'externo':
            # Remover eliminar en lote
            actions.pop('delete_selected', None)
        
        return actions
    
    def save_model(self, request, obj, form, change):
        """Auto-asignar usuario si es nueva conversación"""
        if not change and not obj.usuario:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


# ==========================================
# ADMIN MENSAJE (Solo lectura)
# ==========================================
@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    """Admin para Mensaje - Solo lectura"""
    
    list_display = ['id', 'conversacion_link', 'rol_badge', 'contenido_corto', 'timestamp']
    list_filter = ['rol', 'timestamp', 'conversacion__usuario']
    search_fields = ['contenido', 'conversacion__titulo']
    readonly_fields = ['conversacion', 'rol', 'contenido', 'timestamp']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Mensaje', {
            'fields': ('conversacion', 'rol_badge_detail', 'contenido')
        }),
        ('Fecha', {
            'fields': ('timestamp',)
        }),
    )
    
    # ==========================================
    # MÉTODOS DE AYUDA
    # ==========================================
    
    @admin.display(description='Conversación', ordering='conversacion')
    def conversacion_link(self, obj):
        """Link a la conversación"""
        from django.urls import reverse
        url = reverse('admin:lite_thinking_domain_conversacion_change', args=[obj.conversacion.id])
        return format_html(
            '<a href="{}" style="color: #007bff; text-decoration: none;">'
            '💬 {}</a>',
            url, obj.conversacion.titulo[:40]
        )
    
    @admin.display(description='Rol', ordering='rol')
    def rol_badge(self, obj):
        """Badge visual para el rol"""
        if obj.rol == 'usuario':
            return format_html(
                '<span style="background: #007bff; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">👤 Usuario</span>'
            )
        return format_html(
            '<span style="background: #28a745; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">🤖 Asistente</span>'
        )
    
    @admin.display(description='Rol')
    def rol_badge_detail(self, obj):
        """Badge para vista de detalle"""
        return self.rol_badge(obj)
    
    @admin.display(description='Contenido')
    def contenido_corto(self, obj):
        """Contenido truncado para list_display"""
        if len(obj.contenido) > 80:
            return format_html(
                '<div style="max-width: 400px;">{}<em>...</em></div>',
                obj.contenido[:80]
            )
        return format_html('<div style="max-width: 400px;">{}</div>', obj.contenido)
    
    # ==========================================
    # CONTROL DE PERMISOS
    # ==========================================
    
    def has_add_permission(self, request):
        """No se pueden crear mensajes manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Mensajes son inmutables"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo admin puede eliminar mensajes"""
        return request.user.is_superuser
    
    def get_queryset(self, request):
        """Filtrar mensajes según usuario"""
        queryset = super().get_queryset(request)
        
        # Superusuarios ven todo
        if request.user.is_superuser:
            return queryset
        
        # Administradores ven todo
        if hasattr(request.user, 'tipo') and request.user.tipo == 'administrador':
            return queryset
        
        # Usuarios normales solo ven mensajes de sus conversaciones
        return queryset.filter(conversacion__usuario=request.user)