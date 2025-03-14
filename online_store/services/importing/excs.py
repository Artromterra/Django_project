
from typing import Literal, Set, Optional


class NotFoundData(KeyError):
    """Exc is responsible for errors related to missing data for a specific table."""

    def __init__(
        self,
        model: Literal["Category", "Product", "Seller", "ProductSeller"],
        msg: Optional[str] = None,
    ):
        self.model = model
        self.msg = msg

    def __str__(self) -> str:
        exc_str = f"Not found data for {self.model}."
        if self.msg:
            exc_str = "\n".join((exc_str, self.msg))
        return exc_str


class NotFoundField(NotFoundData):
    """Exc is responsible for errors related to inconsistencies in field names."""

    def __init__(
        self,
        model: Literal["Category", "Product", "Seller", "ProductSeller"],
        fields: Set[str],
        msg: Optional[str] = None,
    ):
        super().__init__(model, msg)
        self.fields = fields

    def __str__(self):
        exc_str: str = f"Not found data for fields {self.fields} for model {self.model}."
        if self.msg:
            exc_str = "\n".join((exc_str, self.msg))
        return exc_str


class InvalidImportFileExtension(ValueError):
    """The exc responsible for errors related to incorrect import file extensions."""
    def __init__(self, extension: str, msg: Optional[str] = None):
        self.extension = extension
        self.msg = msg

    def __str__(self) -> str:
        exc_str: str = f"Can't import file with extension {self.extension}.\n{self.msg}"
        if self.msg:
            exc_str = "\n".join((exc_str, self.msg))
        return exc_str
