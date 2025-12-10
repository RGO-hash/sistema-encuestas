#!/usr/bin/env python3
"""
Script de testing rápido para validar todas las funcionalidades implementadas.
Ejecutar con: python test_new_features.py
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.participant_token = None
        self.test_email = f"test_{int(time.time())}@ejemplo.com"
    
    def print_header(self, title):
        print(f"\n{BLUE}{'='*60}")
        print(f"{title}")
        print(f"{'='*60}{END}\n")
    
    def print_test(self, name, status, details=""):
        icon = f"{GREEN}✓{END}" if status else f"{RED}✗{END}"
        print(f"{icon} {name}")
        if details:
            print(f"  {YELLOW}└─ {details}{END}")
    
    def test_register_participant(self):
        """Test: Registro de participante con email único"""
        self.print_header("1️⃣ REGISTRO DE PARTICIPANTE")
        
        payload = {
            "email": self.test_email,
            "first_name": "Test",
            "last_name": "Usuario",
            "password": "TestPass123",
            "password_confirm": "TestPass123"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/participant-auth/register",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                data = response.json()
                self.participant_token = data.get('access_token')
                self.print_test("✓ Registro exitoso", True, f"Email: {self.test_email}")
                self.passed += 1
            else:
                self.print_test("✗ Registro fallido", False, f"Status: {response.status_code}")
                print(f"  Respuesta: {response.json()}")
                self.failed += 1
        
        except Exception as e:
            self.print_test("✗ Error en registro", False, str(e))
            self.failed += 1
    
    def test_duplicate_email(self):
        """Test: Validación de email único"""
        self.print_header("2️⃣ VALIDACIÓN DE EMAIL ÚNICO")
        
        payload = {
            "email": self.test_email,
            "first_name": "Otro",
            "last_name": "Usuario",
            "password": "TestPass123",
            "password_confirm": "TestPass123"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/participant-auth/register",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 409:
                self.print_test("✓ Email duplicado rechazado", True, "Status 409 Conflict")
                self.passed += 1
            else:
                self.print_test("✗ Email duplicado permitido", False, f"Status: {response.status_code}")
                self.failed += 1
        
        except Exception as e:
            self.print_test("✗ Error en validación", False, str(e))
            self.failed += 1
    
    def test_check_email_availability(self):
        """Test: Verificación AJAX de email disponible"""
        self.print_header("3️⃣ VERIFICACIÓN DE DISPONIBILIDAD DE EMAIL (AJAX)")
        
        try:
            # Email que no existe
            response = requests.post(
                f"{BASE_URL}/api/participant-auth/check-email",
                json={"email": f"unique_{int(time.time())}@ejemplo.com"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('available'):
                    self.print_test("✓ Email disponible detectado", True)
                    self.passed += 1
                else:
                    self.print_test("✗ Email disponible no detectado", False)
                    self.failed += 1
            else:
                self.print_test("✗ Error en verificación", False, f"Status: {response.status_code}")
                self.failed += 1
        
        except Exception as e:
            self.print_test("✗ Error AJAX", False, str(e))
            self.failed += 1
    
    def test_login_participant(self):
        """Test: Login de participante"""
        self.print_header("4️⃣ LOGIN DE PARTICIPANTE")
        
        payload = {
            "email": self.test_email,
            "password": "TestPass123"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/participant-auth/login",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.participant_token = data.get('access_token')
                self.print_test("✓ Login exitoso", True, "Token obtenido")
                self.passed += 1
            else:
                self.print_test("✗ Login fallido", False, f"Status: {response.status_code}")
                self.failed += 1
        
        except Exception as e:
            self.print_test("✗ Error en login", False, str(e))
            self.failed += 1
    
    def test_get_available_positions(self):
        """Test: Obtener posiciones disponibles para candidaturas"""
        self.print_header("5️⃣ POSICIONES DISPONIBLES PARA CANDIDATOS")
        
        if not self.participant_token:
            self.print_test("⊘ Skipped (sin token)", False, "Requiere token válido")
            return
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/candidates/available-positions",
                headers={"Authorization": f"Bearer {self.participant_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                positions_count = len(data.get('positions', []))
                self.print_test("✓ Posiciones obtenidas", True, f"Total: {positions_count}")
                self.passed += 1
            else:
                self.print_test("✗ Error obteniendo posiciones", False, f"Status: {response.status_code}")
                self.failed += 1
        
        except Exception as e:
            self.print_test("✗ Error en solicitud", False, str(e))
            self.failed += 1
    
    def test_get_active_surveys(self):
        """Test: Obtener encuestas activas para votar"""
        self.print_header("6️⃣ ENCUESTAS ACTIVAS PARA VOTACIÓN")
        
        if not self.participant_token:
            self.print_test("⊘ Skipped (sin token)", False, "Requiere token válido")
            return
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/voting/active-surveys",
                headers={"Authorization": f"Bearer {self.participant_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                surveys_count = len(data.get('surveys', []))
                self.print_test("✓ Encuestas obtenidas", True, f"Total: {surveys_count}")
                self.passed += 1
            else:
                self.print_test("✗ Error obteniendo encuestas", False, f"Status: {response.status_code}")
                self.failed += 1
        
        except Exception as e:
            self.print_test("✗ Error en solicitud", False, str(e))
            self.failed += 1
    
    def test_get_vote_status(self):
        """Test: Verificar estado de votación"""
        self.print_header("7️⃣ ESTADO DE VOTACIÓN")
        
        if not self.participant_token:
            self.print_test("⊘ Skipped (sin token)", False, "Requiere token válido")
            return
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/voting/vote-status",
                headers={"Authorization": f"Bearer {self.participant_token}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                has_voted = data.get('has_voted', False)
                status = "Ya votó" if has_voted else "Pendiente"
                self.print_test("✓ Estado obtenido", True, f"Estado: {status}")
                self.passed += 1
            else:
                self.print_test("✗ Error obteniendo estado", False, f"Status: {response.status_code}")
                self.failed += 1
        
        except Exception as e:
            self.print_test("✗ Error en solicitud", False, str(e))
            self.failed += 1
    
    def test_public_results(self):
        """Test: Resultados públicos (sin autenticación)"""
        self.print_header("8️⃣ RESULTADOS PÚBLICOS (SIN AUTENTICACIÓN)")
        
        try:
            response = requests.get(f"{BASE_URL}/api/results/summary")
            
            if response.status_code == 200:
                data = response.json()
                total_votes = data.get('summary', {}).get('total_votes_cast', 0)
                self.print_test("✓ Resultados públicos accesibles", True, f"Votos: {total_votes}")
                self.passed += 1
            else:
                self.print_test("✗ Error obteniendo resultados", False, f"Status: {response.status_code}")
                self.failed += 1
        
        except Exception as e:
            self.print_test("✗ Error en solicitud", False, str(e))
            self.failed += 1
    
    def test_statistics(self):
        """Test: Estadísticas generales"""
        self.print_header("9️⃣ ESTADÍSTICAS GENERALES")
        
        try:
            response = requests.get(f"{BASE_URL}/api/results/statistics")
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('statistics', {})
                participation = stats.get('participation_rate', 0)
                self.print_test("✓ Estadísticas obtenidas", True, 
                              f"Participación: {participation}%")
                self.passed += 1
            else:
                self.print_test("✗ Error obteniendo estadísticas", False, f"Status: {response.status_code}")
                self.failed += 1
        
        except Exception as e:
            self.print_test("✗ Error en solicitud", False, str(e))
            self.failed += 1
    
    def test_pages_load(self):
        """Test: Páginas HTML cargan correctamente"""
        self.print_header("🔟 PÁGINAS HTML")
        
        pages = [
            ("/registro", "Registro de Participante"),
            ("/login-participante", "Login de Participante"),
            ("/votar", "Votación"),
            ("/resultados", "Resultados Públicos"),
        ]
        
        for path, name in pages:
            try:
                response = requests.get(f"{BASE_URL}{path}")
                if response.status_code == 200:
                    self.print_test(f"✓ {name}", True, f"GET {path}")
                    self.passed += 1
                else:
                    self.print_test(f"✗ {name}", False, f"Status: {response.status_code}")
                    self.failed += 1
            except Exception as e:
                self.print_test(f"✗ {name}", False, str(e))
                self.failed += 1
    
    def run_all_tests(self):
        """Ejecutar todos los tests"""
        print(f"\n{BLUE}{'#'*60}")
        print(f"# TESTING - SISTEMA DE ENCUESTAS")
        print(f"# Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#'*60}{END}\n")
        
        self.test_register_participant()
        self.test_duplicate_email()
        self.test_check_email_availability()
        self.test_login_participant()
        self.test_get_available_positions()
        self.test_get_active_surveys()
        self.test_get_vote_status()
        self.test_public_results()
        self.test_statistics()
        self.test_pages_load()
        
        self.print_summary()
    
    def print_summary(self):
        """Imprimir resumen de tests"""
        self.print_header("RESUMEN DE TESTS")
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{GREEN}Pasados:  {self.passed}/{total}{END}")
        print(f"{RED}Fallidos: {self.failed}/{total}{END}")
        print(f"Éxito:    {percentage:.1f}%\n")
        
        if self.failed == 0:
            print(f"{GREEN}{'='*60}")
            print(f"🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
            print(f"{'='*60}{END}\n")
        else:
            print(f"{RED}{'='*60}")
            print(f"⚠️  ALGUNOS TESTS FALLARON")
            print(f"{'='*60}{END}\n")

if __name__ == "__main__":
    runner = TestRunner()
    runner.run_all_tests()
