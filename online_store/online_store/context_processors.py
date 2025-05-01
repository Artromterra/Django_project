from services.category_menu import CategoryMenuService
from services.cart_service import CartService
from services.сomparison_service import ComparisonService
# from services.discount_service import DiscountService


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
    # cart_items = cart_service.get_cart_items()
    cart_total_price = cart_service.get_cart_total_price()
    # for item in cart_items:
    #     discount_service = DiscountService(product=item.product)
    #     cart_total_price += item.quantity * discount_service.one_product_discount_price()
    # cart_total_price = sum(item.quantity * item.product.price for item in cart_items)
    cart_total_count = cart_service.get_cart_count()

    return {
        'cart_total_price': cart_total_price,
        'cart_total_count': cart_total_count
    }

def comparison(request):
    """
    Context processor, который добавляет количество сравниваемых товаров  в контекст всех шаблонов.
    """
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key if not user else None
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    comparison_service = ComparisonService(user=user, session_key=session_key)

    comparison_count = comparison_service.get_count()

    return {
        'comparison_count': comparison_count
    }