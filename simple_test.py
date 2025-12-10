#!/usr/bin/env python3
"""Test API endpoints simple"""
import requests
import json
import sys

BASE = 'http://localhost:5000'

# 1. Login
print("[1] LOGIN...")
r = requests.post(f'{BASE}/api/auth/login', json={
    'email': 'admin@encuestas.com',
    'password': 'admin123'
})
print(f"Status: {r.status_code}")
data = r.json()
print(f"Response: {json.dumps(data, indent=2)[:300]}")

if r.status_code != 200:
    print("❌ Login failed!")
    sys.exit(1)

token = data.get('access_token')
print(f"✓ Token: {token[:30]}...\n")

headers = {'Authorization': f'Bearer {token}'}

# 2. Get participants
print("[2] GET /api/participants?page=1")
r = requests.get(f'{BASE}/api/participants?page=1', headers=headers)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}\n")

# 3. Create participant
print("[3] POST /api/participants")
r = requests.post(f'{BASE}/api/participants', 
    json={'email': 'new@test.com', 'first_name': 'Juan', 'last_name': 'Perez'},
    headers=headers)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:300]}\n")

# 4. Get positions
print("[4] GET /api/survey/positions")
r = requests.get(f'{BASE}/api/survey/positions', headers=headers)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}\n")

# 5. Create position
print("[5] POST /api/survey/positions")
r = requests.post(f'{BASE}/api/survey/positions',
    json={'name': 'Nueva Pos', 'description': 'Desc'},
    headers=headers)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:300]}\n")

print("✓ All tests completed!")
