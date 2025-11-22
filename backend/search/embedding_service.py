# ЗАКОММЕНТИРОВАНО: Используем только облачные API, без локальных моделей
# from sentence_transformers import SentenceTransformer
# import torch
import json


class LocalEmbeddingService:
    """
    ЗАГЛУШКА: Локальные embeddings отключены для деплоя на VPS.
    Используйте облачные API для векторного поиска.
    """

    def __init__(self):
        # Заглушка - не загружаем локальную модель
        pass

    def generate(self, text: str) -> list[float]:
        """Заглушка - возвращает нулевой вектор правильной размерности"""
        # Для VPS используйте облачные API для embeddings
        return [0.0] * 1024

    def generate_for_benefit(self, benefit) -> list[float]:
        """Заглушка - возвращает нулевой вектор правильной размерности"""
        return [0.0] * 1024

    def generate_for_offer(self, offer) -> list[float]:
        """Заглушка - возвращает нулевой вектор правильной размерности"""
        return [0.0] * 1024