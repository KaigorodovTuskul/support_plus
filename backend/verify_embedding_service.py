import os
import sys
import django
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from search.embedding_service import MistralEmbeddingService

def verify_embedding_service():
    print("Initializing MistralEmbeddingService...")
    try:
        service = MistralEmbeddingService()
        print("[OK] Service initialized")
    except Exception as e:
        print(f"[FAIL] Failed to initialize service: {e}")
        return

    print("\nTesting generate()...")
    try:
        text = "Тестовый запрос для проверки эмбеддингов"
        embedding = service.generate(text)
        
        if len(embedding) == 1024:
            print(f"[OK] Generated embedding with correct dimension: {len(embedding)}")
            # Check if it's not all zeros (unless API failed and we returned fallback)
            if any(embedding):
                print("[OK] Embedding contains non-zero values")
            else:
                print("[WARN] Embedding contains all zeros (API error fallback?)")
        else:
            print(f"[FAIL] Incorrect dimension: {len(embedding)} (expected 1024)")
            
    except Exception as e:
        print(f"[FAIL] Failed to generate embedding: {e}")

if __name__ == "__main__":
    verify_embedding_service()
