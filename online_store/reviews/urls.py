
from django.urls import path

from .views import FeedbacksListView, FeedbackCreateView

app_name = "feedbacks"

urlpatterns = [
    path("feedbacks/", FeedbacksListView.as_view(), name="feedbacks-list"),
    path("feedback/new/", FeedbackCreateView.as_view(), name="feedbacks-new"),
]
