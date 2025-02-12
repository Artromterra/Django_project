from django.shortcuts import render
from services.banner_service import BannerService
from django.views import View


class HomepageView(View):
    def get(self, request):
        user = request.user
        banner_service = BannerService(user)
        banners = banner_service.get_banners_to_homepage()
        return render(request, 'index.html', {'banners': banners})