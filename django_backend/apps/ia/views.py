from rest_framework import viewsets
from lite_thinking_domain.models import Conversacion, Mensaje
from .serializers import ConversacionSerializer, MensajeSerializer

class ConversacionViewSet(viewsets.ModelViewSet):
    queryset = Conversacion.objects.all()
    serializer_class = ConversacionSerializer

class MensajeViewSet(viewsets.ModelViewSet):
    queryset = Mensaje.objects.all()
    serializer_class = MensajeSerializer
