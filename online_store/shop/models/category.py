from django.db import models

class Category(models.Model):
    # DB fields
    name = models.CharField(blank=False, max_length=50)
    description = models.TextField(blank=False, max_length=5000)

