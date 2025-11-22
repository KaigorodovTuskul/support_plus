import requests
import json

BASE_URL = "http://localhost:8000/api"

def reproduce():
    # 1. Login
    login_url = f"{BASE_URL}/auth/login/"
    credentials = {
        "username": "kolyaaa",
        "password": "admin1"
    }
    
    print(f"Logging in as {credentials['username']}...")
    try:
        response = requests.post(login_url, json=credentials)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            print(response.text)
            return
            
        tokens = response.json()
        access_token = tokens.get('access')
        print("Login successful. Got access token.")
        
    except Exception as e:
        print(f"Login error: {e}")
        return

    # 2. Send Chat Message
    chat_url = f"{BASE_URL}/chat/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "message": "Hello, chatbot!"
    }
    
    print(f"Sending message to {chat_url}...")
    try:
        response = requests.post(chat_url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(response.text)
        
    except Exception as e:
        print(f"Chat request error: {e}")

if __name__ == "__main__":
    reproduce()
