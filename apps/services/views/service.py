from rest_framework.permissions import IsAuthenticated

from ..models import Component, Vehicle, ServiceOrder, Issue
from ..serializers import (
    ComponentSerializer,
    VehicleSerializer,
    ServiceOrderSerializer,
    IssueSerializer
)
from apps.users.permissions import IsOperationsOrReadOnly
from apps.common.views.base_views import BaseAPIViewSet


class ComponentViewSet(BaseAPIViewSet):
    """
    API endpoint for components.
    - Operations users: full CRUD (register new components, set pricing)
    - Regular users: read-only (can view components for issue selection)
    """
    permission_classes = [IsAuthenticated, IsOperationsOrReadOnly]
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer


class VehicleViewSet(BaseAPIViewSet):
    """API endpoint for managing vehicle registration.
    - Users see only their own vehicles
    - Operations users see all vehicles
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VehicleSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='operations').exists():
            return Vehicle.objects.all()
        return Vehicle.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class ServiceOrderViewSet(BaseAPIViewSet):
    """API endpoint for managing service tickets.
    - Users see only their own orders
    - Operations users see all orders
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceOrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='operations').exists():
            return ServiceOrder.objects.all().prefetch_related('issues')
        return ServiceOrder.objects.filter(created_by=user).prefetch_related('issues')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class IssueViewSet(BaseAPIViewSet):
    """API endpoint for specific issues/repairs.
    - Users can only see/edit/delete issues on their own orders
    - Operations users can see/edit/delete all issues
    """
    permission_classes = [IsAuthenticated]
    serializer_class = IssueSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='operations').exists():
            return Issue.objects.all().select_related('service_order', 'component')
        return Issue.objects.filter(
            service_order__created_by=user
        ).select_related('service_order', 'component')