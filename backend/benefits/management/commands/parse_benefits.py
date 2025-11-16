import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from benefits.models import Benefit, Category, Region
import re


class Command(BaseCommand):
    help = 'Parse benefits from sfr.gov.ru websites'

    URLS = [
        'https://sfr.gov.ru/grazhdanam/pensionres/',
        'https://sfr.gov.ru/grazhdanam/semyam_s_detmi/',
        'https://sfr.gov.ru/grazhdanam/invalidam/',
        'https://sfr.gov.ru/grazhdanam/Informaciya_dlya_uchastnikov_SVO_i_ih_semei/',
        'https://sfr.gov.ru/grazhdanam/victims_of_industrial_accidents/',
        'https://sfr.gov.ru/grazhdanam/newregion/',
        'https://sfr.gov.ru/grazhdanam/pensionres/pens_sssr/',
        'https://sfr.gov.ru/grazhdanam/pensionres/pens_zagran/',
        'https://sfr.gov.ru/grazhdanam/workers/',
        'https://sfr.gov.ru/grazhdanam/eln/',
        'https://sfr.gov.ru/grazhdanam/social_support/',
        'https://sfr.gov.ru/grazhdanam/cosp/',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Test parsing without saving to database',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of URLs to parse (for testing)',
        )

    def handle(self, *args, **options):
        self.dry_run = options.get('dry_run', False)
        limit = options.get('limit')

        if self.dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be saved'))

        self.stdout.write('Starting benefit parsing...')

        # Ensure regions exist
        if not self.dry_run:
            self.create_initial_regions()
            self.create_initial_categories()

        # Parse each URL
        urls_to_parse = self.URLS[:limit] if limit else self.URLS
        for url in urls_to_parse:
            try:
                self.stdout.write(f'Parsing: {url}')
                self.parse_url(url)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error parsing {url}: {str(e)}'))

        # Create mock commercial offers
        if not self.dry_run:
            self.create_mock_commercial_offers()

        if self.dry_run:
            self.stdout.write(self.style.SUCCESS('Parsing test completed! (No data saved)'))
        else:
            self.stdout.write(self.style.SUCCESS('Parsing completed!'))

    def create_initial_regions(self):
        """Create initial Russian regions"""
        regions_data = [
            ('14', 'Республика Саха (Якутия)'),
            ('77', 'Москва'),
            ('78', 'Санкт-Петербург'),
            ('01', 'Республика Адыгея'),
            ('50', 'Московская область'),
        ]

        for code, name in regions_data:
            Region.objects.get_or_create(code=code, defaults={'name': name})

        self.stdout.write(self.style.SUCCESS('Regions created'))

    def create_initial_categories(self):
        """Create initial benefit categories"""
        categories_data = [
            ('transport', 'Транспорт', 'bus'),
            ('medicine', 'Медицина и лекарства', 'medical'),
            ('utilities', 'Коммунальные услуги', 'home'),
            ('education', 'Образование', 'education'),
            ('social_payments', 'Социальные выплаты', 'money'),
            ('housing', 'Жилищные льготы', 'house'),
            ('tax', 'Налоговые льготы', 'receipt'),
        ]

        for slug, name, icon in categories_data:
            Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon}
            )

        self.stdout.write(self.style.SUCCESS('Categories created'))

    def parse_url(self, url):
        """Parse a single URL and extract benefits"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Extract benefits based on page structure
            # This is a simplified parser - adjust selectors based on actual HTML structure
            benefits = self.extract_benefits_from_page(soup, url)

            for benefit_data in benefits:
                self.save_benefit(benefit_data)

        except requests.RequestException as e:
            self.stdout.write(self.style.WARNING(f'Request failed for {url}: {str(e)}'))

    def extract_benefits_from_page(self, soup, source_url):
        """Extract benefit information from parsed HTML"""
        benefits = []

        # Determine beneficiary category from URL
        target_groups = self.determine_target_groups(source_url)

        # Try multiple strategies to find content
        # Strategy 1: Look for article/content containers
        content_sections = soup.find_all(['article', 'section', 'div'],
                                        class_=re.compile(r'content|article|news|info|item|card|block'))

        # Strategy 2: Look for main content area
        main_content = soup.find(['main', 'div'], id=re.compile(r'content|main'))
        if main_content:
            content_sections.extend(main_content.find_all(['div', 'section'], recursive=False))

        # Strategy 3: Look for accordion/expandable sections
        accordions = soup.find_all(['div', 'section'], class_=re.compile(r'accordion|toggle|collapse'))
        content_sections.extend(accordions)

        # Remove duplicates
        content_sections = list(set(content_sections))

        if not content_sections:
            # Fallback: create generic benefit from the page
            title = soup.find('h1')
            if title:
                benefit = {
                    'title': title.get_text(strip=True),
                    'description': self.extract_description(soup),
                    'target_groups': target_groups,
                    'source_url': source_url,
                }
                benefits.append(benefit)
                self.stdout.write(f'  Found 1 benefit (fallback): {title.get_text(strip=True)[:50]}...')
        else:
            # Extract multiple benefits from sections
            count = 0
            for section in content_sections[:10]:  # Limit to first 10 sections
                title_elem = section.find(['h2', 'h3', 'h4', 'strong'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    # Filter out navigation, menu items, and too-short titles
                    if len(title) > 15 and not any(skip in title.lower() for skip in ['меню', 'навигация', 'поиск', 'вход']):
                        description = self.extract_text(section)
                        if len(description) > 50:  # Ensure meaningful content
                            benefit = {
                                'title': title[:200],  # Limit title length
                                'description': description,
                                'target_groups': target_groups,
                                'source_url': source_url,
                            }
                            benefits.append(benefit)
                            count += 1

            self.stdout.write(f'  Found {count} benefits from sections')

        return benefits

    def determine_target_groups(self, url):
        """Determine target beneficiary groups from URL"""
        if 'pensionres' in url:
            return ['pensioner']
        elif 'semyam_s_detmi' in url:
            return ['large_family']
        elif 'invalidam' in url:
            return ['disability_1', 'disability_2', 'disability_3']
        elif 'SVO' in url or 'svo' in url.lower():
            return ['svo_participant', 'svo_family']
        elif 'victims' in url:
            return ['disability_1', 'disability_2']
        else:
            return ['pensioner']  # Default

    def extract_description(self, soup):
        """Extract description text from page"""
        # Try to find main content
        content = soup.find(['div', 'section'], class_=re.compile(r'content|main|article'))
        if content:
            paragraphs = content.find_all('p', limit=3)
            text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            return text[:500] if text else 'Подробности на официальном сайте'
        return 'Подробности на официальном сайте'

    def extract_text(self, element):
        """Extract text from an element"""
        paragraphs = element.find_all('p', limit=2)
        if paragraphs:
            text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            return text[:500] if text else 'Подробности на официальном сайте'
        return element.get_text(strip=True)[:500]

    def save_benefit(self, benefit_data):
        """Save or update a benefit in the database"""
        # Generate unique benefit ID
        title_slug = re.sub(r'[^\w\s-]', '', benefit_data['title']).strip().lower()
        title_slug = re.sub(r'[-\s]+', '-', title_slug)[:50]
        benefit_id = f"sfr-{title_slug}"

        if self.dry_run:
            self.stdout.write(f'[DRY RUN] Would create: {benefit_id} - {benefit_data["title"][:60]}...')
            return

        # Check if benefit already exists
        if Benefit.objects.filter(benefit_id=benefit_id).exists():
            self.stdout.write(f'Benefit already exists: {benefit_id}')
            return

        # Create benefit
        benefit = Benefit.objects.create(
            benefit_id=benefit_id,
            title=benefit_data['title'],
            description=benefit_data['description'],
            benefit_type='federal',
            target_groups=benefit_data['target_groups'],
            applies_to_all_regions=True,
            valid_from=timezone.now().date(),
            valid_to=timezone.now().date() + timedelta(days=365),
            status='active',
            requirements='Предоставить документы, подтверждающие статус льготника',
            how_to_get='Обратиться в отделение СФР с необходимыми документами',
            documents_needed=['Паспорт', 'Удостоверение льготника', 'СНИЛС'],
            source_url=benefit_data['source_url'],
        )

        # Add categories
        self.add_categories_to_benefit(benefit, benefit_data['title'])

        self.stdout.write(self.style.SUCCESS(f'Created benefit: {benefit_id}'))

    def add_categories_to_benefit(self, benefit, title):
        """Add appropriate categories to a benefit based on keywords"""
        title_lower = title.lower()

        category_keywords = {
            'transport': ['транспорт', 'проезд', 'автобус', 'метро'],
            'medicine': ['медицин', 'лекарств', 'здоровь', 'лечение'],
            'utilities': ['коммунальн', 'жкх', 'оплата', 'услуг'],
            'education': ['образован', 'обучен', 'школ', 'универси'],
            'social_payments': ['выплат', 'пособи', 'компенсац', 'деньги'],
            'housing': ['жилищ', 'жилье', 'квартир', 'дом'],
            'tax': ['налог', 'освобожден'],
        }

        for slug, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                try:
                    category = Category.objects.get(slug=slug)
                    benefit.categories.add(category)
                except Category.DoesNotExist:
                    pass

    def create_mock_commercial_offers(self):
        """Create mock commercial partner offers"""
        from benefits.models import CommercialOffer

        offers_data = [
            {
                'offer_id': 'pharmacy-001',
                'title': 'Скидка 10% на лекарства для пенсионеров',
                'description': 'Постоянная скидка 10% на все рецептурные и безрецептурные препараты',
                'discount_description': 'Скидка 10%',
                'partner_name': 'Аптека "Здоровье+"',
                'partner_category': 'Аптека',
                'target_groups': ['pensioner', 'disability_1', 'disability_2', 'disability_3'],
                'how_to_use': 'Предъявите пенсионное удостоверение при покупке',
            },
            {
                'offer_id': 'grocery-001',
                'title': 'Скидка 5% в сети продуктовых магазинов',
                'description': 'Скидка на всю продукцию для льготных категорий граждан',
                'discount_description': 'Скидка 5%',
                'partner_name': 'Магазин "Продукты"',
                'partner_category': 'Продуктовый магазин',
                'target_groups': ['pensioner', 'large_family', 'low_income'],
                'how_to_use': 'Оформите карту постоянного покупателя на кассе',
            },
            {
                'offer_id': 'utility-001',
                'title': 'Льготная установка счетчиков воды',
                'description': 'Бесплатная установка и обслуживание счетчиков воды для льготников',
                'discount_description': 'Бесплатная установка',
                'partner_name': 'ЖКХ Сервис',
                'partner_category': 'Коммунальные услуги',
                'target_groups': ['pensioner', 'disability_1', 'disability_2'],
                'how_to_use': 'Позвоните по телефону и закажите выезд мастера',
            },
        ]

        region_yakutsk = Region.objects.filter(code='14').first()

        for data in offers_data:
            offer_id = data.pop('offer_id')
            if not CommercialOffer.objects.filter(offer_id=offer_id).exists():
                offer = CommercialOffer.objects.create(
                    offer_id=offer_id,
                    valid_from=timezone.now().date(),
                    valid_to=timezone.now().date() + timedelta(days=180),
                    status='active',
                    applies_to_all_regions=False,
                    **data
                )
                if region_yakutsk:
                    offer.regions.add(region_yakutsk)
                self.stdout.write(self.style.SUCCESS(f'Created offer: {offer_id}'))
