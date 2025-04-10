from django.views import View
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from services.banner_service import BannerService


class HomepageView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = request.user
        banner_service = BannerService(user)
        banners = banner_service.get_banners_to_homepage()
        context = {
            'banners': banners,
            'popular_products': None,
            'limited_products': None,
            'discount_produtcs': None,
        }
        return render(request=request, template_name='index.html', context=context)
