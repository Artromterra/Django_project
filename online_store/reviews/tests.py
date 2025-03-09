import random
from typing import List
from logging import getLogger
from unicodedata import category

from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.db.models import Q
import factory

from profiles.models import User
from shop.models.reviews import Review
from shop.models.product import Product
from shop.models.category import Category
from shop.factories.reviews import ReviewFactory
from shop.factories.products import ProductFactory
from shop.factories.categories import CategoryFactory
from profiles.factories import UserFactory

logger = getLogger(__name__)


class ReviewsListViewTest(TestCase):
    """Test case class for testing ReviewsListView."""

    @classmethod
    def setUpClass(cls):
        """Set up class."""
        cls.user = UserFactory.create()

    @classmethod
    def tearDownClass(cls):
        """Tear down class."""
        cls.user.delete()

    def setUp(self):
        """Set up."""
        self.categories: List[Category] = [
            CategoryFactory.create() for _ in range(random.randint(1, 20))
        ]
        self.products: List[Product] = [
            ProductFactory.create(category=random.choice(self.categories))
            for _ in range(random.randint(1, 20))
        ]
        self.reviews: List[Review] = [
            ReviewFactory.create(
                author=self.user,
                product=random.choice(self.products)
            )
            for _ in range(random.randint(10, 100))
        ]

    def tearDown(self):
        """Tear down."""
        for category_ in self.categories:
            category_.delete()
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
                    .filter(product__pk=product.pk).order_by("-created_at").all()),
                values=(s.pk for s in response.context["reviews"]),
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
                values=(s.pk for s in response.context["reviews"]),
                transform=lambda review: review.pk,
            )

    def test_getting_random_num_reviews(self):
        """Test getting random num of reviews."""
        for product in self.products:
            random_limit: int = random.randint(0, 100)

            url = "?".join((
                reverse("reviews:reviews-list"),
                "&".join((
                    f"product_id={product.pk}",
                    f"limit={random_limit}"
                ))
            ))
            response = self.client.get(url)

            # num reviews less or equal random limit
            self.assertLessEqual(
                len(response.context["reviews"]),
                random_limit
            )

            self.assertQuerySetEqual(
                qs=(Review.objects.select_related("product")
                    .filter(product__pk=product.pk).order_by("-created_at")
                    .all()[:random_limit]),
                values=(s.pk for s in response.context["reviews"]),
                transform=lambda review: review.pk,
            )


class ReviewCreateViewTest(TestCase):
    """Test case class for testing ReviewsCreateView."""

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(
            username="test",
            password="test",
            email=factory.Faker("email").evaluate(None, None, {"locale": "en_US"})
        )
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        self.category = CategoryFactory.create()
        self.product = ProductFactory.create(category=self.category)
        self.review_data = ReviewFactory.build(
            author=self.user,
            product=self.product
        )
        # Check that the object is being created in the test
        self.qs = Review.objects.filter(
            Q(product=self.review_data.product) &
            Q(author=self.review_data.author) &
            Q(content=self.review_data.content) &
            Q(created_at=self.review_data.created_at)
        )
        self.qs.delete()
        self.review = None

    def tearDown(self):
        if self.category:
            self.category.delete()
        if self.product:
            self.product.delete()

    def test_create_review(self):
        """Test creating a new review."""
        url: str = "?".join((
            reverse("reviews:reviews-new"),
            f"product_id={self.product.pk}"
        ))
        self.client.post(
            url,
            {"content": self.review_data.content},
            follow=True,
        )

        self.assertTrue(self.qs.exists())
