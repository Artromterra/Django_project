from abc import ABC, abstractmethod
from typing import Generator, Dict, Any
from logging import getLogger


class BaseImporter(ABC):
    """The base class responsible for importing entities from a file."""

    import_params: Dict[str, Dict[str, Any]] = {
        "Category": {
            "fields": frozenset({"pk", "name", "category_icon"}),
        },
        "Product": {
            "fields": frozenset({
                "pk",
                "title",
                "description",
                "short_description",
                "price",
                "is_active",
                "category",
            }),
        },
        "Seller": {
            "fields": frozenset({
                "pk",
                "user",
                "name",
                "description",
                "image",
                "phone",
                "address",
                "email",
            }),
        },
        "ProductSeller": {
            "fields": frozenset({
                "pk",
                "product",
                "seller",
                "price",
                "amount",
            }),
        }
    }

    def __init__(self, filename: str, logger_name: str = "main.services.importing.importers"):
        self.filename = filename
        self.logger = getLogger(logger_name)

    @abstractmethod
    def import_categories(self) -> Generator[Dict[str, Any], None, None]:
        """Import categories."""
        pass

    @abstractmethod
    def import_products(self) -> Generator[Dict[str, Any], None, None]:
        """Import products."""
        pass

    @abstractmethod
    def import_sellers(self) -> Generator[Dict[str, Any], None, None]:
        """Import sellers."""
        pass

    @abstractmethod
    def import_products_sellers(self) -> Generator[Dict[str, Any], None, None]:
        """Import ProductSeller instances."""
        pass
