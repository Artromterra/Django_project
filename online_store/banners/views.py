from django.views import View
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse

from services.banner_service import BannerService
from services.homepage_content_service import HomepageContentService


class HomepageView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        user = request.user
        banner_service = BannerService(user)
        product_service = HomepageContentService()
        banners = banner_service.get_banners_to_homepage()
        products = product_service.get_contex_products()
        context = {
            'banners': banners,
            **products
        }
        return render(request=request, template_name='index.html', context=context)
