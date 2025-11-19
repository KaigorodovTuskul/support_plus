from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
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


class DocumentListView(LoginRequiredMixin, TemplateView):
    """Main page showing initial list of active benefits/offers"""
    template_name = 'search/document_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Show recent benefits for initial load
        context['benefits'] = Benefit.objects.filter(
            status__in=['active', 'expiring_soon']
        ).select_related('benefit_id')[:20]

        return context


class PersonalPageView(LoginRequiredMixin, TemplateView):
    """Personal account page with user history and recommendations"""
    template_name = 'search/personal_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.userprofile

        # Recent searches
        context['recent_searches'] = profile.search_history[-5:]

        # Recommendations based on user profile
        recommended_benefits = Benefit.objects.filter(
            status='active',
            target_groups__overlap=self._get_user_groups(profile)
        )[:5]

        recommended_offers = CommercialOffer.objects.filter(
            status='active',
            target_groups__overlap=self._get_user_groups(profile)
        )[:5]

        context['recommendations'] = {
            'benefits': recommended_benefits,
            'offers': recommended_offers
        }

        return context

    def _get_user_groups(self, profile):
        """Get user's target groups from profile"""
        groups = []
        if profile.is_pensioner:
            groups.append('pensioner')
        if profile.is_disabled:
            groups.append('disability_2')  # Default, adjust as needed
        return groups


class NaturalLanguageSearchAPI(APIView):
    """Main search endpoint - handles natural language queries"""
    # permission_classes = [IsAuthenticated]
    permission_classes = []
    def post(self, request):
        query_text = request.data.get('query', '').strip()
        if not query_text:
            return Response({'error': 'Query is required'}, status=400)

        # Get user profile
        user_profile = getattr(request.user, 'userprofile', None)
        user_region = user_profile.region if user_profile else None

        # 1. Parse natural language query
        parsed = query_parser.parse(query_text, user_region)

        # 2. Generate embedding
        query_embedding = embedding_service.generate(f"query: {query_text}")

        # 3. Search in FAISS
        search_results = vector_store.search(
            query_embedding,
            filters=parsed['filters'],
            top_k=20
        )

        # 4. Fetch full objects from database
        search_ids = [sid for sid, _ in search_results]
        search_records = SearchIndex.objects.filter(id__in=search_ids)

        # 5. Attach similarity scores
        similarity_dict = {sid: sim for sid, sim in search_results}

        benefits = []
        offers = []

        for record in search_records:
            record.search_similarity = similarity_dict.get(record.id, 0)

            if record.content_type_name == 'benefit':
                benefits.append(record.content_object)
            elif record.content_type_name == 'commercial':
                offers.append(record.content_object)

        # 6. Log search history
        if user_profile:
            self._log_search_history(user_profile, query_text, parsed)

        return Response({
            'query': parsed,
            'benefits': [{
                'id': b.id,
                'title': b.title,
                'description': b.description,
                'benefit_type': b.benefit_type,
                'requirements': b.requirements,
                'how_to_get': b.how_to_get,
                'regions': [r.name for r in b.regions.all()[:3]],
                'similarity': similarity_dict.get(
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
                'partner_name': o.partner_name,
                'discount_description': o.discount_description,
                'how_to_use': o.how_to_use,
                'regions': [r.name for r in o.regions.all()[:3]],
                'similarity': similarity_dict.get(
                    SearchIndex.objects.get(
                        content_type=ContentType.objects.get_for_model(CommercialOffer),
                        object_id=o.id
                    ).id, 0
                )
            } for o in offers[:10]],
            'total_benefits': len(benefits),
            'total_offers': len(offers)
        })

    def _log_search_history(self, profile, query, parsed):
        """Save search to user profile (no Redis needed)"""
        profile.search_history.append({
            'query': query,
            'timestamp': str(profile._meta.get_field('search_history').to_python(None)),
            'intent': parsed['intent']
        })
        profile.search_history = profile.search_history[-20:]  # Keep last 20
        profile.save(update_fields=['search_history'])


class MixedSearchResultsView(APIView):
    """Get full details of selected search results"""
    # permission_classes = [IsAuthenticated]
    permission_classes = []

    def post(self, request):
        item_ids = request.data.get('items', [])  # [{'type': 'benefit', 'id': 123}, ...]

        results = []
        for item in item_ids:
            try:
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
                        'source_url': obj.source_url,
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
                        'partner_name': obj.partner_name,
                        'partner_website': obj.partner_website,
                        'how_to_use': obj.how_to_use,
                        'promo_code': obj.promo_code,
                        'regions': [r.name for r in obj.regions.all()],
                    })
            except Exception as e:
                continue  # Skip invalid items

        return Response(results)