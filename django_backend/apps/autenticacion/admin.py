"""
Admin para Usuarios
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from lite_thinking_domain.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """Admin personalizado para Usuario con permisos y acciones"""
    
    list_display = [
        'username',
        'nombre_completo_display',
        'email',
        'tipo_badge',
        'estado_badge',
        'ultimo_acceso_display',
        'date_joined'
    ]
    list_filter = [
        'tipo',
        'activo',
        'is_staff',
        'is_superuser',
        'date_joined',
        'fecha_ultimo_acceso'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    # Fieldsets para edición
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Información Adicional', {
            'fields': ('tipo', 'activo', 'fecha_ultimo_acceso')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets para creación
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name'),
        }),
        ('Tipo de Usuario', {
            'fields': ('tipo',),
            'description': 'Administrador: acceso completo. Externo: solo lectura.'
        }),
    )
    
    readonly_fields = ['fecha_ultimo_acceso', 'last_login', 'date_joined']
    
    actions = [
        'activar_usuarios',
        'desactivar_usuarios',
        'marcar_como_administrador',
        'marcar_como_externo'
    ]
    
    # ==========================================
    # MÉTODOS DE AYUDA PARA LIST_DISPLAY
    # ==========================================
    
    @admin.display(description='Nombre Completo', ordering='first_name')
    def nombre_completo_display(self, obj):
        """Muestra nombre completo o username si está vacío"""
        nombre = obj.get_full_name()
        if nombre.strip():
            return nombre
        return format_html('<em style="color: #999;">{}</em>', obj.username)
    
    @admin.display(description='Tipo', ordering='tipo')
    def tipo_badge(self, obj):
        """Badge visual para el tipo de usuario"""
        if obj.tipo == 'administrador':
            return format_html(
                '<span style="background: #007bff; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">👑 ADMIN</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">👤 EXTERNO</span>'
        )
    
    @admin.display(description='Estado', ordering='activo')
    def estado_badge(self, obj):
        """Badge visual para el estado activo/inactivo"""
        if obj.activo:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">✓ ACTIVO</span>'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">✗ INACTIVO</span>'
        )
    
    @admin.display(description='Último Acceso', ordering='fecha_ultimo_acceso')
    def ultimo_acceso_display(self, obj):
        """Muestra último acceso de forma amigable"""
        if not obj.fecha_ultimo_acceso:
            return format_html('<em style="color: #999;">Nunca</em>')
        
        # Calcular hace cuánto tiempo
        ahora = timezone.now()
        diferencia = ahora - obj.fecha_ultimo_acceso
        
        if diferencia.days == 0:
            if diferencia.seconds < 3600:
                minutos = diferencia.seconds // 60
                return format_html(
                    '<span style="color: #28a745;">Hace {} min</span>',
                    minutos
                )
            horas = diferencia.seconds // 3600
            return format_html(
                '<span style="color: #28a745;">Hace {} h</span>',
                horas
            )
        elif diferencia.days == 1:
            return format_html('<span style="color: #ffc107;">Ayer</span>')
        elif diferencia.days < 7:
            return format_html(
                '<span style="color: #ffc107;">Hace {} días</span>',
                diferencia.days
            )
        else:
            return obj.fecha_ultimo_acceso.strftime('%d/%m/%Y')
    
    # ==========================================
    # ACCIONES PERSONALIZADAS
    # ==========================================
    
    @admin.action(description='✅ Activar usuarios seleccionados')
    def activar_usuarios(self, request, queryset):
        """Activa múltiples usuarios"""
        count = queryset.update(activo=True)
        self.message_user(
            request,
            f'✅ {count} usuario(s) activado(s) exitosamente.'
        )
    
    @admin.action(description='❌ Desactivar usuarios seleccionados')
    def desactivar_usuarios(self, request, queryset):
        """Desactiva múltiples usuarios"""
        count = queryset.update(activo=False)
        self.message_user(
            request,
            f'❌ {count} usuario(s) desactivado(s) exitosamente.'
        )
    
    @admin.action(description='👑 Marcar como Administrador')
    def marcar_como_administrador(self, request, queryset):
        """Convierte usuarios a administradores"""
        count = queryset.update(tipo='administrador')
        self.message_user(
            request,
            f'👑 {count} usuario(s) marcado(s) como Administrador.'
        )
    
    @admin.action(description='👤 Marcar como Externo')
    def marcar_como_externo(self, request, queryset):
        """Convierte usuarios a externos"""
        count = queryset.update(tipo='externo')
        self.message_user(
            request,
            f'👤 {count} usuario(s) marcado(s) como Externo.'
        )
    
    # ==========================================
    # CONTROL DE PERMISOS
    # ==========================================
    
    def has_add_permission(self, request):
        """Solo administradores y superusuarios pueden crear usuarios"""
        return request.user.is_superuser or (
            hasattr(request.user, 'tipo') and 
            request.user.tipo == 'administrador'
        )
    
    def has_change_permission(self, request, obj=None):
        """Control de edición"""
        # Superusuarios pueden editar a todos
        if request.user.is_superuser:
            return True
        
        # Administradores pueden editar a otros (excepto superusuarios)
        if hasattr(request.user, 'tipo') and request.user.tipo == 'administrador':
            if obj is None:
                return True
            # No pueden editar superusuarios
            return not obj.is_superuser
        
        # Usuarios normales pueden editar solo su propio perfil
        if obj and obj.id == request.user.id:
            return True
        
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar usuarios"""
        # Solo superusuarios pueden eliminar
        if request.user.is_superuser:
            # Pero no pueden eliminarse a sí mismos
            if obj and obj.id == request.user.id:
                return False
            return True
        
        return False
    
    def get_actions(self, request):
        """Usuarios externos no ven acciones de edición"""
        actions = super().get_actions(request)
        
        # Usuarios externos no tienen acciones
        if hasattr(request.user, 'tipo') and request.user.tipo == 'externo':
            return {}
        
        # Usuarios normales (no admin) no pueden usar acciones en lote
        if not request.user.is_superuser and not (
            hasattr(request.user, 'tipo') and request.user.tipo == 'administrador'
        ):
            return {}
        
        return actions
    
    def get_queryset(self, request):
        """Filtrar usuarios según permisos"""
        qs = super().get_queryset(request)
        
        # Superusuarios ven todo
        if request.user.is_superuser:
            return qs
        
        # Administradores ven todos excepto superusuarios
        if hasattr(request.user, 'tipo') and request.user.tipo == 'administrador':
            return qs.filter(is_superuser=False)
        
        # Usuarios normales solo se ven a sí mismos
        return qs.filter(id=request.user.id)
    
    def get_readonly_fields(self, request, obj=None):
        """Campos readonly según usuario"""
        readonly = list(self.readonly_fields)
        
        # Si no es superusuario
        if not request.user.is_superuser:
            # No puede editar permisos de staff/superuser
            if obj:
                readonly.extend(['is_staff', 'is_superuser', 'groups', 'user_permissions'])
        
        # Si es usuario normal viendo su perfil
        if obj and obj.id == request.user.id and not (
            request.user.is_superuser or 
            (hasattr(request.user, 'tipo') and request.user.tipo == 'administrador')
        ):
            # Solo puede ver su info, no editarla
            readonly.extend(['tipo', 'activo', 'is_active'])
        
        return readonly
    
    # ==========================================
    # PERSONALIZACIÓN DE FORMULARIOS
    # ==========================================
    
    def save_model(self, request, obj, form, change):
        """Acciones al guardar"""
        # Si es nuevo usuario
        if not change:
            # Establecer valores por defecto
            if not obj.activo:
                obj.activo = True
            
            # Si no tiene tipo, por defecto externo
            if not obj.tipo:
                obj.tipo = 'externo'
        
        super().save_model(request, obj, form, change)