from django.core.management.base import BaseCommand

from profiles.factories import UserFactory


class Command(BaseCommand):
    help = "Create random users"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            required=True,
            help='Number random users.'
        )

    def handle(self, *args, **options):
        count = options['count']

        for num in range(count):
            user = UserFactory.create()
            self.stdout.write(
                f"Create {num} user:\n"
                f"f{user.pk=}\n"
                f"{user.username=}\n"
                f"{user.email=}\n"
                f"{user.password=}\n"
                f"{'-' * 10}\n"
            )