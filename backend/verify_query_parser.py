import os
import sys
import json
from unittest.mock import MagicMock

# Mock Django and benefits.models
sys.modules['django'] = MagicMock()
sys.modules['django.conf'] = MagicMock()
sys.modules['benefits'] = MagicMock()
sys.modules['benefits.models'] = MagicMock()

# Mock Benefit class and BENEFICIARY_CATEGORIES
class MockBenefit:
    BENEFICIARY_CATEGORIES = [
        ('pensioner', 'Пенсионер'),
        ('disability_1', 'Инвалидность 1 группы'),
        ('disability_2', 'Инвалидность 2 группы'),
        ('disability_3', 'Инвалидность 3 группы'),
        ('large_family', 'Многодетная семья'),
        ('veteran', 'Ветеран'),
        ('low_income', 'Малоимущий'),
        ('svo_participant', 'Участник СВО'),
        ('svo_family', 'Семья участника СВО'),
    ]

sys.modules['benefits.models'].Benefit = MockBenefit

# Now import QueryParser
# We need to make sure we can import it even if django is not installed
# Since QueryParser imports Benefit from benefits.models, and we mocked it, it should be fine.
# But we also need to make sure mistralai is installed.

try:
    from search.query_parser import QueryParser
except ImportError as e:
    print(f"Failed to import QueryParser: {e}")
    print("Please ensure 'mistralai' is installed.")
    sys.exit(1)

def test_parser():
    try:
        parser = QueryParser()
    except Exception as e:
        print(f"Failed to instantiate QueryParser: {e}")
        return

    test_queries = [
        "льготы для пенсионеров в Москве",
        "какие выплаты положены инвалидам 1 группы",
        "скидки в аптеках для ветеранов",
        "льготы для многодетных семей",
        "проезд для инвалидов"
    ]
    
    print("Testing QueryParser with Mistral LLM...\n")
    
    for query in test_queries:
        print(f"Query: {query}")
        try:
            result = parser.parse(query)
            print(f"Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Basic validation
            filters = result.get('filters', {})
            target_groups = filters.get('target_groups', [])
            
            if "пенсионер" in query and "pensioner" not in target_groups:
                print("WARNING: Failed to map 'пенсионер'")
            if "инвалид" in query and not any(g.startswith('disability') for g in target_groups):
                print("WARNING: Failed to map 'инвалид'")
                
        except Exception as e:
            print(f"ERROR: {e}")
        print("-" * 50)

if __name__ == "__main__":
    test_parser()
