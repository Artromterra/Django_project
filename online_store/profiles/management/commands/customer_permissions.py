from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

from profiles.models import User

class Command(BaseCommand):
    help = 'Add permissions to customers'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int)

    def handle(self, *args, **options):
        user = User.objects.get(id=options['user_id'])
        group, created = Group.objects.get_or_create(name='Customer_permissions')
        permission_user = Permission.objects.get(codename='view_user')
        permission_category = Permission.objects.get(codename='view_category')
        permission_product = Permission.objects.get(codename='view_product')
        permission_productimage = Permission.objects.get(codename='view_productimage')

        group.permissions.add(permission_user)
        group.permissions.add(permission_category)
        group.permissions.add(permission_product)
        group.permissions.add(permission_productimage)
        user.groups.add(group)
        user.save()
        group.save()
        self.stdout.write(self.style.SUCCESS('Successfully added permissions'))
