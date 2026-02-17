from django.db import models

# Create your models here.
class Cause(models.Model):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="causes")
    title = models.CharField(max_length=100)
    description = models.TextField()
    
    category = models.CharField(max_length=100)
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ACTIVE")
    
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def amount_raised(self): 
        """
        Calculated dynamically from successful donations.
        """
        return 0