from dataclasses import dataclass
from typing import List, Optional

from django.db.models.query import QuerySet

from shop.models.properties import ProductProperties


@dataclass
class ProductPropertiesDTO:
    id: int
    title: str
    product_id: str
    value: Optional[str] = None

    @classmethod
    def from_object(cls, object: ProductProperties) -> "ProductPropertiesDTO":
        if not object:
            return None
        return cls(
            id=object.pk,
            title=object.title,
            product_id=object.product_id,
            value=None if not object.values_id else object.values.value
        )

    @classmethod
    def from_objects(
        cls, queryset: QuerySet[Optional[ProductProperties]]
    ) -> List["ProductPropertiesDTO"]:
        return [cls.from_object(obj) for obj in queryset]
