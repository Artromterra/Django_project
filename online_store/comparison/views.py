from django.http import JsonResponse
from django.views import View
from services.сomparison_service import ComparisonService


class ComparisonView(View):
    def _get_service(self, request):
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        return ComparisonService(user=user, session_key=session_key)

    def post(self, request, *args, **kwargs):
        """
        Добавление товара в список сравнения
        """
        product_id = request.POST.get('product_id')
        if not product_id:
            return JsonResponse({'error': 'Требуется идентификатор продукта'}, status=400)

        service = self._get_service(request)
        added = service.add_product(product_id)
        if added:
            return JsonResponse({'message': 'Продукт добавлен в список сравнения'})
        return JsonResponse({'message': 'Продукт уже в списке сравнения'})

    def delete(self, request, *args, **kwargs):
        """
        Удаление товара из списка сравнения
        """
        product_id = request.GET.get('product_id')
        if not product_id:
            return JsonResponse({'error': 'Требуется идентификатор продукта'}, status=400)

        service = self._get_service(request)
        service.remove_product(product_id)
        return JsonResponse({'message': 'Продукт удален из списка сравнения'})

    def get(self, request, *args, **kwargs):
        """
        Получение списка товаров и их количества
        """
        limit = request.GET.get('limit', 3)
        service = self._get_service(request)

        try:
            limit = int(limit)
        except ValueError:
            return JsonResponse({'error': 'Предел должен быть целым числом'}, status=400)

        products = service.get_products(limit=limit)
        count = service.get_count()
        return JsonResponse({'products': products, 'count': count})