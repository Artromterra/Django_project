from dataclasses import dataclass
from typing import List, Optional

from django.db.models.query import QuerySet

from banners.models import BannerProduct, BannerCategory


@dataclass
class BannerProductDTO:
    id: int
    image: str
    product_id: int
    product_title: str

    @classmethod
    def from_queryset(
        cls, queryset: QuerySet[Optional[BannerProduct]]
    ) -> List["BannerProductDTO"]:
        return [
            cls(
                id=b.id,
                image=b.image.url,
                product_id=b.product.id,
                product_title=b.product.title,
            )
            for b in queryset
        ]


@dataclass
class BannerCategoryDTO:
    id: int
    image: str
    category_id: int
    category_name: str

    @classmethod
    def from_queryset(
        cls, queryset: QuerySet[Optional[BannerCategory]]
    ) -> List["BannerCategoryDTO"]:
        return [
            cls(
                id=b.id,
                image=b.image.url,
                category_id=b.category.id,
                category_name=b.category.name,
            )
            for b in queryset
        ]
