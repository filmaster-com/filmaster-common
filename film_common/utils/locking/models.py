from django.db import models

class Lock(models.Model):
    name = models.CharField(primary_key=True, max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

