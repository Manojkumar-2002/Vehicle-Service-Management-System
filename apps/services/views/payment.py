from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal
from ..models import ServiceOrder
from apps.services.constants.enums import OrderStatus


class PaymentProcessView(APIView):
    """Handles the 'Verification' of payment and closes the order."""
    def post(self, request, order_id):
        order = get_object_or_404(ServiceOrder, id=order_id)

        if order.status == OrderStatus.PAID:
            return Response({"error": "Already paid."}, status=status.HTTP_400_BAD_REQUEST)

        # Get amount from payload
        amount_paid_raw = request.data.get('amount_paid')
        if not amount_paid_raw:
            return Response({"error": "amount_paid required."}, status=status.HTTP_400_BAD_REQUEST)

        # Compare provided amount with system total
        amount_paid = Decimal(str(amount_paid_raw))
        if amount_paid != order.total_price:
            return Response({
                "error": "Amount mismatch",
                "expected": float(order.total_price),
                "received": float(amount_paid)
            }, status=status.HTTP_400_BAD_REQUEST)

        # Finalize
        order.status = OrderStatus.PAID
        order.save()
        return Response({"message": "Payment successful", "status": "paid"})
