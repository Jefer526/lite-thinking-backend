"""
Views para Empresas
Usa el modelo Empresa del Core de Dominio
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from lite_thinking_domain.models import Empresa
from .serializers import (
    EmpresaListSerializer,
    EmpresaDetailSerializer,
    EmpresaCreateSerializer,
    EmpresaUpdateSerializer
)


class EmpresaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Empresas"""
    queryset = Empresa.objects.all()
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activa', 'nit']
    search_fields = ['nit', 'nombre', 'email']
    ordering_fields = ['created_at', 'nombre', 'nit']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmpresaListSerializer
        elif self.action == 'retrieve':
            return EmpresaDetailSerializer
        elif self.action == 'create':
            return EmpresaCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EmpresaUpdateSerializer
        return EmpresaDetailSerializer
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete: desactiva la empresa"""
        instance = self.get_object()
        instance.desactivar()
        
        return Response(
            {'message': 'Empresa desactivada exitosamente'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar una empresa"""
        empresa = self.get_object()
        empresa.activar()
        
        serializer = self.get_serializer(empresa)
        return Response({
            'message': 'Empresa activada exitosamente',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar una empresa"""
        empresa = self.get_object()
        empresa.desactivar()
        
        serializer = self.get_serializer(empresa)
        return Response({
            'message': 'Empresa desactivada exitosamente',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Listar solo empresas activas"""
        activas = self.queryset.filter(activa=True)
        serializer = EmpresaListSerializer(activas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def inactivas(self, request):
        """Listar solo empresas inactivas"""
        inactivas = self.queryset.filter(activa=False)
        serializer = EmpresaListSerializer(inactivas, many=True)
        return Response(serializer.data)
