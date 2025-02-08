from services.category_menu import CategoryMenuService

def category_menu():
    """
    Context processor, который добавляет меню категорий в контекст всех шаблонов.
    """
    return {
        'category_menu': CategoryMenuService.get_cached_menu()
    }