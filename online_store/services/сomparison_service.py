from comparison.models import ComparisonItem
from dto.product_list_dto import ProductDTO


class ComparisonService:
    def __init__(self, request):
        self.request = request

    def _get_queryset(self, product_id):
        user = self.request.user.id
        session_key = self.request.session.session_key
        if user:
            queryset = ComparisonItem.objects.filter(user=user, product_id=product_id)
        else:
            queryset = ComparisonItem.objects.filter(session_key=session_key, product_id=product_id)
        return queryset

    def _get_user(self):
        user = self.request.user.id
        if user:
            return True
        return False

    def add_product(self, product_id):
        """
        Добавляет товар в список сравнения, если его там нет
        """
        if not self._get_queryset(product_id).exists():
            if self._get_user() is True:
                ComparisonItem.objects.create(
                    user=self.request.user,
                    product_id=product_id,
                )
            else:
                ComparisonItem.objects.create(
                    session_key=self.request.session.session_key,
                    product_id=product_id,
                )

    def remove_product(self, product_id):
        """
        Удаляет товар из списка сравнения
        """
        if self._get_user():
            ComparisonItem.objects.filter(
                user_id=self.request.user.id,
                product_id=product_id,
            ).delete()
        else:
            ComparisonItem.objects.filter(
                session_key=self.request.session.session_key,
                product_id=product_id,
            ).delete()

    def get_products(self, limit=2):
        """
        Возвращает список товаров, добавленных к сравнению
        """
        if self._get_user():
            queryset = ComparisonItem.objects.filter(
                user=self.request.user.id,
            ).select_related('product').all()[:limit]
        else:
            queryset = ComparisonItem.objects.filter(
                session_key=self.request.session.session_key,
            ).select_related('product').all()[:limit]
        return queryset

    def get_count(self):
        """
        Возвращает количество товаров в списке сравнения
        """
        if self._get_user():
            count =  ComparisonItem.objects.filter(
                user=self.request.user.id,
            ).count()
        else:
            count = ComparisonItem.objects.filter(
                session_key=self.request.session.session_key,
            ).count()
        return count
