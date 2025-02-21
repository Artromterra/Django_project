from dataclasses import dataclass
from typing import List, Optional

from django.db.models.query import QuerySet

from shop.models.product_properties import ProductProperties


@dataclass
class ProductPropertiesDTO:
    id: int
    product_id: str
    property: str
    value: str
    title: Optional[str] = None

    @classmethod
    def from_object(cls, object: ProductProperties) -> "ProductPropertiesDTO":
        if not object:
            return None
        return cls(
            id=object.pk,
            product_id=object.product_id,
            property=object.property.name,
            value=object.value.value,
            title=object.title,
        )

    @classmethod
    def from_objects(
        cls, queryset: QuerySet[Optional[ProductProperties]]
    ) -> List["ProductPropertiesDTO"]:
        return [cls.from_object(obj) for obj in queryset]
