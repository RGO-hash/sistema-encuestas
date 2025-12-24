#!/usr/bin/env python
"""
Script para ejecutar la aplicación con ngrok automáticamente
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_ngrok_with_flask():
    """Ejecuta Flask y expone a través de ngrok"""
    
    print("=" * 60)
    print("INICIANDO APLICACIÓN CON NGROK")
    print("=" * 60)
    
    # Verificar que ngrok está instalado
    try:
        subprocess.run(['ngrok', '--version'], capture_output=True, check=True)
        print("✓ ngrok está instalado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ ngrok no está instalado")
        print("\nPara instalar ngrok:")
        print("1. Descarga desde: https://ngrok.com/download")
        print("2. O usa: pip install ngrok")
        print("3. Asegúrate de que está en tu PATH")
        sys.exit(1)
    
    # Iniciar Flask en background
    print("\n→ Iniciando servidor Flask...")
    flask_process = subprocess.Popen(
        [sys.executable, 'run.py'],
        cwd=str(Path(__file__).parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Esperar a que Flask se inicie
    time.sleep(3)
    
    if flask_process.poll() is not None:
        print("✗ Error al iniciar Flask")
        stdout, stderr = flask_process.communicate()
        print(f"Error: {stderr.decode()}")
        sys.exit(1)
    
    print("✓ Servidor Flask iniciado en http://127.0.0.1:5000")
    
    # Iniciar ngrok
    print("\n→ Conectando con ngrok...")
    try:
        ngrok_process = subprocess.Popen(
            ['ngrok', 'http', '5000', '--log=stdout'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✓ ngrok conectado")
        print("\n" + "=" * 60)
        print("APLICACIÓN EN EJECUCIÓN")
        print("=" * 60)
        print("Local:  http://127.0.0.1:5000")
        print("ngrok:  Esperando URL...")
        print("\nPulsa Ctrl+C para detener")
        print("=" * 60 + "\n")
        
        # Mostrar logs de ngrok
        for line in ngrok_process.stdout:
            print(line.rstrip())
            # Buscar la URL de ngrok
            if 'Forwarding' in line and 'http' in line:
                # Extraer URL
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.startswith('http'):
                        print(f"\n✓ URL PÚBLICA DISPONIBLE: {part}\n")
                        break
        
        # Si ngrok se cierra, mantener el script en ejecución
        ngrok_process.wait()
        
    except KeyboardInterrupt:
        print("\n\n→ Deteniendo aplicación...")
        ngrok_process.terminate()
        flask_process.terminate()
        time.sleep(1)
        ngrok_process.kill()
        flask_process.kill()
        print("✓ Aplicación detenida")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Error con ngrok: {e}")
        flask_process.terminate()
        sys.exit(1)

if __name__ == '__main__':
    run_ngrok_with_flask()
