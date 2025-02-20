from django.db import models
from .product import Product


class Property(models.Model):
    class Meta:
        verbose_name = "Property name"
        verbose_name_plural = "Properties names"
    def __str__(self):
        return self.name

    # DB fields
    name = models.CharField(blank=True,
                            max_length=100,
                            db_index=True)


class PropertyValue(models.Model):
    class Meta:
        verbose_name = "Property value"
        verbose_name_plural = "Properties values"
    def __str__(self):
        return self.value

    # DB fields
    value = models.CharField(blank=True,
                             max_length=100,
                             db_index=True)

#Properties main model
class ProductProperties(models.Model):
    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"

    def __str__(self):
        return self.title

    # DB fields
    title = models.CharField(blank=True,
                             max_length=100,
                             db_index=True)

    # DB relatives
    product = models.ManyToManyField(Product)
    property = models.ForeignKey(Property,
                                    on_delete=models.CASCADE,
                                    related_name="product_properties",
                                    null=True,
                                    blank=True)
    value = models.ForeignKey(PropertyValue,
                                    on_delete=models.CASCADE,
                                    related_name="product_properties_value",
                                    null=True,
                                    blank=True)


