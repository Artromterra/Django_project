from django.core.exceptions import ValidationError
from django.db import models
import xml.etree.ElementTree as ET
from django.utils.safestring import mark_safe


def is_svg(file):
    try:
        file.seek(0)
        for event, el in ET.iterparse(file, ('start',)):
            return el.tag == '{http://www.w3.org/2000/svg}svg'
    except ET.ParseError:
        return False
    finally:
        file.seek(0)
    return False


def validate_svg(file):
    if not is_svg(file):
        raise ValidationError("Uploaded file is not a valid SVG")


class Category(models.Model):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=50)
    category_icon = models.FileField(
        upload_to="category/icons/", validators=[validate_svg], blank=True, null=True
    )

    def __str__(self):
        return self.name

    def icon_preview(self):
        if self.category_icon:
            return mark_safe(f'<img src="{self.category_icon.url}" width="50" height="50" />')
        return "(No Icon)"

    icon_preview.short_description = "Preview"

    # DB fields
    description = models.TextField(blank=False, max_length=5000)
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, related_name="subcategories", blank=True, null=True)
    is_active = models.BooleanField(default=False)
