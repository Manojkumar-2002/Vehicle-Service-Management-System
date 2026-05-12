from django.db import models

class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    PAID = 'paid', 'Paid'

class ServiceType(models.TextChoices):
    REPAIR = 'repair', 'Repair'
    REPLACE = 'replace', 'Replace'

class PeriodChoice(models.TextChoices):
    DAILY = 'daily', 'Daily'
    MONTHLY = 'monthly', 'Monthly'
    YEARLY = 'yearly', 'Yearly'
