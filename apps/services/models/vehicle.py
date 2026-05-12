from django.db import models
from .audit_trail import AuditTrail

class Vehicle(AuditTrail):
    vin = models.CharField(max_length=17, unique=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)

    class Meta:
        app_label = 'services'
        indexes = [
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.make} {self.model} ({self.vin})"
