from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, DecimalField
from django.db.models.functions import Coalesce, TruncDay, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta

from ..models import ServiceOrder, Issue, Component
from ..serializers import RevenueQuerySerializer
from apps.services.constants.enums import OrderStatus, ServiceType, PeriodChoice
from apps.common.utils.response_utils import ResponseHandler
from rest_framework import status
from rest_framework.views import APIView
from decimal import Decimal


class RevenueAnalyticsView(APIView):
    """
    Revenue analytics endpoint.
    - Regular users: only see revenue from their own orders
    - Operations users: see all revenue
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = RevenueQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return ResponseHandler.error_response(
                message="Invalid query parameters",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        v_data = serializer.validated_data
        period = v_data['period']

        # Configuration mapping
        PERIOD_CONFIG = {
            PeriodChoice.DAILY: {'trunc': TruncDay('created_at'), 'format': '%Y-%m-%d'},
            PeriodChoice.MONTHLY: {'trunc': TruncMonth('created_at'), 'format': '%Y-%m'},
            PeriodChoice.YEARLY: {'trunc': TruncYear('created_at'), 'format': '%Y'}
        }
        config = PERIOD_CONFIG[period]

        # --- Dynamic Filtering ---
        filters = {'status': OrderStatus.PAID}

        # Data scoping: regular users only see their own revenue
        user = request.user
        if not user.groups.filter(name='operations').exists():
            filters['created_by'] = user

        if v_data.get('from_date'):
            filters['created_at__date__gte'] = v_data['from_date']

        if v_data.get('to_date'):
            filters['created_at__date__lte'] = v_data['to_date']

        # Default if no dates provided (last 30 days)
        if not v_data.get('from_date') and not v_data.get('to_date'):
            now = timezone.now()
            if period == PeriodChoice.DAILY:
                filters['created_at__gte'] = now - timedelta(days=30)
            elif period == PeriodChoice.MONTHLY:
                filters['created_at__gte'] = now - timedelta(days=30*6)  # Last 6 months
            elif period == PeriodChoice.YEARLY:
                filters['created_at__gte'] = now - timedelta(days=365)  # Last year

        # Aggregate — Coalesce ensures 0 instead of NULL when no issues
        data = (
            ServiceOrder.objects.filter(**filters)
            .annotate(date_label=config['trunc'])
            .values('date_label')
            .annotate(amount=Coalesce(Sum('issues__price'), Decimal('0.00')))
            .order_by('date_label')
        )

        formatted_data = [
            {
                "date": item['date_label'].strftime(config['format']),
                "amount": float(item['amount'])
            }
            for item in data
        ]

        return ResponseHandler.success_response(
            "Revenue data fetched successfully",
            data=formatted_data
        )


class ComponentAnalyticsView(APIView):
    """
    Component analytics endpoint showing usage statistics.
    - Which components are most used (repair vs replace breakdown)
    - Revenue generated per component
    - Only considers PAID orders for revenue data
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Build order filters: only paid orders, scoped by user role
        order_filters = {'status': OrderStatus.PAID}
        if not user.groups.filter(name='operations').exists():
            order_filters['created_by'] = user

        # Aggregate component usage from issues on paid orders
        data = (
            Issue.objects.filter(service_order__in=ServiceOrder.objects.filter(**order_filters))
            .values('component__id', 'component__name')
            .annotate(
                total_used=Count('id'),
                repair_count=Count('id', filter=Q(issue_type=ServiceType.REPAIR)),
                replace_count=Count('id', filter=Q(issue_type=ServiceType.REPLACE)),
                total_revenue=Coalesce(Sum('price'), Decimal('0.00')),
            )
            .order_by('-total_used')
        )

        formatted_data = [
            {
                "component_id": item['component__id'],
                "component_name": item['component__name'],
                "total_used": item['total_used'],
                "repair_count": item['repair_count'],
                "replace_count": item['replace_count'],
                "total_revenue": float(item['total_revenue']),
            }
            for item in data
        ]

        return ResponseHandler.success_response(
            "Component analytics fetched successfully",
            data=formatted_data
        )