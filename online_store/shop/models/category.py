from django.db import models

class Category(models.Model):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    # DB fields
    name = models.CharField(blank=False, max_length=50)
    description = models.TextField(blank=False, max_length=5000)

class SubCategory(models.Model):
    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"

    def __str__(self):
        return self.name

    name = models.CharField(blank=False, max_length=50)
    description = models.TextField(blank=False, max_length=5000)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")