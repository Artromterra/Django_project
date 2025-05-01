from dataclasses import dataclass
from typing import List, Optional

from django.db.models.query import QuerySet

from shop.models.product import Product


@dataclass
class ProductDTO:
    id: int
    title: str
    price: float
    categories: str
    image_url: Optional[str] = None

    @classmethod
    def from_object(cls, object: Product) -> "ProductDTO":
        if not object:
            return None
        return cls(
            id=object.pk,
            title=object.title,
            price=object.price,
            categories=cls.get_categories(object),
            image_url=(
                object.images.first().image.url  # type: ignore
                if object.images.exists()
                else None
            ),
        )

    @classmethod
    def from_objects(
        cls, queryset: QuerySet[Product]
    ) -> List["ProductDTO"]:
        return [cls.from_object(obj) for obj in queryset]

    @classmethod
    def get_categories(cls, object: Product) -> str:
        """Категории в формате 'категория / категория / категория'"""
        end_category = object.category
        categories_list = [end_category.name]

        while end_category.parent_category:
            end_category = end_category.parent_category
            categories_list.append(end_category.name)

        categories_list.reverse()
        return " / ".join(categories_list)
