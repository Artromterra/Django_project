
from datetime import datetime

from django.views.generic import ListView, CreateView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from .models.feedbacks import Feedback


class FeedbacksListView(ListView):
    model = Feedback
    template_name = "feedback-list.html"
    context_object_name = "feedbacks"

    def get_queryset(self):
        limit = self.request.GET.get("limit", settings.DEFAULT_LIMIT_FEEDBACKS)
        product_id = self.request.GET.get("product_id")
        return (Feedback.objects.filter(Feedback.product.id == product_id)
                .select_related("User").order_by("-pub_date").all()[:limit])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.request.GET.get("product_id")
        context["num_feedbacks"] = Feedback.objects.filter(Feedback.product.id == product_id).count()
        return context


class FeedbackCreateView(LoginRequiredMixin, CreateView):
    model = Feedback
    fields = ["comment"]
    template_name = "feedback-create.html"
    context_object_name = "feedback"

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.pub_date = datetime.now()
        return super().form_valid(form)
