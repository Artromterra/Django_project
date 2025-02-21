import random
from typing import List

from django.test import TestCase
from django.urls import reverse
from django.conf import settings
import factory

from profiles.models import User
from shop.models.reviews import Review
from shop.models.product import Product
from shop.factories.reviews import ReviewFactory
from shop.factories.products import ProductFactory


class ReviewsListViewTest(TestCase):
    """Test case class for testing ReviewsListView."""

    @classmethod
    def setUpClass(cls):
        """Set up class."""
        cls.credentials = dict(
            username="test",
            password="test",
            email=factory.Faker("email").evaluate(None, None, {"locale": "en_US"})
        )
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        """Tear down class."""
        cls.user.delete()

    def setUp(self):
        """Set up."""
        self.products: List[Product] = [
            ProductFactory.create() for _ in range(random.randint(1, 10))
        ]
        self.reviews: List[Review] = [
            ReviewFactory.create(
                author=self.user,
                product=random.choice(self.products)
            )
            for _ in range(random.randint(10, 20))
        ]

    def tearDown(self):
        """Tear down."""
        for product in self.products:
            product.delete()
        # the reviews are deleted in a cascade

    def test_getting_num_reviews(self):
        """Test getting total count of reviews."""
        for product in self.products:
            # check num_reviews from context
            url = "?".join((
                reverse("reviews:reviews-list"),
                f"product_id={product.pk}"
            ))
            response = self.client.get(url)
            self.assertEqual(
                response.context["num_reviews"],
                Review.objects.select_related("product")
                .filter(product__pk=product.pk).count()
            )

    def test_getting_list_all_reviews(self):
        """Test getting list of reviews with max limit."""
        for product in self.products:
            url = "?".join((
                reverse("reviews:reviews-list"),
                "&".join((
                    f"product_id={product.pk}",
                    f"limit={len(self.reviews)}"
                ))
            ))
            response = self.client.get(url)

            self.assertQuerySetEqual(
                qs=(Review.objects.select_related("product")
                    .filter(product__pk=product.pk).order_by("pk").all()),
                values=sorted((s.pk for s in response.context["reviews"])),
                transform=lambda review: review.pk,
            )

    def test_getting_default_num_reviews(self):
        """Test getting default num of reviews."""
        for product in self.products:
            url = "?".join((
                reverse("reviews:reviews-list"),
                f"product_id={product.pk}"
            ))
            response = self.client.get(url)

            # num reviews less or equal default limit
            self.assertLessEqual(
                len(response.context["reviews"]),
                settings.DEFAULT_LIMIT_REVIEWS
            )

            self.assertQuerySetEqual(
                qs=(Review.objects.select_related("product")
                    .filter(product__pk=product.pk).order_by("-created_at")
                    .all()[:settings.DEFAULT_LIMIT_REVIEWS]),
                values=sorted((s.pk for s in response.context["reviews"]), reverse=True),
                transform=lambda review: review.pk,
            )
