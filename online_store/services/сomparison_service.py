from comparison.models import ComparisonItem


class ComparisonService:
    def __init__(self, user=None, session_key=None):
        """
        Конструктор принимает либо user, либо session_key
        """
        # FIXME: При первом заходе на сайт после запуска вызывается это исключение.
        #  После того как закомментировал это условие и запустил сайт, ошибка пропала,
        #  и можно было обратно раскомментировать. Необходимо разобраться
        if not user and not session_key:
            raise ValueError("Either user or session_key must be provided.")
        self.user = user
        self.session_key = session_key

    def add_product(self, product_id):
        """
        Добавляет товар в список сравнения, если его там нет
        """
        if not self._is_product_in_list(product_id):
            ComparisonItem.objects.create(
                user=self.user,
                session_key=self.session_key,
                product_id=product_id
            )
            return True
        return False

    def remove_product(self, product_id):
        """
        Удаляет товар из списка сравнения
        """
        ComparisonItem.objects.filter(
            user=self.user,
            session_key=self.session_key,
            product_id=product_id
        ).delete()

    def get_products(self, limit=3):
        """
        Возвращает список товаров, добавленных к сравнению
        """
        queryset = ComparisonItem.objects.filter(
            user=self.user,
            session_key=self.session_key
        )[:limit]
        return [item.product_id for item in queryset]

    def get_count(self):
        """
        Возвращает количество товаров в списке сравнения
        """
        return ComparisonItem.objects.filter(
            user=self.user,
            session_key=self.session_key
        ).count()

    def _is_product_in_list(self, product_id):
        """
        Проверяет, есть ли товар в списке сравнения
        """
        return ComparisonItem.objects.filter(
            user=self.user,
            session_key=self.session_key,
            product_id=product_id
        ).exists()