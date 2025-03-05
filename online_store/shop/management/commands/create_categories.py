
from django.core.management.base import BaseCommand

from shop.factories.categories import CategoryFactory


class Command(BaseCommand):
    help = "Create random categories."

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            required=True,
            help='Number random categories.'
        )

    def handle(self, *args, **options):
        count = options['count']

        for num in range(count):
            category = CategoryFactory.create()
            self.stdout.write(
                f"Create {num} category:\n"
                f"{category.pk=}\n"
                f"{category.name=}\n"
                f"{category.description=}\n"
                f"{category.is_active=}\n"
                f"{'-' * 10}\n"
            )