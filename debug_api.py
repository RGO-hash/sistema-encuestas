#!/usr/bin/env python
"""Script para depurar errores en API"""
import requests
import json
import sys

BASE_URL = 'http://localhost:5000'

def test_api():
    print("=" * 60)
    print("DEPURACIÓN DE API - SISTEMA DE ENCUESTAS")
    print("=" * 60)
    
    # 1. Login
    print("\n[1] Intentando login...")
    response = requests.post(f'{BASE_URL}/api/auth/login', json={
        'email': 'admin@encuestas.com',
        'password': 'admin123'
    })
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:300]}")
    
    if response.status_code != 200:
        print("❌ Login falló - no se puede continuar")
        return
    
    data = response.json()
    token = data.get('access_token')
    print(f"✓ Token obtenido: {token[:40]}...")
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. Get participants
    print("\n[2] Obteniendo participantes...")
    response = requests.get(f'{BASE_URL}/api/participants?page=1', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:300]}")
    
    # 3. Create participant
    print("\n[3] Creando nuevo participante...")
    participant_data = {
        'email': 'nuevo@test.com',
        'first_name': 'Juan',
        'last_name': 'Pérez'
    }
    response = requests.post(f'{BASE_URL}/api/participants', 
                            json=participant_data, 
                            headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    print(f"Full body: {response.content}")
    
    # 4. Get positions
    print("\n[4] Obteniendo posiciones...")
    response = requests.get(f'{BASE_URL}/api/survey/positions', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:300]}")
    
    # 5. Create position
    print("\n[5] Creando nueva posición...")
    position_data = {
        'title': 'Nueva Posición',
        'description': 'Descripción'
    }
    response = requests.post(f'{BASE_URL}/api/survey/positions', 
                            json=position_data, 
                            headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    # 6. Get candidates
    print("\n[6] Obteniendo candidatos...")
    response = requests.get(f'{BASE_URL}/api/survey/candidates?position_id=1', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:300]}")
    
    # 7. Create candidate
    print("\n[7] Creando nuevo candidato...")
    candidate_data = {
        'position_id': 1,
        'name': 'Nuevo Candidato',
        'description': 'Descripción'
    }
    response = requests.post(f'{BASE_URL}/api/survey/candidates', 
                            json=candidate_data, 
                            headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")

if __name__ == '__main__':
    test_api()
