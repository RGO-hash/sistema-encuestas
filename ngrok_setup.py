#!/usr/bin/env python
"""
Script para configurar ngrok y ejecutar la aplicación
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_ngrok():
    """Configura ngrok con tu authtoken"""
    
    print("\n" + "=" * 70)
    print(" " * 20 + "CONFIGURACIÓN DE NGROK")
    print("=" * 70 + "\n")
    
    print("Para usar ngrok, necesitas una cuenta (gratuita):\n")
    print("1. Ve a: https://ngrok.com/signup")
    print("2. Crea tu cuenta (es gratis)")
    print("3. Copia tu AUTH TOKEN desde el dashboard")
    print("4. Pégalo aquí:\n")
    
    authtoken = input("Ingresa tu AUTH TOKEN: ").strip()
    
    if not authtoken:
        print("\n✗ No ingresaste un token")
        return False
    
    try:
        from pyngrok import ngrok
        ngrok.set_auth_token(authtoken)
        print("\n✓ Token configurado correctamente")
        return True
    except Exception as e:
        print(f"\n✗ Error al configurar el token: {e}")
        return False

def run_with_ngrok():
    """Ejecuta la aplicación con ngrok"""
    
    print("\n" + "=" * 70)
    print(" " * 15 + "INICIANDO APLICACIÓN CON NGROK")
    print("=" * 70 + "\n")
    
    try:
        from pyngrok import ngrok
        from app import create_app
        
        print("✓ Módulos importados correctamente\n")
        
        # Crear y configurar la aplicación
        app = create_app('development')
        
        print("→ Conectando con ngrok...")
        public_url = ngrok.connect(5000)
        print(f"✓ ngrok conectado\n")
        
        print("=" * 70)
        print(" " * 20 + "APLICACIÓN EN EJECUCIÓN")
        print("=" * 70)
        print(f"\n📱 URL Local:     http://127.0.0.1:5000")
        print(f"🌐 URL Pública:   {public_url}")
        print(f"📊 Dashboard:     http://127.0.0.1:4040")
        print("\n💡 Comparte tu URL pública para que otros accedan a tu aplicación")
        print("⚠️  La URL cambia cada vez que reconectas (a menos que uses plan profesional)")
        print("\n🛑 Pulsa Ctrl+C para detener la aplicación\n")
        print("=" * 70 + "\n")
        
        # Ejecutar la aplicación
        app.run(host='127.0.0.1', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n\n→ Deteniendo aplicación...")
        try:
            ngrok.kill()
        except:
            pass
        print("✓ Aplicación detenida")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nSolución: Asegúrate de que el token sea correcto")

def main():
    try:
        from pyngrok import ngrok
    except ImportError:
        print("\n→ Instalando dependencias necesarias...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok"])
        from pyngrok import ngrok
    
    # Verificar si ya hay token configurado
    try:
        from pyngrok import ngrok
        # Intentar conectar para ver si hay token
        test = ngrok.connect(5000, "http", bind_tls=False)
        ngrok.disconnect(test)
        run_with_ngrok()
    except Exception as e:
        if "authentication" in str(e).lower():
            if setup_ngrok():
                run_with_ngrok()
            else:
                print("\n✗ No se pudo configurar ngrok")
                sys.exit(1)
        else:
            raise

if __name__ == '__main__':
    main()
