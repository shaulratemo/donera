from django.db import models
from config import settings

# Create your models here.
class Report(models.Model):
    cause = models.ForeignKey("causes.Cause", on_delete=models.CASCADE, related_name="reports")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports")
    content = models.TextField()
    summary = models.TextField(null=True, blank=True)
    evidence = models.FileField(upload_to="reports/")
    STATUS_CHOICES = (
        ("DRAFT", "Draft"),
        ("PUBLISHED", "Published"),
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="DRAFT")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Report for {self.cause} ({self.status})"