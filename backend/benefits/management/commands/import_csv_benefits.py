import csv
from django.core.management.base import BaseCommand
from benefits.models import Benefit, Category
from django.utils import timezone
from datetime import datetime


class Command(BaseCommand):
    help = 'Import benefits from CSV file db/sfr_all_categories.csv'

    def handle(self, *args, **options):
        # Path relative to project root (parent of backend directory)
        from pathlib import Path

        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        csv_file = base_dir / 'db' / 'sfr_all_categories.csv'

        self.stdout.write(self.style.WARNING(f'Starting import from {csv_file}...'))

        # Create default category
        default_category, created = Category.objects.get_or_create(
            slug='sfr',
            defaults={
                'name': 'СФР (Социальный фонд России)',
                'description': 'Льготы и услуги Социального фонда России',
                'icon': 'document-text'
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created default category: {default_category.name}'))

        # Read and import CSV
        imported_count = 0
        updated_count = 0

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    benefit_id = f"sfr_{row['id']}"

                    # Determine benefit type based on URL
                    url = row.get('url', '')
                    benefit_type = 'federal'  # Default to federal for SFR benefits

                    # Determine target groups based on category
                    category = row.get('category', '').lower()
                    target_groups = []

                    if 'pension' in category or 'пенсион' in category:
                        target_groups.append('pensioner')
                    if 'invalid' in category or 'инвалид' in category:
                        target_groups.extend(['disability_1', 'disability_2', 'disability_3'])
                    if 'sem' in category or 'семь' in category or 'detmi' in category or 'детьми' in category:
                        target_groups.append('large_family')
                    if 'veteran' in category or 'ветеран' in category:
                        target_groups.append('veteran')
                    if 'svo' in category:
                        target_groups.extend(['svo_participant', 'svo_family'])

                    # If no specific target groups, make it available for all
                    if not target_groups:
                        target_groups = ['pensioner', 'disability_1', 'disability_2', 'disability_3',
                                       'large_family', 'veteran', 'low_income', 'svo_participant', 'svo_family']

                    # Create or update benefit
                    benefit, created = Benefit.objects.update_or_create(
                        benefit_id=benefit_id,
                        defaults={
                            'title': row.get('header', 'Без названия'),
                            'description': row.get('text', 'Описание отсутствует'),
                            'benefit_type': benefit_type,
                            'target_groups': list(set(target_groups)),  # Remove duplicates
                            'applies_to_all_regions': True,  # SFR benefits are typically federal
                            'valid_from': timezone.now().date(),
                            'status': 'active',
                            'requirements': 'Информацию о требованиях уточняйте на сайте СФР',
                            'how_to_get': 'Подробную информацию о получении льготы можно найти на официальном сайте СФР',
                            'documents_needed': [],
                            'source_url': row.get('url', row.get('base_url', 'https://sfr.gov.ru')),
                        }
                    )

                    # Add to default category
                    benefit.categories.add(default_category)

                    if created:
                        imported_count += 1
                    else:
                        updated_count += 1

                    if (imported_count + updated_count) % 10 == 0:
                        self.stdout.write(f'Processed {imported_count + updated_count} records...')

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during import: {str(e)}'))
            return

        self.stdout.write(self.style.SUCCESS(
            f'\nImport completed successfully!\n'
            f'Imported: {imported_count} new benefits\n'
            f'Updated: {updated_count} existing benefits\n'
            f'Total processed: {imported_count + updated_count}'
        ))
