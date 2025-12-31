from django.core.management.base import BaseCommand
from lite_thinking_domain.models import Usuario

class Command(BaseCommand):
    help = 'Activa usuarios externos que estén inactivos'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username del usuario a activar')

    def handle(self, *args, **options):
        username = options['username']
        try:
            usuario = Usuario.objects.get(username=username)
            usuario.activo = True
            usuario.is_active = True
            usuario.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario {username} activado exitosamente'))
        except Usuario.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuario {username} no existe'))
