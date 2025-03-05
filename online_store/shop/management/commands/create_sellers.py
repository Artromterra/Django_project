
import random

from django.core.management.base import BaseCommand

from shop.factories.sellers import SellerFactory
from profiles.models import User


class Command(BaseCommand):
    help = "Create random sellers from existing users."

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            required=True,
            help='Number random sellers.'
        )

    def handle(self, *args, **options):
        count = options['count']

        users = User.objects.exclude(seller__isnull=False).all()
        if not users.exists():
            self.stderr.write(
                "There is not a single user in the database who is not a seller.\n"
                "To generate users, run the django command "
                "create_users --count=<number of users>"
            )
            return

        user_list = list(users)
        for num in range(min(count, len(users))):
            random_user = random.choice(user_list)
            user_list.remove(random_user)
            seller = SellerFactory.create(user=random_user)
            self.stdout.write(
                f"Create {num} seller:\n"
                f"{seller.pk=}\n"
                f"{seller.user.pk=}\n"
                f"{seller.name=}\n"
                f"{seller.phone=}\n"
                f"{seller.address=}\n"
                f"{seller.email=}\n"
                f"{'-' * 10}\n"
            )