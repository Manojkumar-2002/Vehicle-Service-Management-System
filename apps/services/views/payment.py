from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from decimal import Decimal

from ..models import ServiceOrder
from ..models.payment import Payment
from apps.services.constants.enums import OrderStatus
from apps.common.utils.response_utils import ResponseHandler


class PaymentProcessView(APIView):
    """Handles payment processing with JWT authentication and audit trail.
    - Users can only pay for their own orders
    - Operations users can pay for any order
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        user = request.user
        # Operations users can pay any order; regular users only their own
        if user.groups.filter(name='operations').exists():
            order = get_object_or_404(ServiceOrder, id=order_id)
        else:
            order = get_object_or_404(ServiceOrder, id=order_id, created_by=user)

        if order.status == OrderStatus.PAID:
            return ResponseHandler.error_response(
                "Already paid.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Get amount from payload
        amount_paid_raw = request.data.get('amount_paid')
        if not amount_paid_raw:
            return ResponseHandler.error_response(
                "amount_paid required.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Compare provided amount with system total
        amount_paid = Decimal(str(amount_paid_raw))
        if amount_paid != order.total_price:
            return ResponseHandler.error_response(
                "Amount mismatch",
                errors={
                    "expected": float(order.total_price),
                    "received": float(amount_paid)
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Finalize order
        order.status = OrderStatus.PAID
        order.save()

        # Create payment record for audit trail
        payment = Payment.objects.create(
            order=order,
            amount=amount_paid,
        )

        return ResponseHandler.success_response(
            "Payment successful",
            data={
                "status": "paid",
                "transaction_id": payment.transaction_id,
                "paid_at": payment.paid_at,
            },
            status_code=status.HTTP_200_OK
        )