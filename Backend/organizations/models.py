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
    # Compliance fields
    registration_number = models.CharField(max_length=100, unique=True)
    kra_pin = models.CharField(max_length=20, unique=True)
    tcc_number = models.CharField(max_length=50, unique=True)
    tcc_document = models.FileField(upload_to="organization_documents/tccs/")
    
    VERIFICATION_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_CHOICES, default='PENDING')
    
    PAYOUT_CHOICES = (
        ('PAYBILL', 'Paybill'),
        ('TILL', 'Till'),
        ('BANK', 'Bank Transfer'),
    )
    payout_method = models.CharField(max_length=20, choices=PAYOUT_CHOICES, default='BANK')
    payout_bank_name = models.CharField(max_length=100, null=True, blank=True)
    payout_shortcode = models.CharField(max_length=20, null=True, blank=True) # The Bank's Paybill or the NGO's Paybill/Till number
    payout_account_number = models.CharField(max_length=50, null=True, blank=True) # The bank account number or the paybill account number
    
    verified_at = models.DateTimeField(null=True, blank=True)
    
    contact_email = models.EmailField(null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    physical_address = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name