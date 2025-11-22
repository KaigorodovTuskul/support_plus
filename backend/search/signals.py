from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.db import OperationalError
import json  # Add this
from benefits.models import Benefit, CommercialOffer
from .models import SearchIndex
from .embedding_service import LocalEmbeddingService
from .vector_store import InMemoryVectorStore

# Global singletons
embedding_service = LocalEmbeddingService()
vector_store = InMemoryVectorStore()


def create_or_update_search_index(instance, content_type_name):
    """Create/update SearchIndex - now with error handling"""
    try:
        content_type = ContentType.objects.get_for_model(instance.__class__)

        # Get regions as codes
        regions = [r.code for r in instance.regions.all()[:5]]  # Limit to 5 regions for speed
        if not regions and instance.applies_to_all_regions:
            regions = ['all']

        # Generate embedding
        if content_type_name == 'benefit':
            embedding = embedding_service.generate_for_benefit(instance)
        else:
            embedding = embedding_service.generate_for_offer(instance)

        # Create/update SearchIndex
        search_index, created = SearchIndex.objects.update_or_create(
            content_type=content_type,
            object_id=instance.id,
            defaults={
                'title': instance.title,
                'content_type_name': content_type_name,
                'target_groups': instance.target_groups,
                'regions': regions,
                'is_active': instance.status in ['active', 'expiring_soon'],
                'embedding_vector': json.dumps(embedding)
            }
        )

        # Add to FAISS index
        vector_store.add_item(search_index.id, embedding)

    except OperationalError:
        # Table doesn't exist yet - silently skip (will be indexed after migrations)
        print(f"SearchIndex table not ready for {content_type_name} {instance.id}")
        pass
    except Exception as e:
        print(f"Error indexing {content_type_name}: {e}")


@receiver(post_save, sender=Benefit)
def handle_benefit_save(sender, instance, created, **kwargs):
    if instance.status != 'expired':
        create_or_update_search_index(instance, 'benefit')
    else:
        content_type = ContentType.objects.get_for_model(Benefit)
        SearchIndex.objects.filter(
            content_type=content_type,
            object_id=instance.id
        ).delete()
        vector_store.remove_document(instance.id)


@receiver(post_save, sender=CommercialOffer)
def handle_offer_save(sender, instance, created, **kwargs):
    if instance.status != 'expired':
        create_or_update_search_index(instance, 'commercial')
    else:
        content_type = ContentType.objects.get_for_model(CommercialOffer)
        SearchIndex.objects.filter(
            content_type=content_type,
            object_id=instance.id
        ).delete()
        vector_store.remove_document(instance.id)


@receiver(post_delete, sender=Benefit)
@receiver(post_delete, sender=CommercialOffer)
def handle_content_delete(sender, instance, **kwargs):
    """Clean up search index when content is deleted"""
    try:
        content_type = ContentType.objects.get_for_model(sender)
        SearchIndex.objects.filter(
            content_type=content_type,
            object_id=instance.id
        ).delete()
        vector_store.remove_document(instance.id)
    except OperationalError:
        pass  # Table might not exist during migrations