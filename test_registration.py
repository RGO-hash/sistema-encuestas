#!/usr/bin/env python3
"""Test participant registration system"""
import requests
import json

BASE = 'http://localhost:5000'

print("=" * 60)
print("TESTING PARTICIPANT REGISTRATION SYSTEM")
print("=" * 60)

# Test 1: Register new participant
print("\n[1] Registering new participant...")
register_data = {
    'email': 'juan@example.com',
    'password': 'password123',
    'first_name': 'Juan',
    'last_name': 'Pérez'
}
r = requests.post(f'{BASE}/api/auth/participant/register', json=register_data)
print(f"Status: {r.status_code}")
print(f"Response: {json.dumps(r.json(), indent=2)}")

if r.status_code == 201:
    print("✓ Registration successful")
else:
    print("✗ Registration failed")

# Test 2: Try to register same email again (should fail)
print("\n[2] Trying to register same email again (should fail)...")
r = requests.post(f'{BASE}/api/auth/participant/register', json=register_data)
print(f"Status: {r.status_code}")
print(f"Response: {json.dumps(r.json(), indent=2)}")
if r.status_code != 201:
    print("✓ Correctly rejected duplicate email")
else:
    print("✗ Should have rejected duplicate email")

# Test 3: Try to register with invalid email
print("\n[3] Registering with invalid email (should fail)...")
invalid_data = {
    'email': 'not-an-email',
    'password': 'password123',
    'first_name': 'Test',
    'last_name': 'User'
}
r = requests.post(f'{BASE}/api/auth/participant/register', json=invalid_data)
print(f"Status: {r.status_code}")
print(f"Response: {json.dumps(r.json(), indent=2)}")
if r.status_code != 201:
    print("✓ Correctly rejected invalid email")
else:
    print("✗ Should have rejected invalid email")

# Test 4: Try to register with short password
print("\n[4] Registering with short password (should fail)...")
short_pass_data = {
    'email': 'maria@example.com',
    'password': '123',
    'first_name': 'Maria',
    'last_name': 'García'
}
r = requests.post(f'{BASE}/api/auth/participant/register', json=short_pass_data)
print(f"Status: {r.status_code}")
print(f"Response: {json.dumps(r.json(), indent=2)}")
if r.status_code != 201:
    print("✓ Correctly rejected short password")
else:
    print("✗ Should have rejected short password")

print("\n" + "=" * 60)
print("✓ All tests completed!")
print("=" * 60)
