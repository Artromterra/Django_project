from django.urls import path
from .views import ComparisonView, AddComparisonView, DeleteComparisonView

app_name = 'comparison'

urlpatterns = [
    path('add-product/<int:product_id>', AddComparisonView.as_view(), name='add_product'),
    path('product/', ComparisonView.as_view(), name='comparison_list'),
    path('delete-product/<int:product_id>', DeleteComparisonView.as_view(), name='delete_product'),
]