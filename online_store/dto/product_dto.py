from dataclasses import dataclass
from typing import List, Optional

from django.db.models.query import QuerySet

from shop.models.product import Product


@dataclass
class ProductDTO:
    id: int
    title: str
    description: str
    short_description: str
    price: float
    is_active: bool
    category_name: Optional[str] = None

    @classmethod
    def from_object(cls, object: Product) -> "ProductDTO":
        if not object:
            return None
        return cls(
            id=object.pk,
            title=object.title,
            description=object.description,
            short_description=object.short_description,
            price=object.price,
            is_active=object.price,
            category_name=(
                None if not object.category_id else object.category.name
            ),
        )

    @classmethod
    def from_objects(
        cls, queryset: QuerySet[Optional[Product]]
    ) -> List["ProductDTO"]:
        return [cls.from_object(obj) for obj in queryset]
