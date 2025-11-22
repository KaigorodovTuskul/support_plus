import os
import django
import sys
from datetime import date, timedelta

# Setup Django environment
sys.path.append('/Users/koluj/Documents/study/approx/sem6/support_plus/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from benefits.models import Benefit, Category, Region
from search.models import SearchIndex
from django.contrib.contenttypes.models import ContentType

def populate():
    print("Populating database...")
    
    # Create Categories
    cat_pensioner, _ = Category.objects.get_or_create(name="Pensioner", slug="pensioner")
    cat_veteran, _ = Category.objects.get_or_create(name="Veteran", slug="veteran")
    
    # Create Regions
    reg_moscow, _ = Region.objects.get_or_create(name="Москва", code="77")
    reg_spb, _ = Region.objects.get_or_create(name="Санкт-Петербург", code="78")
    
    # Create Benefits
    benefits_data = [
        {
            "benefit_id": "ben_001",
            "title": "Бесплатный проезд для пенсионеров",
            "description": "Бесплатный проезд в общественном транспорте для пенсионеров Москвы.",
            "benefit_type": "regional",
            "status": "active",
            "valid_from": date.today(),
            "valid_to": date.today() + timedelta(days=365),
            "regions": [reg_moscow],
            "categories": [cat_pensioner]
        },
        {
            "benefit_id": "ben_002",
            "title": "Льготы по оплате ЖКХ",
            "description": "Скидка 50% на оплату жилищно-коммунальных услуг для ветеранов труда.",
            "benefit_type": "federal",
            "status": "active",
            "valid_from": date.today(),
            "valid_to": date.today() + timedelta(days=365),
            "regions": [reg_moscow, reg_spb],
            "categories": [cat_veteran]
        },
        {
            "benefit_id": "ben_003",
            "title": "Санаторно-курортное лечение",
            "description": "Бесплатные путевки в санатории для пенсионеров и инвалидов.",
            "benefit_type": "federal",
            "status": "active",
            "valid_from": date.today(),
            "valid_to": date.today() + timedelta(days=365),
            "regions": [reg_moscow, reg_spb],
            "categories": [cat_pensioner]
        }
    ]
    
    for data in benefits_data:
        regions = data.pop("regions")
        categories = data.pop("categories")
        benefit, created = Benefit.objects.get_or_create(benefit_id=data["benefit_id"], defaults=data)
        if created:
            benefit.regions.set(regions)
            benefit.categories.set(categories)
            print(f"Created benefit: {benefit.title}")
        else:
            print(f"Benefit already exists: {benefit.title}")

    print(f"Total benefits: {Benefit.objects.count()}")
    print(f"Total search index items: {SearchIndex.objects.count()}")

if __name__ == '__main__':
    populate()
