from django.db import models
from profiles.models import User


def seller_directory_path(instance: "Seller", filename: str) -> str:
    return f"sellers/seller_{instance.id}/images/{filename}"


class Seller(models.Model):
    objects = models.Manager()

    class Meta:
        verbose_name = 'Seller'
        verbose_name_plural = 'Sellers'

    def __str__(self):
        return self.name

    # DB Fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller')

    name = models.CharField('Name', max_length=50)
    description = models.TextField('Description', blank=True)
    image = models.ImageField('Image', upload_to=seller_directory_path, blank=True, null=True)
    phone = models.CharField('Phone', max_length=20, unique=True)
    address = models.CharField('Address', max_length=80)
    email = models.EmailField('Email', unique=True)



