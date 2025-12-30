"""
Admin para Inventario con acciones personalizadas
"""
from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.conf import settings
from django.db import connection
from django.utils.html import format_html
from lite_thinking_domain.models import Inventario, MovimientoInventario
from .reports import generar_pdf_inventario


# ========================================
# INLINE PARA MOVIMIENTOS
# ========================================
class MovimientoInventarioInline(admin.TabularInline):
    """
    Inline para mostrar movimientos dentro del inventario
    Solo lectura - no se pueden crear/editar desde aquí
    """
    model = MovimientoInventario
    extra = 0
    can_delete = False
    max_num = 50  # Limitar a 50 movimientos más recientes
    
    fields = ['tipo_badge', 'cantidad', 'motivo_corto', 'usuario', 'fecha']
    readonly_fields = ['tipo_badge', 'cantidad', 'motivo_corto', 'usuario', 'fecha']
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    @admin.display(description='Tipo')
    def tipo_badge(self, obj):
        """Badge visual para tipo de movimiento"""
        if obj.tipo == 'entrada':
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">📥 ENTRADA</span>'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">📤 SALIDA</span>'
        )
    
    @admin.display(description='Motivo')
    def motivo_corto(self, obj):
        """Motivo truncado"""
        if len(obj.motivo) > 50:
            return format_html('{}<em>...</em>', obj.motivo[:50])
        return obj.motivo
    
    def get_queryset(self, request):
        """Ordenar por fecha descendente (más recientes primero)"""
        qs = super().get_queryset(request)
        return qs.order_by('-fecha')
    
    verbose_name = "Movimiento de Inventario"
    verbose_name_plural = "📋 Historial de Movimientos (últimos 50)"


