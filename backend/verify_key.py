import os
import sys

try:
    from dotenv import load_dotenv
    print("python-dotenv is installed.")
    load_dotenv()
except ImportError:
    print("python-dotenv is NOT installed.")
    # Fallback: try to read .env manually for this test
    try:
        with open('.env') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        key, value = parts
                        os.environ[key] = value
        print("Manually loaded .env")
    except Exception as e:
        print(f"Could not read .env: {e}")

try:
    from mistralai import Mistral
except ImportError:
    print("mistralai is NOT installed.")
    sys.exit(1)

api_key = os.getenv('MISTRAL_API_KEY')
print(f"API Key found: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API Key length: {len(api_key)}")
    print(f"API Key start: {api_key[:4]}...")
else:
    print("MISTRAL_API_KEY not found in environment.")
    sys.exit(1)

client = Mistral(api_key=api_key)

try:
    print("Attempting to call Mistral API...")
    resp = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("Success!")
    print(resp.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
