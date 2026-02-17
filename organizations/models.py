from config import settings
from django.db import models

# Create your models here.
class Organization(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organization",
        limit_choices_to={"role": "ORGANIZATION"},
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    registration_number = models.CharField(max_length=100, unique=True)
    
    VERIFICATION_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES,
                                           default='PENDING')
    verified_at = models.DateTimeField(null=True, blank=True)
    
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name