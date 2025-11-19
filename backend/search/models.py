from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json


class SearchIndex(models.Model):
    """
    Unified index for both Benefit and CommercialOffer.
    Uses GenericForeignKey to link to either model.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Store embedding as JSON in SQLite
    embedding_vector = models.TextField(null=True, blank=True)  # JSON serialized

    # Denormalized fields for fast filtering
    title = models.CharField(max_length=500)
    content_type_name = models.CharField(max_length=20)  # 'benefit' or 'commercial'
    target_groups = models.JSONField(default=list)
    regions = models.JSONField(default=list)  # Store region IDs
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'search_index'
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['content_type_name', 'is_active']),
        ]

    def get_embedding(self):
        """Deserialize embedding vector"""
        if self.embedding_vector:
            return json.loads(self.embedding_vector)
        return None

    def set_embedding(self, vector):
        """Serialize embedding vector"""
        self.embedding_vector = json.dumps(vector)