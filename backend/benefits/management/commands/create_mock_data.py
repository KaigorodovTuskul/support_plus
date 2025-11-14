from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from benefits.models import Benefit, CommercialOffer, Category, Region


class Command(BaseCommand):
    help = 'Create mock benefits and offers data'

    def handle(self, *args, **options):
        self.stdout.write('Creating mock data...')

        # Create regions
        regions = {
            'yakutsk': Region.objects.get_or_create(code='14', defaults={'name': 'Республика Саха (Якутия)'})[0],
            'moscow': Region.objects.get_or_create(code='77', defaults={'name': 'Москва'})[0],
            'spb': Region.objects.get_or_create(code='78', defaults={'name': 'Санкт-Петербург'})[0],
        }

        # Create categories
        categories = {
            'transport': Category.objects.get_or_create(slug='transport', defaults={'name': 'Транспорт', 'icon': 'bus'})[0],
            'medicine': Category.objects.get_or_create(slug='medicine', defaults={'name': 'Медицина и лекарства', 'icon': 'medical'})[0],
            'utilities': Category.objects.get_or_create(slug='utilities', defaults={'name': 'Коммунальные услуги', 'icon': 'home'})[0],
            'social': Category.objects.get_or_create(slug='social_payments', defaults={'name': 'Социальные выплаты', 'icon': 'money'})[0],
            'housing': Category.objects.get_or_create(slug='housing', defaults={'name': 'Жилищные льготы', 'icon': 'house'})[0],
        }

        # Create federal benefits
        federal_benefits = [
            {
                'benefit_id': 'fed-transport-001',
                'title': 'Бесплатный проезд в общественном транспорте',
                'description': 'Льгота на бесплатный проезд в городском общественном транспорте (автобус, троллейбус, трамвай) для пенсионеров и инвалидов.',
                'benefit_type': 'federal',
                'target_groups': ['pensioner', 'disability_1', 'disability_2', 'disability_3'],
                'applies_to_all_regions': True,
                'requirements': 'Пенсионное удостоверение или справка об инвалидности',
                'how_to_get': 'Оформить социальную карту в МФЦ или отделении соцзащиты',
                'documents_needed': ['Паспорт', 'Пенсионное удостоверение', 'СНИЛС', 'Фотография'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/pensionres/',
                'categories': ['transport'],
            },
            {
                'benefit_id': 'fed-medicine-001',
                'title': 'Бесплатные лекарства по рецепту врача',
                'description': 'Право на получение бесплатных лекарственных препаратов по рецепту лечащего врача из перечня жизненно необходимых.',
                'benefit_type': 'federal',
                'target_groups': ['pensioner', 'disability_1', 'disability_2', 'disability_3', 'veteran'],
                'applies_to_all_regions': True,
                'requirements': 'Рецепт врача на лекарственный препарат',
                'how_to_get': 'Получить рецепт у врача и обратиться в социальную аптеку',
                'documents_needed': ['Паспорт', 'Полис ОМС', 'СНИЛС', 'Рецепт врача'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/pensionres/',
                'categories': ['medicine'],
            },
            {
                'benefit_id': 'fed-utilities-001',
                'title': 'Компенсация расходов на оплату ЖКХ',
                'description': 'Ежемесячная денежная компенсация 50% расходов на оплату жилищно-коммунальных услуг для инвалидов и ветеранов.',
                'benefit_type': 'federal',
                'target_groups': ['disability_1', 'disability_2', 'veteran', 'svo_participant'],
                'applies_to_all_regions': True,
                'requirements': 'Удостоверение инвалида или ветерана',
                'how_to_get': 'Подать заявление в отделение СФР',
                'documents_needed': ['Паспорт', 'Удостоверение', 'Квитанции ЖКХ', 'Реквизиты счета'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/invalidam/',
                'categories': ['utilities'],
            },
            {
                'benefit_id': 'fed-social-001',
                'title': 'Ежемесячная денежная выплата (ЕДВ)',
                'description': 'Ежемесячная денежная выплата инвалидам, ветеранам, героям СССР и РФ. Размер зависит от категории льготника.',
                'benefit_type': 'federal',
                'target_groups': ['disability_1', 'disability_2', 'disability_3', 'veteran'],
                'applies_to_all_regions': True,
                'requirements': 'Принадлежность к одной из льготных категорий',
                'how_to_get': 'Подать заявление в СФР или через Госуслуги',
                'documents_needed': ['Паспорт', 'СНИЛС', 'Удостоверение льготника', 'Реквизиты счета'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/social_support/',
                'categories': ['social'],
            },
            {
                'benefit_id': 'fed-family-001',
                'title': 'Материнский капитал',
                'description': 'Государственная поддержка семей при рождении или усыновлении ребенка. Средства можно направить на улучшение жилищных условий, образование детей, пенсию матери.',
                'benefit_type': 'federal',
                'target_groups': ['large_family'],
                'applies_to_all_regions': True,
                'requirements': 'Рождение или усыновление второго или последующего ребенка',
                'how_to_get': 'Подать заявление через Госуслуги или в отделении СФР',
                'documents_needed': ['Паспорт', 'Свидетельства о рождении детей', 'СНИЛС'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/semyam_s_detmi/',
                'categories': ['social', 'housing'],
            },
            {
                'benefit_id': 'fed-svo-001',
                'title': 'Выплаты участникам СВО',
                'description': 'Ежемесячные выплаты и единовременные пособия участникам специальной военной операции и членам их семей.',
                'benefit_type': 'federal',
                'target_groups': ['svo_participant', 'svo_family'],
                'applies_to_all_regions': True,
                'requirements': 'Документы, подтверждающие участие в СВО',
                'how_to_get': 'Обратиться в военкомат или СФР с документами',
                'documents_needed': ['Паспорт', 'Военный билет', 'Справка из военкомата'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/Informaciya_dlya_uchastnikov_SVO_i_ih_semei/',
                'categories': ['social'],
            },
        ]

        # Create regional benefits for Yakutsk
        regional_benefits = [
            {
                'benefit_id': 'reg-yakutsk-transport-001',
                'title': 'Дополнительные льготы на транспорт в Якутии',
                'description': 'Региональная программа поддержки пенсионеров: бесплатный проезд на междугородних автобусах внутри республики.',
                'benefit_type': 'regional',
                'target_groups': ['pensioner', 'disability_1'],
                'applies_to_all_regions': False,
                'regions_list': ['yakutsk'],
                'requirements': 'Регистрация в Республике Саха (Якутия)',
                'how_to_get': 'Оформить в МФЦ или отделении соцзащиты РС(Я)',
                'documents_needed': ['Паспорт с регистрацией', 'Пенсионное удостоверение'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/newregion/',
                'categories': ['transport'],
            },
            {
                'benefit_id': 'reg-yakutsk-utilities-001',
                'title': 'Компенсация на отопление в Якутии',
                'description': 'Повышенная компенсация расходов на отопление для жителей северных районов Якутии в связи с суровым климатом.',
                'benefit_type': 'regional',
                'target_groups': ['pensioner', 'disability_1', 'disability_2', 'low_income'],
                'applies_to_all_regions': False,
                'regions_list': ['yakutsk'],
                'requirements': 'Проживание в районах Крайнего Севера',
                'how_to_get': 'Подать заявление в соцзащиту РС(Я)',
                'documents_needed': ['Паспорт', 'Справка о составе семьи', 'Квитанции за отопление'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/newregion/',
                'categories': ['utilities'],
            },
            {
                'benefit_id': 'reg-yakutsk-housing-001',
                'title': 'Жилищные субсидии для северян',
                'description': 'Региональные субсидии на приобретение или строительство жилья для семей, проживающих на Крайнем Севере.',
                'benefit_type': 'regional',
                'target_groups': ['large_family', 'veteran', 'svo_participant'],
                'applies_to_all_regions': False,
                'regions_list': ['yakutsk'],
                'requirements': 'Стаж работы в районах Крайнего Севера не менее 15 лет',
                'how_to_get': 'Встать на учет в качестве нуждающегося в жилье',
                'documents_needed': ['Паспорт', 'Трудовая книжка', 'Справка о составе семьи'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/newregion/',
                'categories': ['housing'],
            },
        ]

        # Create municipal benefits
        municipal_benefits = [
            {
                'benefit_id': 'mun-yakutsk-social-001',
                'title': 'Адресная социальная помощь в г. Якутск',
                'description': 'Единовременная или ежемесячная материальная помощь малоимущим гражданам, проживающим в городе Якутске.',
                'benefit_type': 'municipal',
                'target_groups': ['low_income', 'pensioner', 'large_family'],
                'applies_to_all_regions': False,
                'regions_list': ['yakutsk'],
                'requirements': 'Доход ниже прожиточного минимума',
                'how_to_get': 'Обратиться в отдел соцзащиты администрации г. Якутска',
                'documents_needed': ['Паспорт', 'Справки о доходах всех членов семьи', 'Справка о составе семьи'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/social_support/',
                'categories': ['social'],
            },
            {
                'benefit_id': 'mun-yakutsk-medicine-001',
                'title': 'Бесплатная диспансеризация для пенсионеров',
                'description': 'Ежегодная бесплатная диспансеризация для пенсионеров города Якутска в муниципальных поликлиниках.',
                'benefit_type': 'municipal',
                'target_groups': ['pensioner'],
                'applies_to_all_regions': False,
                'regions_list': ['yakutsk'],
                'requirements': 'Регистрация в г. Якутске',
                'how_to_get': 'Записаться в поликлинику по месту прикрепления',
                'documents_needed': ['Паспорт', 'Полис ОМС', 'Пенсионное удостоверение'],
                'source_url': 'https://sfr.gov.ru/grazhdanam/pensionres/',
                'categories': ['medicine'],
            },
        ]

        all_benefits = federal_benefits + regional_benefits + municipal_benefits

        # Create benefits
        for data in all_benefits:
            benefit_id = data.pop('benefit_id')
            category_slugs = data.pop('categories', [])
            regions_list = data.pop('regions_list', [])

            if not Benefit.objects.filter(benefit_id=benefit_id).exists():
                benefit = Benefit.objects.create(
                    benefit_id=benefit_id,
                    valid_from=timezone.now().date(),
                    valid_to=timezone.now().date() + timedelta(days=365),
                    status='active',
                    **data
                )

                # Add categories
                for slug in category_slugs:
                    if slug in categories:
                        benefit.categories.add(categories[slug])

                # Add regions
                for region_key in regions_list:
                    if region_key in regions:
                        benefit.regions.add(regions[region_key])

                self.stdout.write(self.style.SUCCESS(f'Created benefit: {benefit_id}'))

        # Create additional commercial offers
        additional_offers = [
            {
                'offer_id': 'comm-pharmacy-002',
                'title': 'Бесплатная доставка лекарств на дом',
                'description': 'Бесплатная доставка лекарств для пенсионеров и инвалидов по городу Якутску',
                'discount_description': 'Бесплатная доставка',
                'partner_name': 'Аптечная сеть "Фармация"',
                'partner_category': 'Аптека',
                'target_groups': ['pensioner', 'disability_1', 'disability_2'],
                'how_to_use': 'Позвонить по телефону и оформить заказ',
                'regions_list': ['yakutsk'],
            },
            {
                'offer_id': 'comm-store-001',
                'title': 'Скидка 15% на продукты питания',
                'description': 'Скидка 15% на все продукты питания для многодетных семей',
                'discount_description': 'Скидка 15%',
                'partner_name': 'Супермаркет "Полярный"',
                'partner_category': 'Продуктовый магазин',
                'target_groups': ['large_family'],
                'how_to_use': 'Предъявить удостоверение многодетной семьи на кассе',
                'regions_list': ['yakutsk'],
            },
            {
                'offer_id': 'comm-telecom-001',
                'title': 'Льготный тариф на телефонную связь',
                'description': 'Специальный тариф для пенсионеров: 300 минут и 5 ГБ интернета за 200 рублей',
                'discount_description': 'Льготный тариф',
                'partner_name': 'МТС',
                'partner_category': 'Мобильная связь',
                'target_groups': ['pensioner', 'veteran'],
                'how_to_use': 'Подключить в салоне связи с документами',
                'regions_list': ['yakutsk', 'moscow', 'spb'],
            },
            {
                'offer_id': 'comm-bank-001',
                'title': 'Бесплатное обслуживание карты для пенсионеров',
                'description': 'Бесплатное открытие и обслуживание дебетовой карты МИР для получения пенсии',
                'discount_description': 'Без платы за обслуживание',
                'partner_name': 'Сбербанк',
                'partner_category': 'Банковские услуги',
                'target_groups': ['pensioner'],
                'how_to_use': 'Обратиться в любое отделение банка',
                'regions_list': ['yakutsk', 'moscow', 'spb'],
            },
            {
                'offer_id': 'comm-transport-001',
                'title': 'Скидка 30% на такси для инвалидов',
                'description': 'Постоянная скидка 30% на все поездки для людей с ограниченными возможностями',
                'discount_description': 'Скидка 30%',
                'partner_name': 'Яндекс.Такси',
                'partner_category': 'Транспорт',
                'target_groups': ['disability_1', 'disability_2', 'disability_3'],
                'how_to_use': 'Указать статус в приложении при заказе',
                'promo_code': 'INVALID30',
                'regions_list': ['yakutsk', 'moscow', 'spb'],
            },
            {
                'offer_id': 'comm-education-001',
                'title': 'Бесплатные компьютерные курсы для пенсионеров',
                'description': 'Бесплатное обучение основам работы на компьютере и в интернете для пенсионеров',
                'discount_description': 'Бесплатное обучение',
                'partner_name': 'IT-школа "Цифровой мир"',
                'partner_category': 'Образование',
                'target_groups': ['pensioner'],
                'how_to_use': 'Записаться по телефону на ближайший курс',
                'regions_list': ['yakutsk'],
            },
        ]

        for data in additional_offers:
            offer_id = data.pop('offer_id')
            regions_list = data.pop('regions_list', [])

            if not CommercialOffer.objects.filter(offer_id=offer_id).exists():
                offer = CommercialOffer.objects.create(
                    offer_id=offer_id,
                    valid_from=timezone.now().date(),
                    valid_to=timezone.now().date() + timedelta(days=180),
                    status='active',
                    applies_to_all_regions=False,
                    promo_code=data.pop('promo_code', ''),
                    **data
                )

                # Add regions
                for region_key in regions_list:
                    if region_key in regions:
                        offer.regions.add(regions[region_key])

                self.stdout.write(self.style.SUCCESS(f'Created offer: {offer_id}'))

        self.stdout.write(self.style.SUCCESS(f'\nSummary:'))
        self.stdout.write(f'Total benefits: {Benefit.objects.count()}')
        self.stdout.write(f'Total offers: {CommercialOffer.objects.count()}')
