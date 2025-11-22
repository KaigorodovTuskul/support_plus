# ЗАКОММЕНТИРОВАНО: Используем только облачные API, без локальных моделей
# from sentence_transformers import SentenceTransformer
# import torch
import json
import os
from mistralai import Mistral
import time


class MistralEmbeddingService:
    """
    Service for generating embeddings using Mistral API.
    """

    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is not set")
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-embed"

    def generate(self, text: str) -> list[float]:
        """Generate embedding for a single text string"""
        if not text:
            return [0.0] * 1024
            
        try:
            response = self.client.embeddings.create(
                model=self.model,
                inputs=[text]
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            # Return zero vector on error to prevent crash, but log it
            return [0.0] * 1024

    def generate_for_benefit(self, benefit) -> list[float]:
        """Generate embedding for a Benefit object"""
        # Combine relevant fields for semantic search
        text = f"{benefit.title} {benefit.description} {benefit.requirements}"
        # Add target groups and regions for better context
        if benefit.target_groups:
            text += f" для {', '.join(benefit.target_groups)}"
        
        return self.generate(text)

    def generate_for_offer(self, offer) -> list[float]:
        """Generate embedding for a CommercialOffer object"""
        text = f"{offer.title} {offer.description} {offer.partner_name} {offer.discount_description}"
        return self.generate(text)