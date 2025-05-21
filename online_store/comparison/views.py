from django.http import JsonResponse
from django.views.generic import View, ListView
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from comparison.models import ComparisonItem
from services.сomparison_service import ComparisonService

from django.utils.translation import gettext_lazy as _


class AddComparisonView(View):
    model = ComparisonItem

    def get(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        comparison_service = ComparisonService(request)
        comparison_service.add_product(product_id)
        return redirect('shop:products_list', pk=0)


class ComparisonView(ListView):
    model = ComparisonItem
    template_name = 'comparison.html'

    def get(self, request, **kwargs):
        comparison_service = ComparisonService(request)
        products = comparison_service.get_products()
        context = {
            'products': products,
        }
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super(ComparisonView, self).get_context_data(**kwargs)



class DeleteComparisonView(View):
    model = ComparisonItem

    def get(self, request, **kwargs):
        comparison_service = ComparisonService(request)
        product_id = self.kwargs.get('product_id')
        comparison_service.remove_product(product_id)
        return redirect('comparison:comparison_list')

