from dataclasses import dataclass
from typing import List, Optional

from django.db.models.query import QuerySet

from shop.models.product import ProductFeature


@dataclass
class ProductFeatureDTO:
    id: int
    value: str
    product_id: int

    @classmethod
    def from_object(cls, object: ProductFeature) -> "ProductFeatureDTO":
        if not object:
            return None
        return cls(
            id=object.pk,
            value=object.value,
            product_id=object.product_id
        )

    @classmethod
    def from_objects(
        cls, queryset: QuerySet[Optional[ProductFeature]]
    ) -> List["ProductFeatureDTO"]:
        return [cls.from_object(obj) for obj in queryset]
