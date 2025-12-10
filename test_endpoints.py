import requests
import json

# 1. Login
print("=== LOGIN ===")
r = requests.post('http://localhost:5000/api/auth/login', json={
    'email': 'admin@encuestas.com',
    'password': 'admin123'
})
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

if r.status_code == 200:
    token = r.json()['access_token']
    print(f"\nToken obtained: {token[:40]}...")
    
    # 2. Try GET participants with token
    print("\n=== GET PARTICIPANTS WITH TOKEN ===")
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get('http://localhost:5000/api/participants?page=1', headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:300]}")
    
    # 3. Try creating participant
    print("\n=== CREATE PARTICIPANT ===")
    data = {
        'email': 'test.new@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
    r = requests.post('http://localhost:5000/api/participants', json=data, headers=headers)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")

