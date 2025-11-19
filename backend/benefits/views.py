from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
import json
from .query_parser import QueryParser
from .embedding_service import LocalEmbeddingService
from .vector_store import InMemoryVectorStore
from .models import SearchIndex
from benefits.models import Benefit, CommercialOffer

# Global services
query_parser = QueryParser()
embedding_service = LocalEmbeddingService()
vector_store = InMemoryVectorStore()


class NaturalLanguageSearchAPI(APIView):
    """Unified search for benefits and commercial offers"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query_text = request.data.get('query', '').strip()
        if not query_text:
            return Response({'error': 'Query is required'}, status=400)

        # Get user region for personalization
        user_profile = getattr(request.user, 'userprofile', None)
        user_region = user_profile.region if user_profile else None

        # 1. Parse query
        parsed = query_parser.parse(query_text, user_region)

        # 2. Generate query embedding
        query_embedding = embedding_service.generate(f"query: {query_text}")

        # 3. Search in FAISS
        search_results = vector_store.search(
            query_embedding,
            filters=parsed['filters'],
            top_k=20
        )

        # 4. Fetch actual objects from SQLite
        search_ids = [sid for sid, _ in search_results]
        search_records = SearchIndex.objects.filter(id__in=search_ids)

        # Group by type
        benefits = []
        offers = []
        similarity_scores = {}

        for sid, sim in search_results:
            similarity_scores[sid] = sim

        for record in search_records:
            # Attach similarity score
            record.search_similarity = similarity_scores.get(record.id, 0)

            if record.content_type_name == 'benefit':
                benefits.append(record.content_object)
            elif record.content_type_name == 'commercial':
                offers.append(record.content_object)

        # 5. Serialize with type information
        return Response({
            'query': parsed,
            'benefits': [{
                'id': b.id,
                'title': b.title,
                'description': b.description,
                'type': 'benefit',
                'benefit_type': b.benefit_type,
                'similarity': similarity_scores.get(
                    SearchIndex.objects.get(
                        content_type=ContentType.objects.get_for_model(Benefit),
                        object_id=b.id
                    ).id, 0
                )
            } for b in benefits[:10]],
            'offers': [{
                'id': o.id,
                'title': o.title,
                'description': o.description,
                'type': 'commercial',
                'partner': o.partner_name,
                'discount': o.discount_description,
                'similarity': similarity_scores.get(
                    SearchIndex.objects.get(
                        content_type=ContentType.objects.get_for_model(CommercialOffer),
                        object_id=o.id
                    ).id, 0
                )
            } for o in offers[:10]],
            'total_benefits': len(benefits),
            'total_offers': len(offers)
        })


class MixedSearchResultsView(APIView):
    """Get full details of mixed results"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Accept list of mixed IDs and return full objects"""
        item_ids = request.data.get('items', [])  # [{'type': 'benefit', 'id': 123}, ...]

        results = []
        for item in item_ids:
            if item['type'] == 'benefit':
                obj = get_object_or_404(Benefit, id=item['id'])
                results.append({
                    'type': 'benefit',
                    'id': obj.id,
                    'title': obj.title,
                    'description': obj.description,
                    'requirements': obj.requirements,
                    'how_to_get': obj.how_to_get,
                    'documents_needed': obj.documents_needed,
                    'regions': [r.name for r in obj.regions.all()],
                    'categories': [c.name for c in obj.categories.all()],
                })
            elif item['type'] == 'commercial':
                obj = get_object_or_404(CommercialOffer, id=item['id'])
                results.append({
                    'type': 'commercial',
                    'id': obj.id,
                    'title': obj.title,
                    'description': obj.description,
                    'discount_description': obj.discount_description,
                    'how_to_use': obj.how_to_use,
                    'partner_name': obj.partner_name,
                    'regions': [r.name for r in obj.regions.all()],
                })

        return Response(results)