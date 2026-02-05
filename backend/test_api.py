"""測試 generate-today API"""
import requests
import json

url = "http://localhost:8000/api/v1/schedules/generate-today"
body = {"force": False}

try:
    response = requests.post(url, json=body, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Content: {response.text}")
    print(f"Response JSON: {response.json()}")
except Exception as e:
    print(f"Error: {e}")

