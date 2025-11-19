import openai
import json
from django.conf import settings


class QueryParser:
    """Parse natural language to structured query using OpenAI"""

    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

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

        system_prompt = """
        Parse Russian natural language queries for a social benefits portal.

        Available content types:
        - benefit: Government benefits (льготы, пособия, компенсации)
        - commercial: Partner discounts and offers (скидки, акции)

        Target group identifiers: pensioner, disability_1/2/3, large_family, veteran, low_income, svo_participant, svo_family

        Return JSON with:
        - intent: "find_benefits" | "find_commercial" | "mixed"
        - keywords: array of search terms
        - filters: {content_type, target_groups, regions, category_slugs}
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""
                    Query: "{query}"
                    User region: {user_region or 'Unknown'}
                    Parse into structured format.
                    """}
                ],
                temperature=0.1,
                max_tokens=400
            )

            content = response.choices[0].message.content.strip()
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0]
            elif '```' in content:
                content = content.split('```')[1].split('```')[0]

            parsed = json.loads(content)

            # Validate and normalize
            return {
                'intent': parsed.get('intent', 'mixed'),
                'keywords': parsed.get('keywords', query.split()[:10]),
                'filters': {
                    'content_type': parsed.get('filters', {}).get('content_type', ['benefit', 'commercial']),
                    'target_groups': parsed.get('filters', {}).get('target_groups', []),
                    'regions': parsed.get('filters', {}).get('regions', []),
                    'category_slugs': parsed.get('filters', {}).get('category_slugs', [])
                }
            }

        except Exception as e:
            # Fallback parsing
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