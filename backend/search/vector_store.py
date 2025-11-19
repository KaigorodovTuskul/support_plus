import faiss
import numpy as np
import json
import os
from django.conf import settings
from django.db import OperationalError  # Import this to catch table errors
from .models import SearchIndex


class InMemoryVectorStore:
    """Singleton FAISS index with lazy loading"""
    _instance = None
    _index = None
    _index_map = []
    _initialized = False  # Add initialization flag

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._create_empty_index()  # Create empty index, don't load
        return cls._instance

    def _create_empty_index(self):
        """Create empty FAISS index without touching database"""
        dimension = 1024
        self._index = faiss.IndexFlatIP(dimension)
        self._index_map = []
        self._initialized = False

    def ensure_initialized(self):
        """Load from disk or rebuild from DB (safe to call after migrations)"""
        if not self._initialized:
            self._load_or_rebuild()
            self._initialized = True

    def _load_or_rebuild(self):
        """Load existing index or rebuild from database if table exists"""
        index_path = os.path.join(settings.BASE_DIR, 'search_index.faiss')
        mapping_path = os.path.join(settings.BASE_DIR, 'search_mapping.json')

        # Try to load from disk first
        if os.path.exists(index_path) and os.path.exists(mapping_path):
            try:
                self._index = faiss.read_index(index_path)
                with open(mapping_path, 'r') as f:
                    self._index_map = json.load(f)
                print(f"✓ Loaded {len(self._index_map)} vectors from disk")
                return
            except Exception as e:
                print(f"⚠️ Could not load from disk: {e}")

        # Try to rebuild from database (only if table exists)
        try:
            self._rebuild_index()
        except OperationalError:
            print("⚠️ SearchIndex table doesn't exist yet. Will rebuild after migrations.")
            self._create_empty_index()

    def _rebuild_index(self):
        """Rebuild from database - only called when table exists"""
        print("Building vector index from database...")
        self._index.reset()
        self._index_map = []

        # This is safe now because we know the table exists
        for search_record in SearchIndex.objects.filter(
                is_active=True,
                embedding_vector__isnull=False
        ):
            vector = search_record.get_embedding()
            if vector:
                self._index.add(np.array(vector, dtype=np.float32).reshape(1, -1))
                self._index_map.append(search_record.id)

        self._persist_to_disk()
        print(f"✓ Indexed {len(self._index_map)} documents")

    def add_item(self, search_index_id: int, embedding: list):
        """Add single item to index"""
        vector = np.array(embedding, dtype=np.float32).reshape(1, -1)
        self._index.add(vector)
        self._index_map.append(search_index_id)
        self._persist_to_disk()

    def search(self, query_embedding: list, filters: dict, top_k: int = 20):
        """Search - ensures initialization first"""
        self.ensure_initialized()

        # NEW: Rebuild if index is empty
        if self._index.ntotal == 0:
            print("⚠️ Index is empty, rebuilding...")
            self._rebuild_index()

        # Rest of search code
        query_vector = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        distances, indices = self._index.search(query_vector, top_k * 3)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self._index_map):
                search_index_id = self._index_map[idx]
                if self._matches_filters(search_index_id, filters):
                    results.append((search_index_id, float(distances[0][i])))
                    if len(results) >= top_k:
                        break

        return results

    def _matches_filters(self, search_index_id: int, filters: dict) -> bool:
        """Check if SearchIndex record matches filters"""
        try:
            record = SearchIndex.objects.get(id=search_index_id)

            if content_types := filters.get('content_type'):
                if record.content_type_name not in content_types:
                    return False

            if target_groups := filters.get('target_groups'):
                if not any(tg in record.target_groups for tg in target_groups):
                    return False

            if region_codes := filters.get('regions'):
                if not any(str(r) in record.regions for r in region_codes):
                    return False

            return True
        except SearchIndex.DoesNotExist:
            return False

    def _persist_to_disk(self):
        """Save index and mapping to disk"""
        index_path = os.path.join(settings.BASE_DIR, 'search_index.faiss')
        mapping_path = os.path.join(settings.BASE_DIR, 'search_mapping.json')

        faiss.write_index(self._index, index_path)
        with open(mapping_path, 'w') as f:
            json.dump(self._index_map, f)

    def remove_document(self, doc_id: int):
        """Remove from index (rebuild for simplicity)"""
        self.ensure_initialized()
        self._rebuild_index()  # Clean rebuild