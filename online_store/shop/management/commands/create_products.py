
import random

from django.core.management.base import BaseCommand

from shop.factories.products import ProductFactory
from shop.models.category import Category
from shop.models.seller import Seller


class Command(BaseCommand):
    help = "Create random products"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            required=True,
            help='Number random products.'
        )

    def handle(self, *args, **options):
        count = options['count']

        categories = Category.objects.all()
        if not categories.exists():
            self.stderr.write(
                "There is not a single category in the database.\n"
                "To generate categories, use the django command "
                "create_categories --count=<number of categories>"
            )
            return

        for num in range(count):
            product = ProductFactory.create(
                category=random.choice(categories),
            )
            self.stdout.write(
                f"Create {num} product:\n"
                f"{product.pk=}\n"
                f"{product.title=}\n"
                f"{product.description=}\n"
                f"{product.short_description=}\n"
                f"{product.price=}\n"
                f"{product.is_active=}\n"
                f"{product.category.pk=}\n"
                f"{'-' * 10}\n"
            )
