from django.db import models

class BlockchainNode(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=50, default='unknown')
    uptime = models.FloatField(default=0.0)  # Percentage
    resource_utilization = models.JSONField(default=dict)
    last_checked = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.url})"