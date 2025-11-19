from sentence_transformers import SentenceTransformer
import torch
import json


class LocalEmbeddingService:
    """Synchronous local embedding generation"""

    def __init__(self):
        # Load model once at startup (~1.5GB RAM)
        self.model = SentenceTransformer(
            'intfloat/multilingual-e5-large',
            device='cpu'  # No GPU dependency
        )

    def generate(self, text: str) -> list[float]:
        """Generate embedding for any text"""
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True
        ).tolist()
        return embedding

    def generate_for_benefit(self, benefit) -> list[float]:
        """Create rich embedding from Benefit model"""
        regions_text = ', '.join([r.name for r in benefit.regions.all()[:3]])
        categories_text = ', '.join([c.name for c in benefit.categories.all()[:3]])

        text = f"""
        Title: {benefit.title}
        Type: {benefit.get_benefit_type_display()}
        Description: {benefit.description}
        Requirements: {benefit.requirements}
        How to get: {benefit.how_to_get}
        Regions: {regions_text}
        Categories: {categories_text}
        """
        return self.generate(text)

    def generate_for_offer(self, offer) -> list[float]:
        """Create rich embedding from CommercialOffer model"""
        regions_text = ', '.join([r.name for r in offer.regions.all()[:3]])
        categories_text = ', '.join([c.name for c in offer.categories.all()[:3]])

        text = f"""
        Title: {offer.title}
        Partner: {offer.partner_name}
        Discount: {offer.discount_description}
        Description: {offer.description}
        How to use: {offer.how_to_use}
        Regions: {regions_text}
        Categories: {categories_text}
        """
        return self.generate(text)