from django.db import models
from .product import Product

#Properties main model
class ProductProperties(models.Model):
    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.title

    # DB fields
    title = models.CharField(blank=True, max_length=100, db_index=True)

    # DB relatives
    product = models.ManyToManyField(Product)
    values = models.ManyToManyField("ProductPropertiesValues", related_name="properties", null=True, blank=True)

class ProductPropertiesValues(models.Model):
    def __str__(self):
        return self.value
    
    # DB fields
    value = models.CharField(blank=True, max_length=100, db_index=True)