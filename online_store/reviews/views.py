"""The module responsible for views for reviews."""

from datetime import datetime
from logging import getLogger

from django.views.generic import ListView, CreateView
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from shop.models.reviews import Review
from shop.models.product import Product

logger = getLogger(__name__)


class ReviewsListView(ListView):
    """ListView for reviews."""

    model = Review
    template_name = "review-list.html"
    context_object_name = "reviews"

    def get_queryset(self):
        limit = self.request.GET.get("limit", settings.DEFAULT_LIMIT_REVIEWS)
        limit = int(limit)
        logger.debug("Limit is %d", limit)

        product_id = self.request.GET.get("product_id")
        logger.debug("Product pk is %d", product_id)
        return (Review.objects
                .select_related("product").filter(product__pk=product_id)
                .select_related("author").order_by("-created_at").all()[:limit])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.request.GET.get("product_id")
        context["num_reviews"] = Review.objects.filter(product__pk=product_id).count()
        logger.debug("Total num reviews: %d", context["num_reviews"])
        return context


class ReviewsCreateView(LoginRequiredMixin, CreateView):
    """CreateView for reviews."""

    model = Review
    fields = ["content"]
    template_name = "review-create.html"

    def form_valid(self, form):
        product_id = self.request.GET.get("product_id")
        logger.debug("Product pk is %d", product_id)

        form.instance.product = Product.objects.get(pk=product_id)
        form.instance.user = self.request.user
        form.instance.pub_date = datetime.now()
        return super().form_valid(form)
