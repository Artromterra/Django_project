from datetime import datetime
from typing import Optional

from viewed_products.models import ViewedProducts
from profiles.models import User
from shop.models.product import Product


class ViewHistoryProductsService:
    def __init__(self, user: User, product: Product):
        self.user = user
        self.product = product

    def add_viewed_products(self):
        """
        добавление просмотренных товаров текущим пользователем в БД
        :return: ViewedProducts
        """
        obj, created = ViewedProducts.objects.update_or_create(
            viewed_by_user=self.user,
            product=self.product,
            defaults={'viewed_at': datetime.now()},
        )

        return obj

    def remove_viewed_products(self):
        """
        удаление просмотренного продукта текущим пользователем из БД
        :return: None
        """
        obj = ViewedProducts.objects.filter(
            viewed_by_user=self.user,
            product=self.product,
        )
        if obj:
            obj.delete()

    def is_product_in_list(self):
        """
        проверка существования просмотренного продукта текущим пользователем в БД
        :return: Boolean
        """
        obj = ViewedProducts.objects.filter(
            viewed_by_user=self.user,
            product=self.product,
        ).first()
        if obj:
            return True
        return False

    def get_viewed_products(self, number_of_products: Optional[int] = None):
        """
        создание кверисета продуктов просмотренных текущим пользователем
        :param number_of_products: int параметр для вывода количества просмотренных товаров
        :return: QuerySet[ViewedProducts]
        """
        queryset = ViewedProducts.objects.filter(
            viewed_by_user=self.user,
        ).select_related(
            'viewed_by_user',
            'product',
        ).order_by('viewed_at')[:number_of_products]
        return queryset
