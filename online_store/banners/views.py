from django.shortcuts import render
from services.banner_service import BannerService


def homepage(request):
    user = request.user
    banner_service = BannerService(user)
    banners = banner_service.get_banners_to_homepage()

    return render(request, 'index.html', {'banners': banners})