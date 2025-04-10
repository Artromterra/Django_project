'''Модуль для подготовки контента для глановй страницы'''

from dto.product_list_dto import ProductDTO


class HomepageContentService:

    def get_products(self) -> dict['str', list[ProductDTO]]:
        '''Возвращает продукты для отображения главной страницы'''
        pass

    def _get_popular_products(self) -> list[ProductDTO]:
        '''Возвращает 6 популярных продуктов'''
        pass

    def _get_limited_products(self) -> list[ProductDTO]:
        '''Возвращает 12 продуктов ограниченного тиража'''
        pass

    def _get_discount_produtcs(self) -> list[ProductDTO]:
        '''Возвращает 2 продукта с истекающей скидкой'''
        pass
