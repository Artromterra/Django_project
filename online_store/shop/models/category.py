from django.db import models


# TODO: The Category class references the SubCategory class -
#  need to add an implementation of the SubCategory class.


class SubCategory(models.Model):
    pass


class Category(models.Model):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    # DB fields
    name = models.CharField(blank=False, max_length=50)
    description = models.TextField(blank=False, max_length=5000)
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, related_name="subcategories", null=True)
