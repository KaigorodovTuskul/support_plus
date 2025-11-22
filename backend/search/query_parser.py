import os
import json
from mistralai import Mistral
from benefits.models import Benefit

# API key
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')

class QueryParser:
    """
    Parses natural language queries into structured search filters using Mistral LLM.
    """

    def __init__(self):
        self.client = Mistral(api_key=MISTRAL_API_KEY)
        
        # Extract beneficiary categories for the prompt
        self.beneficiary_map = {label.lower(): code for code, label in Benefit.BENEFICIARY_CATEGORIES}
        self.beneficiary_desc = ", ".join([f"'{label}' ({code})" for code, label in Benefit.BENEFICIARY_CATEGORIES])

    def parse(self, query: str, user_region: str = None) -> dict:
        """
        Parses the query using Mistral LLM to extract intent, keywords, and filters.
        """
        try:
            system_prompt = f"""You are a search query parser for a Russian social benefits portal.
Your goal is to extract structured data from the user's search query.

VALID BENEFICIARY CATEGORIES (target_groups):
{self.beneficiary_desc}

INSTRUCTIONS:
1. Analyze the user's query.
2. Extract keywords (list of strings).
3. Determine the intent: 'find_benefits' (default), 'find_commercial', or 'mixed'.
4. Extract filters:
    - 'target_groups': Map user terms (e.g., "пенсионеры", "инвалиды") to the EXACT codes listed above.
      Example: "льготы для пенсионеров" -> ["pensioner"]
      Example: "инвалид 1 группы" -> ["disability_1"]
      Example: "инвалиды" -> ["disability_1", "disability_2", "disability_3"] (if group not specified, include all relevant)
    - 'regions': List of region names if mentioned (e.g., "в Москве").
    - 'content_type': ["benefit"] or ["commercial"] or both.

OUTPUT FORMAT:
Return ONLY a valid JSON object. Do not include markdown formatting or explanations.
{{
    "intent": "find_benefits",
    "keywords": ["keyword1", "keyword2"],
    "filters": {{
        "content_type": ["benefit"],
        "target_groups": ["pensioner"],
        "regions": ["Москва"]
    }}
}}
"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]

            response = self.client.chat.complete(
                model="open-mistral-nemo",
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            parsed_data = json.loads(content)
            
            # Ensure required fields exist
            if 'filters' not in parsed_data:
                parsed_data['filters'] = {}
            
            # Add user region if not present and relevant
            if user_region and not parsed_data['filters'].get('regions'):
                # We don't automatically add user region to search filters unless we want strict filtering
                # But for now, let's leave it to the search engine to boost local results
                pass

            return parsed_data

        except Exception as e:
            print(f"Error parsing query with LLM: {e}")
            # Fallback to simple keyword parsing
            return self._fallback_parse(query)

    def _fallback_parse(self, query: str) -> dict:
        """Simple fallback parsing if LLM fails"""
        keywords = query.lower().split()
        filters = {
            'content_type': ['benefit', 'commercial'],
            'target_groups': [],
            'regions': []
        }
        
        # Simple keyword matching for categories
        for code, label in Benefit.BENEFICIARY_CATEGORIES:
            if label.lower() in query.lower() or code in query.lower():
                filters['target_groups'].append(code)
                
        # Handle generic "disabled" term
        if 'инвалид' in query.lower() and not filters['target_groups']:
             filters['target_groups'].extend(['disability_1', 'disability_2', 'disability_3'])

        return {
            'intent': 'mixed',
            'keywords': keywords[:10],
            'filters': filters
        }