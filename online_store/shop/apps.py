from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"

    def ready(self):
        import signals.category_menu_signals
        import signals.product_signals
        import signals.product_feature_signals
        import signals.product_image_signals
        import signals.product_properties_signals
        import signals.product_tag_signals
