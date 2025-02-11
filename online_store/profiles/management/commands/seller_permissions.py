from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

from profiles.models import User

class Command(BaseCommand):
    help = 'Add permissions to sellers'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int)

    def handle(self, *args, **options):
        codenames = [
            'view_category',
            'add_product',
            'change_product',
            'delete_product',
            'view_product',
            'add_productimage',
            'change_productimage',
            'delete_productimage',
            'view_productimage',
        ]
        user = User.objects.get(id=options['user_id'])
        group, created = Group.objects.get_or_create(name='Seller_permissions')
        permissions = Permission.objects.filter(
            content_type__app_label='shop',
            codename__in=codenames,
        )
        for permission in permissions:
            group.permissions.add(permission)
        user.groups.add(group)
        user.save()
        group.save()
        self.stdout.write(self.style.SUCCESS('Successfully added permissions'))
