"""
Signals para Productos
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from lite_thinking_domain.models import Producto, Inventario


@receiver(post_save, sender=Producto)
def crear_inventario_automatico(sender, instance, created, **kwargs):
    """
    Signal que crea automáticamente un Inventario con cantidad 0
    cuando se crea un nuevo Producto
    """
    if created:
        # Verificar que no exista ya un inventario
        if not hasattr(instance, 'inventario'):
            Inventario.objects.create(
                producto=instance,
                cantidad_actual=0,
                ubicacion=""
            )
            print(f"✅ Inventario creado automáticamente para: {instance.codigo} - {instance.nombre}")