class SettingsService:
    @staticmethod
    def get_cache_timeout():
        """
        Возвращает время жизни кеша из сервиса настроек.
        """
        return 86400