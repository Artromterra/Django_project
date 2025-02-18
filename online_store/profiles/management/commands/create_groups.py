from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Create permission groups'

    def handle(self, *args, **options):
        seller_codenames = [
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
        customer_codenames = [
            'view_user',
            'view_category',
            'view_product',
            'view_productimage',
        ]
        group_seller, created = Group.objects.get_or_create(
            name='Seller_permissions_group'
        )
        group_customer, created = Group.objects.get_or_create(
            name='Customer_permissions_group'
        )

        permissions_seller = Permission.objects.filter(
            content_type__app_label='shop',
            codename__in=seller_codenames,
        )
        permissions_customer = Permission.objects.filter(
            codename__in=customer_codenames,
        )
        for permission in permissions_seller:
            group_seller.permissions.add(permission)

        for permission in permissions_customer:
            group_customer.permissions.add(permission)

        group_customer.save()
        group_seller.save()
        self.stdout.write(self.style.SUCCESS('Successfully added permissions'))
