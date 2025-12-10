#!/usr/bin/env python
"""
Script de configuración automática para el Sistema de Votación
Instala dependencias, inicializa la base de datos y prepara el entorno
"""

import os
import sys
import subprocess
import platform

def print_header(text):
    """Imprimir encabezado"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"▶ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} - OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} - ERROR")
        print(f"  {e.stderr}")
        return False

def main():
    print_header("Sistema de Votación - Configuración Automática")
    
    # Detectar sistema operativo
    is_windows = platform.system() == "Windows"
    
    # Paso 1: Verificar Python
    print("1️⃣  Verificando Python...")
    python_version = sys.version.split()[0]
    print(f"  Python {python_version} ✓\n")
    
    # Paso 2: Crear entorno virtual
    print_header("2️⃣  Configurando Entorno Virtual")
    
    if not os.path.exists("venv"):
        run_command(f"{sys.executable} -m venv venv", "Crear entorno virtual")
    else:
        print("✓ Entorno virtual ya existe\n")
    
    # Paso 3: Instalar dependencias
    print_header("3️⃣  Instalando Dependencias")
    
    if is_windows:
        pip_cmd = "venv\\Scripts\\pip install -r requirements.txt"
    else:
        pip_cmd = "source venv/bin/activate && pip install -r requirements.txt"
    
    run_command(pip_cmd, "Instalar paquetes")
    
    # Paso 4: Inicializar base de datos
    print_header("4️⃣  Inicializando Base de Datos")
    
    if is_windows:
        python_cmd = "venv\\Scripts\\python init_db.py"
    else:
        python_cmd = "source venv/bin/activate && python init_db.py"
    
    run_command(python_cmd, "Inicializar base de datos")
    
    # Paso 5: Crear archivo .env si no existe
    print_header("5️⃣  Configurando Variables de Entorno")
    
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""FLASK_ENV=development
FLASK_DEBUG=True
JWT_SECRET_KEY=tu-clave-secreta-super-segura-aqui
DATABASE_URL=sqlite:///instance/voting_system.db
""")
        print("✓ Archivo .env creado\n")
    else:
        print("✓ Archivo .env ya existe\n")
    
    # Resumen final
    print_header("✅ Configuración Completada")
    
    print("Tu sistema de votación está listo para ejecutarse.\n")
    
    if is_windows:
        print("Para iniciar el servidor, ejecuta:")
        print("  venv\\Scripts\\activate")
        print("  python run.py")
    else:
        print("Para iniciar el servidor, ejecuta:")
        print("  source venv/bin/activate")
        print("  python run.py")
    
    print("\nLuego abre tu navegador en: http://127.0.0.1:5000")
    print("\nCredenciales por defecto:")
    print("  Email: admin@test.com")
    print("  Contraseña: test123\n")

if __name__ == "__main__":
    main()
