from django.views.generic import TemplateView, FormView, View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Comparison
from shop.models import Product
from .forms import ComparisonForm
from django.contrib.auth.mixins import LoginRequiredMixin


class ComparisonView(LoginRequiredMixin, TemplateView):
    "Отвечает за отображение страницы сравнения товаров для пользователя."

    template_name = "templates/comparison.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comparisons'] = self.get_user_comparisons()
        context['comparison_count'] = self.get_comparison_count()
        return context

    def get_user_comparisons(self):
        return Comparison.objects.filter(user_comparison=self.request.user)

    def get_comparison_count(self):
        return self.get_user_comparisons().count()


class ComparisonListView(LoginRequiredMixin, View):
    "Возвращает список товаров для сравнения текущего пользователя в формате JSON."

    def get(self, request, *args, **kwargs):
        try:
            limit = int(request.GET.get('count', 3))
            if limit <= 0:
                limit = 3
            elif limit > 100:
                limit = 100
        except ValueError:
            limit = 3

        comparisons = Comparison.objects.filter(user_comparison=request.user).order_by('id')

        comparisons_limited = comparisons[:limit]
        result = [
            {
                'id': item.product_comparison.id,
                'name': item.product_comparison.title,
                'price': item.product_comparison.price,

            } for item in comparisons_limited
        ]

        return JsonResponse({'status': 'success', 'comparisons': result})


class ComparisonAddView(LoginRequiredMixin, FormView):
    "Добавляет товар в список сравнения текущего пользователя."

    form_class = ComparisonForm

    def form_valid(self, form):
        product_id = form.cleaned_data['product_id']
        product = get_object_or_404(Product, id=product_id)

        if not Comparison.objects.filter(user_comparison=self.request.user, product_comparison=product).exists():
            Comparison.objects.create(user_comparison=self.request.user, product_comparison=product)

            return JsonResponse({'status': 'success', 'message': 'Товар добавлен в список сравнения.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Товар уже в списке сравнения.'})

    def form_invalid(self, form):
        return JsonResponse({'status': 'error', 'message': 'Некорректные данные.'})


class ComparisonRemoveView(LoginRequiredMixin, FormView):
    "Удаляет товар из списка сравнения текущего пользователя."

    form_class = ComparisonForm

    def form_valid(self, form):
        product_id = form.cleaned_data['product_id']
        product = get_object_or_404(Product, id=product_id)

        comparison = Comparison.objects.filter(user_comparison=self.request.user, product_comparison=product)
        if comparison.exists():
            comparison.delete()
            return JsonResponse({'status': 'success', 'message': 'Товар удален из списка сравнения.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Товар не найден в списке сравнения.'})

    def form_invalid(self, form):
        return JsonResponse({'status': 'error', 'message': 'Некорректные данные.'})