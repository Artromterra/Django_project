
from django.urls import path

from .views import ReviewsListView, ReviewsCreateView

app_name = "reviews"

urlpatterns = [
    path("reviews/", ReviewsListView.as_view(), name="reviews-list"),
    path("reviews/new/", ReviewsCreateView.as_view(), name="reviews-new"),
]
