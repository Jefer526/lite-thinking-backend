"""
Views para Autenticación JWT
Usa el modelo Usuario del Core de Dominio
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from lite_thinking_domain.models import Usuario
from .serializers import (
    UsuarioSerializer,
    RegistroSerializer,
    CustomTokenObtainPairSerializer,
    CambiarPasswordSerializer
)
from .permissions import EsAdministrador


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para obtener token JWT
    POST /api/auth/login/
    """
    serializer_class = CustomTokenObtainPairSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios
    
    Endpoints:
    - GET    /api/auth/usuarios/          - Listar usuarios (Admin)
    - POST   /api/auth/usuarios/          - Crear usuario (Admin)
    - GET    /api/auth/usuarios/{id}/     - Detalle usuario (Admin)
    - PUT    /api/auth/usuarios/{id}/     - Actualizar usuario (Admin)
    - DELETE /api/auth/usuarios/{id}/     - Eliminar usuario (Admin)
    - GET    /api/auth/usuarios/me/       - Ver perfil propio
    - PUT    /api/auth/usuarios/me/       - Actualizar perfil propio
    - POST   /api/auth/usuarios/cambiar-password/ - Cambiar contraseña
    - POST   /api/auth/usuarios/registro/ - Registro público
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    def get_permissions(self):
        """Permisos según acción"""
        if self.action in ['registro']:
            permission_classes = [AllowAny]
        elif self.action in ['me', 'cambiar_password']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [EsAdministrador]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Seleccionar serializer según acción"""
        if self.action == 'registro':
            return RegistroSerializer
        elif self.action == 'cambiar_password':
            return CambiarPasswordSerializer
        return UsuarioSerializer
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def registro(self, request):
        """
        Registro público de usuarios
        POST /api/auth/usuarios/registro/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        
        response_serializer = UsuarioSerializer(usuario)
        return Response(
            {
                'message': 'Usuario registrado exitosamente',
                'usuario': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Ver o actualizar perfil del usuario autenticado
        GET  /api/auth/usuarios/me/
        PUT  /api/auth/usuarios/me/
        """
        usuario = request.user
        
        if request.method == 'GET':
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data)
        
        # PUT/PATCH: Actualizar perfil
        serializer = UsuarioSerializer(
            usuario,
            data=request.data,
            partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Perfil actualizado exitosamente',
            'usuario': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def cambiar_password(self, request):
        """
        Cambiar contraseña del usuario autenticado
        POST /api/auth/usuarios/cambiar-password/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Contraseña cambiada exitosamente'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[EsAdministrador])
    def activar(self, request, pk=None):
        """Activar usuario (Solo Admin)"""
        usuario = self.get_object()
        usuario.activar()
        
        return Response({
            'message': f'Usuario {usuario.username} activado exitosamente'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[EsAdministrador])
    def desactivar(self, request, pk=None):
        """Desactivar usuario (Solo Admin)"""
        usuario = self.get_object()
        usuario.desactivar()
        
        return Response({
            'message': f'Usuario {usuario.username} desactivado exitosamente'
        })
    
    @action(detail=False, methods=['get'], permission_classes=[EsAdministrador])
    def administradores(self, request):
        """Listar solo usuarios administradores"""
        usuarios = Usuario.objects.filter(tipo='administrador')
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[EsAdministrador])
    def externos(self, request):
        """Listar solo usuarios externos"""
        usuarios = Usuario.objects.filter(tipo='externo')
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data)
