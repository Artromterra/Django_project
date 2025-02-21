from dataclasses import dataclass
from typing import List, Optional

from django.db.models.query import QuerySet

from shop.models.product import ProductImage


@dataclass
class ProductImageDTO:
    id: int
    description: str
    url: str

    @classmethod
    def from_object(cls, object: ProductImage) -> "ProductImageDTO":
        if not object:
            return None
        return cls(
            id=object.pk,
            description=object.description,
            url=object.image.url,
        )

    @classmethod
    def from_objects(
        cls, queryset: QuerySet[Optional[ProductImage]]
    ) -> List["ProductImageDTO"]:
        return [cls.from_object(obj) for obj in queryset]
