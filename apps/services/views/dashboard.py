from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta

from ..models import ServiceOrder
from ..serializers import RevenueQuerySerializer
from apps.services.constants.enums import OrderStatus, PeriodChoice

class RevenueAnalyticsView(APIView):
    def get(self, request):
        serializer = RevenueQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        v_data = serializer.validated_data
        period = v_data['period']
        
        # Configuration mapping
        PERIOD_CONFIG = {
            PeriodChoice.DAILY: {'trunc': TruncDay('created_at'), 'format': '%Y-%m-%d'},
            PeriodChoice.MONTHLY: {'trunc': TruncMonth('created_at'), 'format': '%Y-%m'},
            PeriodChoice.YEARLY: {'trunc': TruncYear('created_at'), 'format': '%Y'}
        }
        config = PERIOD_CONFIG[period]

        # --- Dynamic Date Filtering ---
        filters = {'status': OrderStatus.PAID}
        
        if v_data.get('from_date'):
            filters['created_at__date__gte'] = v_data['from_date']
        
        if v_data.get('to_date'):
            filters['created_at__date__lte'] = v_data['to_date']
        
        # Default if no dates provided (e.g., last 30 days)
        if not v_data.get('from_date') and not v_data.get('to_date'):
            filters['created_at__gte'] = timezone.now() - timedelta(days=30)

        # Aggregate
        data = (
            ServiceOrder.objects.filter(**filters)
            .annotate(date_label=config['trunc'])
            .values('date_label')
            .annotate(amount=Sum('issues__price'))
            .order_by('date_label')
        )

        formatted_data = [
            {
                "date": item['date_label'].strftime(config['format']),
                "amount": float(item['amount']) if item['amount'] else 0
            } 
            for item in data
        ]

        return Response(formatted_data)