import csv
import os
import json
from django.core.management.base import BaseCommand
from django.db import connection, OperationalError, transaction
from benefits.models import Benefit, Region, Category


class Command(BaseCommand):
    help = 'Import benefits from CSV file into database with auto-indexing'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--clear', action='store_true', help='Clear existing CSV-imported benefits first')
        parser.add_argument('--batch-size', type=int, default=10, help='Batch size for bulk operations')

    def handle(self, *args, **options):
        csv_path = options['csv_file']
        batch_size = options['batch_size']

        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'File not found: {csv_path}'))
            return

        # Verify SearchIndex table exists
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM search_index LIMIT 1")
        except OperationalError:
            self.stdout.write(self.style.ERROR(
                'SearchIndex table not found. Run: python manage.py migrate search'
            ))
            return

        # Clear existing if requested
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing CSV-imported benefits...'))
            deleted = Benefit.objects.filter(benefit_id__startswith='sfr_').delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted[0]} benefits'))

        # Setup defaults
        default_region, created = Region.objects.get_or_create(
            code='00',
            defaults={'name': 'Вся Россия'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created default region: {default_region}'))

        # Default category if not specified
        default_category, created = Category.objects.get_or_create(
            name='Льготы для инвалидов',
            defaults={'slug': 'invalidam', 'description': 'Льготы для людей с инвалидностью'}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created default category: {default_category}'))

        # Process CSV
        count = 0
        errors = 0

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            benefits_to_create = []

            for row in reader:
                try:
                    benefit_id = f"sfr_{row['id']}"

                    # Skip if exists
                    if Benefit.objects.filter(benefit_id=benefit_id).exists():
                        self.stdout.write(f"⚠️ Skipping existing: {benefit_id}")
                        continue

                    # Get or create category from CSV if available
                    if 'category' in row and row['category']:
                        category_name = row['category']
                        # Create slug from name
                        category_slug = category_name.lower().replace(' ', '-')
                        category, _ = Category.objects.get_or_create(
                            name=category_name,
                            defaults={'slug': category_slug, 'description': f'Категория: {category_name}'}
                        )
                    else:
                        category = default_category

                    # Create benefit
                    benefit = Benefit(
                        benefit_id=benefit_id,
                        title=row['header'][:255],
                        description=row['text'][:4000],
                        benefit_type='federal',
                        target_groups=['disability_1', 'disability_2', 'disability_3'],
                        applies_to_all_regions=True,
                        valid_from='2024-01-01',
                        valid_to='2024-12-31',
                        status='active',
                        requirements='Обратитесь в СФР с паспортом и документами',
                        how_to_get='Подайте заявление через портал Госуслуги',
                        documents_needed=['Паспорт', 'Справка об инвалидности'],
                        source_url=row['url'][:200]
                    )

                    benefits_to_create.append((benefit, category))
                    count += 1

                    # Bulk create in batches
                    if len(benefits_to_create) >= batch_size:
                        self._create_batch(benefits_to_create, default_region)
                        benefits_to_create = []

                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.ERROR(f"✗ Row {row['id']}: {e}"))
                    continue

            # Create remaining
            if benefits_to_create:
                self._create_batch(benefits_to_create, default_region)

        # Summary
        if errors > 0:
            self.stdout.write(self.style.WARNING(f'\nCompleted with {errors} errors'))

        self.stdout.write(self.style.SUCCESS(f'\n✓ Imported {count} benefits'))
        self.stdout.write(self.style.SUCCESS('✓ Embeddings will auto-generate via signals'))

        # Show final counts
        benefit_count = Benefit.objects.filter(benefit_id__startswith='sfr_').count()
        self.stdout.write(self.style.SUCCESS(f'\nTotal benefits: {benefit_count}'))

    def _create_batch(self, benefits_with_categories, region):
        """Create benefits in bulk and add relationships"""
        # Extract just the benefits for bulk creation
        benefits = [item[0] for item in benefits_with_categories]
        created_benefits = Benefit.objects.bulk_create(benefits)

        # Add relationships with their respective categories
        for i, benefit in enumerate(created_benefits):
            category = benefits_with_categories[i][1]
            benefit.regions.add(region)
            benefit.categories.add(category)

        self.stdout.write(self.style.SUCCESS(f'✓ Created batch of {len(created_benefits)} benefits'))