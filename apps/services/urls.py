from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ComponentViewSet, 
    VehicleViewSet, 
    ServiceOrderViewSet, 
    IssueViewSet,
    PaymentProcessView,
    RevenueAnalyticsView,
    ComponentAnalyticsView
)

# Initialize the router
router = DefaultRouter()

# Register ViewSets
# The first argument is the URL prefix, the second is the ViewSet class
router.register(r'components', ComponentViewSet, basename='component')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'orders', ServiceOrderViewSet, basename='service-order')
router.register(r'issues', IssueViewSet, basename='issue')

urlpatterns = [
    # Include all the router-generated URLs
    path('', include(router.urls)),
    path('orders/<int:order_id>/pay/', PaymentProcessView.as_view(), name='order-pay'),
    path('revenue-analytics/', RevenueAnalyticsView.as_view(), name='revenue-analytics'),
    path('component-analytics/', ComponentAnalyticsView.as_view(), name='component-analytics'),
]
