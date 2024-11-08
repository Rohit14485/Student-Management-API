import requests

def generate_response(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2",
        "prompt": "hello"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Checks for HTTP errors
        return response.json()  # Assuming response is in JSON format
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
