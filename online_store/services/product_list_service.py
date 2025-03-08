from typing import List, Optional

from dto.product_list_dto import ProductListDTO


def sort_list_products_dto(
    products_list_dto: List[ProductListDTO], sort_query: Optional[str] = None
) -> List[ProductListDTO]:
    """Сортирует список продуктов"""
    if not sort_query:
        return products_list_dto

    reverse = sort_query.startswith("-")
    sort_query = sort_query.lstrip("-")

    products_list_dto.sort(
        key=lambda x: getattr(x, sort_query, 0), reverse=reverse
    )
    return products_list_dto
