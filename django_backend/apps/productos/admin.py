"""
Admin para Productos
"""
from django.contrib import admin
from django.utils.html import format_html
from decimal import Decimal
from lite_thinking_domain.models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Admin para Producto con permisos y visualización mejorada"""
    
    list_display = [
        'codigo',
        'nombre',
        'empresa',
        'precio_badge',
        'tipo_badge',
        'stock_actual_badge',
        'estado_badge',
        'created_at'
    ]
    list_filter = ['tipo', 'activo', 'empresa', 'created_at', 'updated_at']
    search_fields = ['codigo', 'nombre', 'descripcion', 'empresa__nombre']
    readonly_fields = [
        'codigo',
        'created_at',
        'updated_at',
        'stock_inventario',
        'link_inventario'
    ]
    ordering = ['-created_at']  # Más recientes primero
    
    fieldsets = (
        ('Información General', {
            'fields': ('empresa', 'codigo', 'nombre', 'descripcion')
        }),
        ('Precio', {
            'fields': ('precio_usd',)
        }),
        ('Clasificación', {
            'fields': ('tipo',)
        }),
        ('Inventario', {
            'fields': ('stock_minimo', 'stock_inventario', 'link_inventario'),
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_productos', 'desactivar_productos']
    
    # ==========================================
    # MÉTODOS DE AYUDA PARA LIST_DISPLAY
    # ==========================================
    
    @admin.display(description='Precio', ordering='precio_usd')
    def precio_badge(self, obj):
        """Muestra precio en USD con badge"""
        from decimal import Decimal
        
        # Obtener el valor como Decimal puro
        precio = obj.precio_usd
        if isinstance(precio, str):
            precio = Decimal(precio)
        
        return format_html(
            '<span style="background: #28a745; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">💵 ${} USD</span>',
            f'{precio:,.2f}'
        )
    
    @admin.display(description='Tipo', ordering='tipo')
    def tipo_badge(self, obj):
        """Badge visual para el tipo de producto"""
        colores = {
            'fisico': ('#007bff', '📦 FÍSICO'),
            'servicio': ('#28a745', '🔧 SERVICIO'),
            'digital': ('#6f42c1', '💻 DIGITAL'),
        }
        color, texto = colores.get(obj.tipo, ('#6c757d', f'📌 {obj.tipo.upper()}'))
        
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color, texto
        )
    
    @admin.display(description='Stock', ordering='inventario__cantidad_actual')
    def stock_actual_badge(self, obj):
        """Muestra stock actual con badge de color"""
        try:
            inventario = obj.inventario
            cantidad = inventario.cantidad_actual
            
            # Determinar color según nivel de stock
            if cantidad == 0:
                color = '#dc3545'
                icon = '⚠️'
            elif cantidad <= obj.stock_minimo:
                color = '#ffc107'
                icon = '⚡'
            elif cantidad <= obj.stock_minimo * 2:
                color = '#17a2b8'
                icon = '📊'
            else:
                color = '#28a745'
                icon = '✅'
            
            return format_html(
                '<span style="background: {}; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">{} {}</span>',
                color, icon, cantidad
            )
        except:
            return format_html(
                '<span style="color: #999; font-style: italic;">Sin inventario</span>'
            )
    
    @admin.display(description='Estado', ordering='activo')
    def estado_badge(self, obj):
        """Badge visual para estado activo/inactivo"""
        if obj.activo:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">✓ ACTIVO</span>'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">✗ INACTIVO</span>'
        )
    
    @admin.display(description='Stock en Inventario')
    def stock_inventario(self, obj):
        """Muestra información detallada del inventario"""
        try:
            inventario = obj.inventario
            cantidad = inventario.cantidad_actual
            estado = inventario.estado_stock
            
            # Badges de estado
            estados_badges = {
                'sin_stock': ('<span style="background: #dc3545; color: white; padding: 3px 8px; '
                             'border-radius: 3px; font-size: 11px;">⚠️ SIN STOCK</span>'),
                'bajo': ('<span style="background: #ffc107; color: white; padding: 3px 8px; '
                        'border-radius: 3px; font-size: 11px;">⚡ BAJO</span>'),
                'medio': ('<span style="background: #17a2b8; color: white; padding: 3px 8px; '
                         'border-radius: 3px; font-size: 11px;">📊 MEDIO</span>'),
                'suficiente': ('<span style="background: #28a745; color: white; padding: 3px 8px; '
                              'border-radius: 3px; font-size: 11px;">✅ SUFICIENTE</span>'),
            }
            
            return format_html(
                '<div style="line-height: 2;">'
                '<strong>Cantidad:</strong> {} unidades<br>'
                '<strong>Estado:</strong> {}<br>'
                '<strong>Ubicación:</strong> {}<br>'
                '<strong>Requiere reabastecimiento:</strong> {}'
                '</div>',
                cantidad,
                estados_badges.get(estado, estado),
                inventario.ubicacion or '<em>Sin ubicación</em>',
                '✅ Sí' if inventario.requiere_reabastecimiento else '❌ No'
            )
        except:
            return format_html(
                '<span style="color: #dc3545;">⚠️ No hay inventario creado</span>'
            )
    
    @admin.display(description='Ver Inventario')
    def link_inventario(self, obj):
        """Link directo al inventario del producto"""
        try:
            from django.urls import reverse
            inventario = obj.inventario
            url = reverse('admin:lite_thinking_domain_inventario_change', args=[inventario.id])
            
            return format_html(
                '<a href="{}" style="background: #007bff; color: white; padding: 6px 12px; '
                'border-radius: 4px; text-decoration: none; display: inline-block; font-size: 12px;">'
                '📦 Ver Inventario</a>',
                url
            )
        except:
            return format_html(
                '<span style="color: #999; font-style: italic;">Sin inventario</span>'
            )
    
    # ==========================================
    # OPTIMIZACIÓN DE QUERIES
    # ==========================================
    
    def get_queryset(self, request):
        """Optimizar queries con select_related"""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('empresa', 'inventario')
        return queryset
    
    # ==========================================
    # ACCIONES PERSONALIZADAS
    # ==========================================
    
    @admin.action(description='✅ Activar productos seleccionados')
    def activar_productos(self, request, queryset):
        """Activa múltiples productos"""
        count = queryset.update(activo=True)
        self.message_user(
            request,
            f'✅ {count} producto(s) activado(s) exitosamente.'
        )
    
    @admin.action(description='❌ Desactivar productos seleccionados')
    def desactivar_productos(self, request, queryset):
        """Desactiva múltiples productos"""
        count = queryset.update(activo=False)
        self.message_user(
            request,
            f'❌ {count} producto(s) desactivado(s) exitosamente.'
        )
    
    # ==========================================
    # CONTROL DE PERMISOS
    # ==========================================
    
    def has_add_permission(self, request):
        """Solo administradores pueden crear productos"""
        return request.user.is_superuser or (
            hasattr(request.user, 'tipo') and 
            request.user.tipo == 'administrador'
        )
    
    def has_change_permission(self, request, obj=None):
        """Solo administradores pueden editar productos"""
        return request.user.is_superuser or (
            hasattr(request.user, 'tipo') and 
            request.user.tipo == 'administrador'
        )
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar productos"""
        return request.user.is_superuser
    
    def get_actions(self, request):
        """Usuarios externos no ven acciones de edición"""
        actions = super().get_actions(request)
        
        # Si es usuario externo, remover acciones
        if hasattr(request.user, 'tipo') and request.user.tipo == 'externo':
            actions.pop('activar_productos', None)
            actions.pop('desactivar_productos', None)
            actions.pop('delete_selected', None)
        
        return actions
    
    # ==========================================
    # VALIDACIÓN AL ELIMINAR
    # ==========================================
    
    def delete_model(self, request, obj):
        """Validar antes de eliminar"""
        try:
            if hasattr(obj, 'inventario'):
                inventario = obj.inventario
                if inventario.cantidad_actual > 0:
                    self.message_user(
                        request,
                        f'❌ No se puede eliminar "{obj.nombre}" porque tiene {inventario.cantidad_actual} '
                        f'unidades en inventario. Primero registra salidas para llevar a 0.',
                        level='ERROR'
                    )
                    return
                
                # Si tiene inventario en 0, eliminarlo primero
                inventario.delete()
        except:
            pass
        
        super().delete_model(request, obj)
        self.message_user(
            request,
            f'✅ Producto "{obj.nombre}" eliminado exitosamente.'
        )
    
    def delete_queryset(self, request, queryset):
        """Validar eliminación en lote"""
        productos_con_stock = []
        productos_eliminados = 0
        
        for producto in queryset:
            try:
                if hasattr(producto, 'inventario') and producto.inventario.cantidad_actual > 0:
                    productos_con_stock.append(
                        f'{producto.nombre} ({producto.inventario.cantidad_actual} unidades)'
                    )
                else:
                    # Eliminar inventario si existe
                    if hasattr(producto, 'inventario'):
                        producto.inventario.delete()
                    producto.delete()
                    productos_eliminados += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'❌ Error al eliminar {producto.nombre}: {str(e)}',
                    level='ERROR'
                )
        
        # Mensajes
        if productos_eliminados > 0:
            self.message_user(
                request,
                f'✅ {productos_eliminados} producto(s) eliminado(s) exitosamente.'
            )
        
        if productos_con_stock:
            self.message_user(
                request,
                f'❌ No se pudieron eliminar estos productos porque tienen stock: '
                f'{", ".join(productos_con_stock)}',
                level='WARNING'
            )