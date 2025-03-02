from django.urls import path

from .views import (
    ComparisonAddView,
    ComparisonListView,
    ComparisonRemoveView,
    ComparisonView,
)


urlpatterns = [
    path('', ComparisonView.as_view(), name='comparison'),
    path('list/', ComparisonListView.as_view(), name='comparison_list'),
    path('add/', ComparisonAddView.as_view(), name='comparison_add'),
    path('remove/', ComparisonRemoveView.as_view(), name='comparison_remove'),
]