"""
Admin para Empresas
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from lite_thinking_domain.models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    """Admin para Empresa con permisos y acciones personalizadas"""
    
    list_display = [
        'nit',
        'nombre',
        'email',
        'telefono',
        'total_productos',
        'estado_badge',
        'created_at'
    ]
    list_filter = ['activa', 'created_at', 'updated_at']
    search_fields = ['nit', 'nombre', 'email', 'telefono']
    readonly_fields = ['created_at', 'updated_at', 'total_productos']
    ordering = ['-created_at']  # Más recientes primero
    
    fieldsets = (
        ('Información General', {
            'fields': ('nit', 'nombre', 'direccion')
        }),
        ('Contacto', {
            'fields': ('telefono', 'email')
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
        ('Estadísticas', {
            'fields': ('total_productos',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_empresas', 'desactivar_empresas']
    
    # ==========================================
    # MÉTODOS DE AYUDA PARA LIST_DISPLAY
    # ==========================================
    
    @admin.display(description='Productos', ordering='productos_count')
    def total_productos(self, obj):
        """Muestra cantidad total de productos"""
        # Usar la anotación si existe, sino contar directamente
        try:
            count = obj.productos_count
        except AttributeError:
            count = obj.productos.count()
        
        if count == 0:
            return format_html('<span style="color: #999;">0</span>')
        return format_html('<strong>{}</strong>', count)
    
    @admin.display(description='Estado', ordering='activa')
    def estado_badge(self, obj):
        """Muestra badge de estado activo/inactivo"""
        if obj.activa:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">✓ ACTIVA</span>'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">✗ INACTIVA</span>'
        )
    
    # ==========================================
    # OPTIMIZACIÓN DE QUERIES
    # ==========================================
    
    def get_queryset(self, request):
        """Optimizar queries agregando count de productos"""
        queryset = super().get_queryset(request)
        # CORRECCIÓN: usar 'productos' (plural) en lugar de 'producto'
        queryset = queryset.annotate(
            productos_count=Count('productos')
        )
        return queryset
    
    # ==========================================
    # ACCIONES PERSONALIZADAS
    # ==========================================
    
    @admin.action(description='✅ Activar empresas seleccionadas')
    def activar_empresas(self, request, queryset):
        """Activa múltiples empresas"""
        count = queryset.update(activa=True)
        self.message_user(
            request,
            f'✅ {count} empresa(s) activada(s) exitosamente.'
        )
    
    @admin.action(description='❌ Desactivar empresas seleccionadas')
    def desactivar_empresas(self, request, queryset):
        """Desactiva múltiples empresas"""
        count = queryset.update(activa=False)
        self.message_user(
            request,
            f'❌ {count} empresa(s) desactivada(s) exitosamente.'
        )
    
    # ==========================================
    # CONTROL DE PERMISOS
    # ==========================================
    
    def has_add_permission(self, request):
        """Solo administradores pueden crear empresas"""
        return request.user.is_superuser or (
            hasattr(request.user, 'tipo') and 
            request.user.tipo == 'administrador'
        )
    
    def has_change_permission(self, request, obj=None):
        """Solo administradores pueden editar empresas"""
        return request.user.is_superuser or (
            hasattr(request.user, 'tipo') and 
            request.user.tipo == 'administrador'
        )
    
    def has_delete_permission(self, request, obj=None):
        """Solo administradores pueden eliminar empresas"""
        return request.user.is_superuser or (
            hasattr(request.user, 'tipo') and 
            request.user.tipo == 'administrador'
        )
    
    def get_actions(self, request):
        """Usuarios externos no ven acciones de edición"""
        actions = super().get_actions(request)
        
        # Si es usuario externo, remover acciones
        if hasattr(request.user, 'tipo') and request.user.tipo == 'externo':
            actions.pop('activar_empresas', None)
            actions.pop('desactivar_empresas', None)
            actions.pop('delete_selected', None)
        
        return actions
    
    # ==========================================
    # VALIDACIÓN AL ELIMINAR
    # ==========================================
    
    def delete_model(self, request, obj):
        """Validar antes de eliminar"""
        productos_count = obj.productos.count()
        
        if productos_count > 0:
            self.message_user(
                request,
                f'❌ No se puede eliminar la empresa "{obj.nombre}" porque tiene '
                f'{productos_count} producto(s) asociado(s). '
                f'Primero elimina o reasigna los productos.',
                level='ERROR'
            )
            return
        
        super().delete_model(request, obj)
        self.message_user(
            request,
            f'✅ Empresa "{obj.nombre}" eliminada exitosamente.'
        )
    
    def delete_queryset(self, request, queryset):
        """Validar eliminación en lote"""
        empresas_con_productos = []
        empresas_eliminadas = 0
        
        for empresa in queryset:
            if empresa.productos.count() > 0:
                empresas_con_productos.append(empresa.nombre)
            else:
                empresa.delete()
                empresas_eliminadas += 1
        
        # Mensajes
        if empresas_eliminadas > 0:
            self.message_user(
                request,
                f'✅ {empresas_eliminadas} empresa(s) eliminada(s) exitosamente.'
            )
        
        if empresas_con_productos:
            self.message_user(
                request,
                f'❌ No se pudieron eliminar estas empresas porque tienen productos: '
                f'{", ".join(empresas_con_productos)}',
                level='WARNING'
            )