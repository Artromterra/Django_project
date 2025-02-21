from dataclasses import dataclass
from typing import List, Optional

from django.db.models.query import QuerySet

from shop.models.product import ProductTag


@dataclass
class ProductTagDTO:
    id: int
    name: str
    product_id: int

    @classmethod
    def from_object(cls, object: ProductTag) -> "ProductTagDTO":
        if not object:
            return None
        return cls(
            id=object.pk,
            name=object.name,
            product_id=object.product_id,
        )

    @classmethod
    def from_objects(
        cls, queryset: QuerySet[Optional[ProductTag]]
    ) -> List["ProductTagDTO"]:
        return [cls.from_object(obj) for obj in queryset]
