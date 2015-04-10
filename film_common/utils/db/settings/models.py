from django.db import models

class Settings(models.Model):
    namespace = models.CharField(max_length=16)
    key = models.CharField(max_length=64, db_index=True)
    value = models.TextField(default=None, null=True, blank=True)

    class Meta:
        unique_together = [('namespace', 'key')]
