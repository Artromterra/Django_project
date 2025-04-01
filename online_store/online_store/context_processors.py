from services.category_menu import CategoryMenuService
from services.cart_service import CartService

def category_menu(request):
    """
    Context processor, который добавляет меню категорий в контекст всех шаблонов.
    """
    return {
        'category_menu': CategoryMenuService.get_cached_menu()
    }

def cart(request):
    """
    Context processor, который добавляет корзину в контекст всех шаблонов.
    """
    cart_service = CartService(request)
    cart_items = cart_service.get_cart_items()

    cart_total_price = sum(item.quantity * item.product.price for item in cart_items)
    cart_total_count = cart_service.get_cart_count()

    return {
        'cart_total_price': cart_total_price,
        'cart_total_count': cart_total_count
    }