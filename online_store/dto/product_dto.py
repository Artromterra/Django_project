from dataclasses import dataclass
from typing import List, Optional

from django.db.models.query import QuerySet

from shop.models.product import Product
from dto.product_features_dto import ProductFeatureDTO
from dto.product_image_dto import ProductImageDTO
from dto.product_properties_dto import ProductPropertiesDTO
from dto.product_tag_dto import ProductTagDTO


@dataclass
class ProductDetailDTO:
    id: int
    title: str
    description: str
    short_description: str
    price: float
    is_active: bool
    features: List[Optional[ProductFeatureDTO]]
    images: List[Optional[ProductImageDTO]]
    properties: List[Optional[ProductPropertiesDTO]]
    tags: List[Optional[ProductTagDTO]]
    category_name: Optional[str] = None

    @classmethod
    def from_object(cls, object: Product) -> "ProductDetailDTO":
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
            features=ProductFeatureDTO.from_objects(object.features),
            images=ProductImageDTO.from_objects(object.images),
            properties=ProductPropertiesDTO.from_objects(object.properties),
            tags=ProductTagDTO.from_objects(object.tags),
        )

    @classmethod
    def from_objects(
        cls, queryset: QuerySet[Optional[Product]]
    ) -> List["ProductDetailDTO"]:
        return [cls.from_object(obj) for obj in queryset]
