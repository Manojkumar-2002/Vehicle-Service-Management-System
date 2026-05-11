from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.db.models.functions import TruncDay

from ..models import Component, Vehicle, ServiceOrder, Issue
from apps.services.constants.enums import OrderStatus
from ..serializers import (
    ComponentSerializer, 
    VehicleSerializer, 
    ServiceOrderSerializer, 
    IssueSerializer
)

class ComponentViewSet(viewsets.ModelViewSet):
    """API endpoint for listing and editing components."""
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    """API endpoint for managing vehicle registration."""
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class ServiceOrderViewSet(viewsets.ModelViewSet):
    """API endpoint for managing service tickets."""
    queryset = ServiceOrder.objects.all().prefetch_related('issues')
    serializer_class = ServiceOrderSerializer

class IssueViewSet(viewsets.ModelViewSet):
    """API endpoint for specific issues/repairs."""
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
