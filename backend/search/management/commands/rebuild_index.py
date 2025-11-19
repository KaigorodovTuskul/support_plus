# search/management/commands/rebuild_index.py
from django.core.management.base import BaseCommand
from search.vector_store import InMemoryVectorStore


class Command(BaseCommand):
    help = 'Rebuild vector search index'

    def handle(self, *args, **options):
        store = InMemoryVectorStore()
        store._rebuild_index()
        self.stdout.write(self.style.SUCCESS('✓ Index rebuilt!'))