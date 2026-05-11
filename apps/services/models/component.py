from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Component(models.Model):
    name = models.CharField(max_length=255)
    
    
    repair_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    purchase_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    class Meta:
        app_label = 'services'

    def __str__(self):
        return self.name