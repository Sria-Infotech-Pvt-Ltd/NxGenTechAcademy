import os
import sys
from pathlib import Path

# Add Backend root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Ensure DATABASE_URL is set for Django PostgreSQL connection
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@127.0.0.1:5432/postgres?sslmode=disable"

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

import django
django.setup()

import json
from rest_framework.test import APIClient

client = APIClient(SERVER_NAME='localhost')
url = '/api/chatbot/search/'

tests = [
    (1, "Tell me about Python courses", {"query": "Tell me about Python courses"}),
    (2, "What is the duration of the Python course?", {"query": "What is the duration of the Python course?"}),
    (3, "Tell me about Artificial Intelligence", {"query": "Tell me about Artificial Intelligence"}),
    (4, "Tell me about AIML", {"query": "Tell me about AIML"}),
    (5, "Tell me about Data Analytics", {"query": "Tell me about Data Analytics"}),
    (6, "What is the capital of France?", {"query": "What is the capital of France?"}),
    (7, "Empty query", {"query": ""}),
]

print("=" * 90)
print("DJANGO REST API VERIFICATION: POST /api/chatbot/search/")
print("=" * 90)

for test_num, name, payload in tests:
    print(f"\n--- TEST {test_num}: {name} ---")
    print(f"Request Payload: {json.dumps(payload)}")
    
    response = client.post(url, payload, format='json')
    print(f"HTTP Status: {response.status_code}")
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))
