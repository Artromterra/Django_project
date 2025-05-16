from django.shortcuts import render
from django.views.generic import ListView

from shop.models import Product
from dto.product_list_dto import ProductDTO


class SearchListView(ListView):
    template_name = 'search_products.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query')
        if query:
            products = Product.objects.filter(title__icontains=query)
            product_dto = ProductDTO.from_objects(products)
            return render(request, self.template_name, {'products': product_dto})
        return render(request, self.template_name)