# ========================================
# ADMIN INVENTARIO
# ========================================
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    """Admin para Inventario con acciones personalizadas y permisos"""
    
    inlines = [MovimientoInventarioInline]
    
    list_display = [
        'producto',
        'cantidad_actual_badge',
        'ubicacion',
        'estado_stock_badge',
        'requiere_reabastecimiento_badge',
        'updated_at'
    ]
    list_filter = ['updated_at', 'producto__empresa']
    search_fields = ['producto__codigo', 'producto__nombre', 'ubicacion']
    readonly_fields = [
        'cantidad_actual',
        'created_at',
        'updated_at',
        'estado_stock',
        'requiere_reabastecimiento'
    ]
    ordering = ['-updated_at']  # Más recientes primero
    
    fieldsets = (
        ('Producto', {
            'fields': ('producto',)
        }),
        ('Stock', {
            'fields': ('cantidad_actual', 'estado_stock', 'requiere_reabastecimiento')
        }),
        ('Ubicación', {
            'fields': ('ubicacion',)
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'registrar_entrada_action',
        'registrar_salida_action',
        'descargar_pdf_action',
        'enviar_email_action'
    ]
    
    # ==========================================
    # MÉTODOS DE AYUDA PARA LIST_DISPLAY
    # ==========================================
    
    @admin.display(description='Stock', ordering='cantidad_actual')
    def cantidad_actual_badge(self, obj):
        """Badge visual para cantidad actual"""
        cantidad = obj.cantidad_actual
        stock_minimo = obj.producto.stock_minimo if obj.producto else 10
        
        # Determinar color según nivel de stock
        if cantidad == 0:
            color = '#dc3545'  # Rojo
            icon = '⚠️'
        elif cantidad <= stock_minimo:
            color = '#ffc107'  # Amarillo
            icon = '⚡'
        elif cantidad <= stock_minimo * 2:
            color = '#17a2b8'  # Cyan
            icon = '📊'
        else:
            color = '#28a745'  # Verde
            icon = '✅'
        
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, cantidad
        )
    
    @admin.display(description='Estado', ordering='cantidad_actual')
    def estado_stock_badge(self, obj):
        """Badge visual para estado de stock"""
        estado = obj.estado_stock
        
        if estado == 'sin_stock':
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">⚠️ SIN STOCK</span>'
            )
        elif estado == 'bajo':
            return format_html(
                '<span style="background: #ffc107; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">⚡ BAJO</span>'
            )
        elif estado == 'medio':
            return format_html(
                '<span style="background: #17a2b8; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">📊 MEDIO</span>'
            )
        else:  # suficiente
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">✅ SUFICIENTE</span>'
            )
    
    @admin.display(description='¿Reabastecer?', boolean=True)
    def requiere_reabastecimiento_badge(self, obj):
        """Indica si requiere reabastecimiento"""
        return obj.requiere_reabastecimiento
    
    # ==========================================
    # ACCIONES PERSONALIZADAS
    # ==========================================
    
    def registrar_entrada_action(self, request, queryset):
        """Acción para registrar entrada de inventario"""
        if queryset.count() != 1:
            self.message_user(
                request,
                "Selecciona solo UN inventario para registrar entrada",
                level=messages.ERROR
            )
            return
        
        inventario = queryset.first()
        
        if 'cantidad' in request.POST and 'motivo' in request.POST:
            try:
                cantidad = int(request.POST.get('cantidad'))
                motivo = request.POST.get('motivo')
                
                inventario.registrar_entrada(
                    cantidad=cantidad,
                    motivo=motivo,
                    usuario=request.user
                )
                
                self.message_user(
                    request,
                    f"✅ Entrada registrada: +{cantidad} unidades. Stock actual: {inventario.cantidad_actual}",
                    level=messages.SUCCESS
                )
                return redirect('admin:lite_thinking_domain_inventario_changelist')
            except ValueError as e:
                self.message_user(request, f"❌ Error: {str(e)}", level=messages.ERROR)
            except Exception as e:
                self.message_user(request, f"❌ Error: {str(e)}", level=messages.ERROR)
        
        context = {
            'inventario': inventario,
            'titulo': 'Registrar Entrada de Inventario',
            'tipo': 'entrada',
            'opts': self.model._meta,
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
        }
        return render(request, 'admin/inventario_movimiento.html', context)
    
    registrar_entrada_action.short_description = "📥 Registrar Entrada"
    
    def registrar_salida_action(self, request, queryset):
        """Acción para registrar salida de inventario"""
        if queryset.count() != 1:
            self.message_user(
                request,
                "Selecciona solo UN inventario para registrar salida",
                level=messages.ERROR
            )
            return
        
        inventario = queryset.first()
        
        if 'cantidad' in request.POST and 'motivo' in request.POST:
            try:
                cantidad = int(request.POST.get('cantidad'))
                motivo = request.POST.get('motivo')
                
                inventario.registrar_salida(
                    cantidad=cantidad,
                    motivo=motivo,
                    usuario=request.user
                )
                
                self.message_user(
                    request,
                    f"✅ Salida registrada: -{cantidad} unidades. Stock actual: {inventario.cantidad_actual}",
                    level=messages.SUCCESS
                )
                return redirect('admin:lite_thinking_domain_inventario_changelist')
            except ValueError as e:
                self.message_user(request, f"❌ Error: {str(e)}", level=messages.ERROR)
            except Exception as e:
                self.message_user(request, f"❌ Error: {str(e)}", level=messages.ERROR)
        
        context = {
            'inventario': inventario,
            'titulo': 'Registrar Salida de Inventario',
            'tipo': 'salida',
            'opts': self.model._meta,
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
        }
        return render(request, 'admin/inventario_movimiento.html', context)
    
    registrar_salida_action.short_description = "📤 Registrar Salida"
    
    def descargar_pdf_action(self, request, queryset):
        """Genera y descarga PDF del inventario seleccionado"""
        pdf_buffer = generar_pdf_inventario(queryset)
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="inventario_reporte.pdf"'
        
        self.message_user(
            request,
            f"📄 PDF generado con {queryset.count()} productos",
            level=messages.SUCCESS
        )
        
        return response
    
    descargar_pdf_action.short_description = "📄 Descargar PDF"
    
    def enviar_email_action(self, request, queryset):
        """Envía el reporte de inventario por email"""
        
        if 'email_destino' in request.POST:
            email_destino = request.POST.get('email_destino')
            
            try:
                print("="*50)
                print("🔍 INICIANDO ENVÍO DE EMAIL")
                print(f"Destino: {email_destino}")
                print(f"Cantidad de inventarios: {queryset.count()}")
                
                # Generar PDF
                print("📄 Generando PDF...")
                pdf_buffer = generar_pdf_inventario(queryset)
                pdf_size = len(pdf_buffer.getvalue())
                print(f"✅ PDF generado: {pdf_size} bytes")
                
                # Crear email
                print("📧 Creando email...")
                email = EmailMessage(
                    subject='Reporte de Inventario - Lite Thinking',
                    body=f'Adjunto encontrarás el reporte de inventario con {queryset.count()} productos.\n\nGenerado automáticamente por Lite Thinking.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email_destino]
                )
                print(f"From: {settings.DEFAULT_FROM_EMAIL}")
                print(f"To: {email_destino}")
                
                # Adjuntar PDF
                print("📎 Adjuntando PDF...")
                email.attach('inventario_reporte.pdf', pdf_buffer.read(), 'application/pdf')
                print("✅ PDF adjuntado")
                
                # Enviar
                print("🚀 Enviando email...")
                result = email.send()
                print(f"✅ Email enviado. Resultado: {result}")
                print("="*50)
                
                self.message_user(
                    request,
                    f"✅ Email enviado exitosamente a {email_destino} (PDF: {pdf_size} bytes)",
                    level=messages.SUCCESS
                )
                return redirect('admin:lite_thinking_domain_inventario_changelist')
                
            except Exception as e:
                print("="*50)
                print(f"❌ ERROR AL ENVIAR EMAIL")
                print(f"Tipo: {type(e).__name__}")
                print(f"Mensaje: {str(e)}")
                import traceback
                traceback.print_exc()
                print("="*50)
                
                self.message_user(
                    request,
                    f"❌ Error al enviar email: {str(e)}",
                    level=messages.ERROR
                )
        
        selected_ids = request.POST.getlist('_selected_action')
        
        # Mostrar formulario para pedir email
        context = {
            'total_productos': queryset.count(),
            'selected_ids': selected_ids,
            'opts': self.model._meta,
            'site_title': admin.site.site_title,
            'site_header': admin.site.site_header,
        }
        return render(request, 'admin/enviar_email_form.html', context)
    
    enviar_email_action.short_description = "📧 Enviar por Email"
    
    # ==========================================
    # CONTROL DE PERMISOS
    # ==========================================
    
    def has_add_permission(self, request):
        """Solo administradores pueden crear inventarios manualmente"""
        # Normalmente se crean automáticamente al crear producto
        return request.user.is_superuser or (
            hasattr(request.user, 'tipo') and 
            request.user.tipo == 'administrador'
        )
    
    def has_change_permission(self, request, obj=None):
        """Solo administradores pueden editar inventarios"""
        return request.user.is_superuser or (
            hasattr(request.user, 'tipo') and 
            request.user.tipo == 'administrador'
        )
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar inventarios"""
        return request.user.is_superuser
    
    def get_actions(self, request):
        """Usuarios externos solo pueden descargar PDF"""
        actions = super().get_actions(request)
        
        # Si es usuario externo
        if hasattr(request.user, 'tipo') and request.user.tipo == 'externo':
            # Remover acciones de modificación
            actions.pop('registrar_entrada_action', None)
            actions.pop('registrar_salida_action', None)
            actions.pop('enviar_email_action', None)
            actions.pop('delete_selected', None)
            # Solo dejar descargar PDF
        
        return actions
    
    def get_readonly_fields(self, request, obj=None):
        """Usuarios externos todo es readonly"""
        readonly = list(self.readonly_fields)
        
        # Si es externo, todo readonly
        if hasattr(request.user, 'tipo') and request.user.tipo == 'externo':
            return [f.name for f in self.model._meta.fields]
        
        return readonly


# ========================================
# ADMIN MOVIMIENTOS
# ========================================
@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    """Admin para MovimientoInventario - Inmutable"""
    
    list_display = [
        'id',
        'inventario_link',
        'tipo_badge',
        'cantidad',
        'motivo_corto',
        'usuario',
        'fecha'
    ]
    list_filter = ['tipo', 'fecha', 'usuario']
    search_fields = ['inventario__producto__codigo', 'inventario__producto__nombre', 'motivo']
    readonly_fields = ['inventario', 'tipo', 'cantidad', 'motivo', 'usuario', 'fecha']
    ordering = ['-fecha']
    
    fieldsets = (
        ('Movimiento', {
            'fields': ('inventario', 'tipo_badge_detail', 'cantidad', 'motivo')
        }),
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Fecha', {
            'fields': ('fecha',)
        }),
    )
    
    # ==========================================
    # MÉTODOS DE AYUDA
    # ==========================================
    
    @admin.display(description='Inventario', ordering='inventario')
    def inventario_link(self, obj):
        """Link al inventario"""
        from django.urls import reverse
        url = reverse('admin:lite_thinking_domain_inventario_change', args=[obj.inventario.id])
        return format_html(
            '<a href="{}" style="color: #007bff; text-decoration: none;">'
            '📦 {}</a>',
            url, obj.inventario.producto.nombre
        )
    
    @admin.display(description='Tipo', ordering='tipo')
    def tipo_badge(self, obj):
        """Badge visual para tipo de movimiento"""
        if obj.tipo == 'entrada':
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">📥 ENTRADA</span>'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">📤 SALIDA</span>'
        )
    
    @admin.display(description='Tipo')
    def tipo_badge_detail(self, obj):
        """Badge para vista de detalle"""
        return self.tipo_badge(obj)
    
    @admin.display(description='Motivo')
    def motivo_corto(self, obj):
        """Motivo truncado para list_display"""
        if len(obj.motivo) > 60:
            return format_html('{}<em>...</em>', obj.motivo[:60])
        return obj.motivo
    
    # ==========================================
    # CONTROL DE PERMISOS
    # ==========================================
    
    def has_add_permission(self, request):
        """No se pueden crear movimientos manualmente"""
        # Los movimientos se crean a través de las acciones del admin de Inventario
        return False
    
    def has_change_permission(self, request, obj=None):
        """Movimientos son inmutables"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar movimientos (desarrollo)"""
        return request.user.is_superuser
    
    def get_queryset(self, request):
        """Filtrar movimientos según usuario"""
        queryset = super().get_queryset(request)
        
        # Superusuarios y administradores ven todo
        if request.user.is_superuser:
            return queryset
        
        if hasattr(request.user, 'tipo') and request.user.tipo == 'administrador':
            return queryset
        
        # Usuarios normales/externos ven solo movimientos de su empresa (si aplica)
        # Por ahora, todos ven todo pero no pueden modificar
        return queryset
    
    # ==========================================
    # ELIMINACIÓN (SOLO DESARROLLO)
    # ==========================================
    
    def delete_model(self, request, obj):
        """Usar SQL directo para bypass constraints"""
        inventario_id = obj.inventario.id
        inventario_actual = obj.inventario.cantidad_actual
        
        if obj.tipo == 'entrada':
            nueva_cantidad = inventario_actual - obj.cantidad
        else:
            nueva_cantidad = inventario_actual + obj.cantidad
        
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE inventarios SET cantidad_actual = %s WHERE id = %s",
                [nueva_cantidad, inventario_id]
            )
        
        obj.delete()
        
        self.message_user(
            request,
            f"✅ Movimiento eliminado. Stock actualizado a: {nueva_cantidad}",
            level=messages.SUCCESS
        )
    
    def delete_queryset(self, request, queryset):
        """Borrado múltiple con SQL directo"""
        total = queryset.count()
        
        with connection.cursor() as cursor:
            for obj in queryset:
                inventario_id = obj.inventario.id
                inventario_actual = obj.inventario.cantidad_actual
                
                if obj.tipo == 'entrada':
                    nueva_cantidad = inventario_actual - obj.cantidad
                else:
                    nueva_cantidad = inventario_actual + obj.cantidad
                
                cursor.execute(
                    "UPDATE inventarios SET cantidad_actual = %s WHERE id = %s",
                    [nueva_cantidad, inventario_id]
                )
        
        queryset.delete()
        
        self.message_user(
            request,
            f"✅ {total} movimientos eliminados",
            level=messages.SUCCESS
        )