from django.db import models
from django.utils.text import slugify
from decimal import Decimal
from django.db.models.functions import Coalesce
from django.db.models import Sum


class Category(models.Model):
    """
    Category model for causes.
    Acts as the mapping anchor for the AI recommendation engine.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Override save to automatically generate slug from name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Cause(models.Model):
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE, related_name="causes")
    title = models.CharField(max_length=100)
    description = models.TextField()
    cover_image = models.FileField(upload_to="causes/covers/", null=True, blank=True)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='causes')
    
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
        from donations.models import Donation
        total = Donation.objects.filter(
            cause=self,
            status="SUCCESS"
        ).aggregate(total=Coalesce(Sum("amount"), Decimal("0.00")))["total"]
        return total