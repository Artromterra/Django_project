from django.core.management.base import BaseCommand

from shop.factories.products import ProductFactory


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

        for num in range(count):
            product = ProductFactory.create()
            self.stdout.write(
                f"Create {num} product:\n"
                f"f{product.pk=}\n"
                f"{product.title=}\n"
                f"{product.description=}\n"
                f"{product.short_description=}\n"
                f"{product.price=}\n"
                f"{product.is_active=}\n"
                f"{product.category.name}\n"
                f"{'-' * 10}\n"
            )
