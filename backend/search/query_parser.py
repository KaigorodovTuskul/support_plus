# ЗАКОММЕНТИРОВАНО: Используем только облачные API через requests
# import openai
import json
from django.conf import settings


class QueryParser:
    """
    ЗАГЛУШКА: OpenAI парсер отключен для деплоя на VPS.
    Используйте простой парсинг или другие облачные API.
    """

    def __init__(self):
        # Заглушка - не используем OpenAI
        pass

    def parse(self, query: str, user_region: str = None) -> dict:
        """
        Returns:
        {
            "intent": "find_benefits" | "find_commercial" | "mixed",
            "keywords": ["льготы", "пенсионеры"],
            "filters": {
                "content_type": ["benefit", "commercial"],
                "target_groups": ["pensioner", "disabled"],
                "regions": [77, 78],  # Moscow, St. Petersburg codes
                "category_slugs": ["housing", "transport"]
            }
        }
        """

        # Простой fallback парсинг без OpenAI
        return {
            'intent': 'mixed',
            'keywords': query.split()[:10],
            'filters': {
                'content_type': ['benefit', 'commercial'],
                'target_groups': [],
                'regions': [],
                'category_slugs': []
            }
        }