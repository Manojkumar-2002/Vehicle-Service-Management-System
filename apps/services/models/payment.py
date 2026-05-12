import uuid
from django.db import models
from django.utils import timezone
from apps.services.constants.enums import OrderStatus
from .audit_trail import AuditTrail


class Payment(AuditTrail):
    order = models.ForeignKey(
        'services.ServiceOrder',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PAID)
    paid_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'services'
        ordering = ['-paid_at']

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"PAY-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount} ({self.status})"
