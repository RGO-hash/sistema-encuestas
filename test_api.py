import requests
import json

# Login
print("Testing API...")
response = requests.post('http://localhost:5000/api/auth/login', json={
    'email': 'admin@encuestas.com',
    'password': 'admin123'
})
print('Login Response:', response.status_code)
if response.status_code == 200:
    data = response.json()
    token = data.get('access_token')
    print('Token received:', token[:20] + '...')
    
    # Try to get participants
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('http://localhost:5000/api/participants?page=1', headers=headers)
    print('Participants Response:', response.status_code)
    print('Response:', response.text[:300])
    
    # Try to create participant
    participant_data = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
    response = requests.post('http://localhost:5000/api/participants', json=participant_data, headers=headers)
    print('Create Participant Response:', response.status_code)
    print('Response:', response.text)
else:
    print('Login failed:', response.text)
