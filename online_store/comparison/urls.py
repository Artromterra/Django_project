from django.urls import path
from .views import ComparisonView

urlpatterns = [
    path('comparison/', ComparisonView.as_view(), name='comparison_list'),
]