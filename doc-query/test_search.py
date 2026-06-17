import requests
import json

url = 'http://127.0.0.1:8001/api/search'
payload = {'query': 'What is the tech stack for the payment system?'}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    print('Search Results:')
    for i, result in enumerate(data.get('results', [])):
        print(f"\n--- Result {i+1} ---")
        print(f"Doc ID: {result.get('doc_id')}")
        print(f"Similarity (pgvector): {result.get('similarity', 'N/A')}")
        print(f"Cross-Encoder Score: {result.get('cross_encoder_score', 'N/A')}")
        print(f"Text Snippet: {result.get('chunk_text', '')[:150]}...")
except requests.exceptions.RequestException as e:
    print(f'Error connecting to the service: {e}')
