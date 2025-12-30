"""
Serializers para Empresas
Usa el modelo Empresa del Core de Dominio
"""
from rest_framework import serializers
from lite_thinking_domain.models import Empresa


class EmpresaListSerializer(serializers.ModelSerializer):
    """Serializer para listar empresas (solo campos necesarios)"""
    
    class Meta:
        model = Empresa
        fields = [
            'id',
            'nit',
            'nombre',
            'email',
            'activa',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmpresaDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver detalle completo de una empresa"""
    
    class Meta:
        model = Empresa
        fields = [
            'id',
            'nit',
            'nombre',
            'direccion',
            'telefono',
            'email',
            'activa',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EmpresaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear una nueva empresa"""
    
    class Meta:
        model = Empresa
        fields = [
            'nit',
            'nombre',
            'direccion',
            'telefono',
            'email',
            'activa'
        ]
    
    def validate_email(self, value):
        """Validación de email único"""
        value = value.lower().strip()
        
        if self.instance:
            if Empresa.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("Ya existe una empresa con este email")
        else:
            if Empresa.objects.filter(email=value).exists():
                raise serializers.ValidationError("Ya existe una empresa con este email")
        
        return value


class EmpresaUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar una empresa existente"""
    
    class Meta:
        model = Empresa
        fields = [
            'nombre',
            'direccion',
            'telefono',
            'email',
            'activa'
        ]
    
    def validate_email(self, value):
        """Validación de email único para actualización"""
        value = value.lower().strip()
        
        if Empresa.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
            raise serializers.ValidationError("Ya existe una empresa con este email")
        
        return value


class EmpresaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple para referencia desde otros modelos"""
    
    class Meta:
        model = Empresa
        fields = ['id', 'nit', 'nombre']
        read_only_fields = ['id', 'nit', 'nombre']
