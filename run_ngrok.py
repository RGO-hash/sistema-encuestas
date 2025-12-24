#!/usr/bin/env python
"""
Script para ejecutar la aplicación con ngrok automáticamente usando pyngrok
"""

import os
import sys
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Ejecuta Flask y expone a través de ngrok"""
    
    print("\n" + "=" * 70)
    print(" " * 15 + "INICIANDO APLICACIÓN CON NGROK")
    print("=" * 70 + "\n")
    
    # Intentar importar pyngrok
    try:
        from pyngrok import ngrok
        print("✓ pyngrok importado correctamente\n")
    except ImportError:
        print("✗ pyngrok no está instalado")
        print("\nInstalando pyngrok...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok"])
        from pyngrok import ngrok
        print("✓ pyngrok instalado correctamente\n")
    
    # Importar la aplicación Flask
    try:
        from app import create_app
        print("✓ Aplicación Flask importada correctamente\n")
    except ImportError as e:
        print(f"✗ Error al importar la aplicación: {e}")
        sys.exit(1)
    
    # Crear la aplicación
    app = create_app('development')
    
    # Configurar ngrok
    print("→ Configurando ngrok...")
    try:
        # Obtener URL pública
        public_url = ngrok.connect(5000)
        print(f"✓ ngrok conectado\n")
    except Exception as e:
        print(f"✗ Error al conectar ngrok: {e}")
        print("\nAsegúrate de que:")
        print("1. Tienes internet")
        print("2. ngrok está instalado: pip install pyngrok")
        print("3. El puerto 5000 está disponible")
        sys.exit(1)
    
    # Mostrar información
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
    try:
        app.run(host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\n\n→ Deteniendo aplicación...")
        ngrok.disconnect(public_url)
        print("✓ Aplicación detenida")
        sys.exit(0)

if __name__ == '__main__':
    main()
