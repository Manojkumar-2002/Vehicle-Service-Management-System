from django.db import models
from apps.services.constants.enums import OrderStatus, ServiceType

class ServiceOrder(models.Model):
    # String reference avoids importing Vehicle class directly
    vehicle = models.ForeignKey(
        'services.Vehicle', 
        on_delete=models.CASCADE, 
        related_name='service_orders'
    )
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)


    @property
    def total_price(self):
        return sum(issue.price for issue in self.issues.all())

    def __str__(self):
        return f"Order {self.id} - {self.status}"

class Issue(models.Model):
    service_order = models.ForeignKey(
        'services.ServiceOrder', 
        related_name='issues', 
        on_delete=models.CASCADE
    )
    component = models.ForeignKey(
        'services.Component', 
        on_delete=models.PROTECT
    )
    issue_type = models.CharField(max_length=10, choices=ServiceType.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        app_label = 'services'

    def save(self, *args, **kwargs):
        # Logic to auto-set price from the related component
        if not self.price:
            if self.issue_type == ServiceType.REPAIR:
                self.price = self.component.repair_price
            else:
                self.price = self.component.purchase_price
        super().save(*args, **kwargs)
