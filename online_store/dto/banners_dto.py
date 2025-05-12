from dataclasses import dataclass
from typing import List, Optional

from django.db.models.query import QuerySet
from django.db.models import Min

from banners.models.banner_product import BannerProduct
from banners.models.banner_category import BannerCategory


@dataclass
class BannerProductDTO:
    id: int
    image: str
    # url: str
    product_id: int
    product_title: str
    product_description: str
    short_description: str

    @classmethod
    def from_queryset(
        cls, queryset: QuerySet[Optional[BannerProduct]]
    ) -> List["BannerProductDTO"]:
        return [
            cls(
                id=b.id,
                image=b.image.url,
                # :TODO закоментировано, так как не определен абсолютный url в модели BannerProduct
                # url=b.get_absolute_url,
                product_id=b.product.id,
                product_title=b.product.title,
                product_description=b.product.description,
                short_description=b.product.short_description,
            )
            for b in queryset
        ]


@dataclass
class BannerCategoryDTO:
    id: int
    image: str
    # url: str
    category_id: int
    category_name: str
    min_product_price: Optional[float]

    @classmethod
    def from_queryset(
        cls, queryset: QuerySet[Optional[BannerCategory]]
    ) -> List["BannerCategoryDTO"]:
        result = []
        for b in queryset:
            min_price = b.category.products.aggregate(Min('price'))['price__min']

            result.append(
                cls(
                    id=b.id,
                    image=b.image.url,
                    # :TODO закоментировано, так как не определен абсолютный url в модели BannerCategory
                    # url=b.get_absolute_url,
                    category_id=b.category.id,
                    category_name=b.category.name,
                    min_product_price=min_price,
                )
            )
        return result
