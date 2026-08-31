from django.db import models
from config import settings

# Create your models here.
class Donation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="donations")
    cause = models.ForeignKey("causes.Cause", on_delete=models.CASCADE, related_name="donations")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    currency = models.CharField(max_length=3, default="KES")
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    payment_method = models.CharField(max_length=20, default="MPESA")
    
    transaction_reference = models.CharField(max_length=100, null=True, blank=True)
    external_checkout_id = models.CharField(max_length=100, null=True, blank=True)
    failure_reason = models.CharField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user} -> {self.cause} {self.amount} {self.currency}"