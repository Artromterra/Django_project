
import random

from django.core.management.base import BaseCommand

from shop.factories.products_sellers import ProductSellerFactory
from shop.models.product import Product
from shop.models.seller import Seller


class Command(BaseCommand):
    help = "Create random ProductSeller instances."

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            required=False,
            help='Number random ProductSeller instances.'
        )

    def handle(self, *args, **options):
        count = options.get("count")

        products = Product.objects.all()
        if not products.exists():
            self.stderr.write(
                "There is not a single product in the database.\n"
                "To generate products, use the django command "
                "create_products --count=<number of product>"
            )
            return
        sellers = Seller.objects.all()
        if not sellers.exists():
            self.stderr.write(
                "There is not a single seller in the database.\n"
                "To generate categories, use the django command "
                "create_sellers --count=<number of sellers>"
            )
            return

        products_sellers = [
            (product, seller)
            for product in products
            for seller in sellers
        ]
        if count is None:
            count = len(products_sellers)
        for num in range(min(count, len(products_sellers))):
            random_product_seller = random.choice(products_sellers)
            products_sellers.remove(random_product_seller)
            product_seller = ProductSellerFactory.create(
                product=random_product_seller[0],
                seller=random_product_seller[1],
            )
            self.stdout.write(
                f"Create {num} ProductSeller instance:\n"
                f"{product_seller.pk=}\n"
                f"{product_seller.product=}\n"
                f"{product_seller.seller=}\n"
                f"{product_seller.price=}\n"
                f"{product_seller.amount=}\n"
                f"{'-' * 10}\n"
            )