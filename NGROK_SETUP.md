# Ejecutar Proyecto con ngrok

Esta guía explica cómo ejecutar automáticamente tu proyecto en ngrok para exponerlo a internet.

## ¿Qué es ngrok?

ngrok crea un túnel seguro a tu servidor local, permitiendo que personas desde internet accedan a tu aplicación sin necesidad de desplegarlo en la nube.

**Ventajas:**
- ✅ Fácil de usar
- ✅ Genera URL pública automáticamente
- ✅ Útil para testing, webhooks y compartir demo
- ✅ Soporta HTTPS por defecto

## Instalación de ngrok

### Opción 1: Descarga desde el sitio web
1. Ve a https://ngrok.com/download
2. Descarga la versión para Windows
3. Extrae el archivo `ngrok.exe`
4. Coloca `ngrok.exe` en una carpeta que esté en tu PATH (ej: `C:\Program Files\ngrok`)

### Opción 2: Instalar con pip
```bash
pip install ngrok-cli
```

### Opción 3: Instalar con chocolatey (si tienes)
```bash
choco install ngrok
```

## Verificar instalación

Abre PowerShell o CMD y ejecuta:
```bash
ngrok --version
```

Deberías ver algo como: `ngrok version 3.x.x`

## Ejecutar con ngrok

### Método 1: Script Python (Recomendado)
```bash
python run_with_ngrok.py
```

### Método 2: Script Batch (Windows)
```bash
run_with_ngrok.bat
```

O simplemente haz doble clic en el archivo desde el Explorador de Windows.

### Método 3: Comando directo
```bash
python run.py &
ngrok http 5000
```

## Uso de ngrok

Una vez ejecutado, verás algo como:

```
========================================
APLICACION EN EJECUCION
========================================
Local:  http://127.0.0.1:5000

Forwarding                    https://abc123.ngrok.io -> http://127.0.0.1:5000
Introspection                 http://127.0.0.1:4040
```

**URLs disponibles:**
- `http://127.0.0.1:5000` - Solo desde tu máquina
- `https://abc123.ngrok.io` - Desde cualquier lugar del mundo

## Acceder a tu aplicación

1. **Localmente**: http://127.0.0.1:5000
2. **Desde otra máquina**: https://abc123.ngrok.io (la URL cambia cada vez que reconectas)

## Dashboard de ngrok

Puedes ver los requests en tiempo real:
- http://127.0.0.1:4040

## Configuración avanzada

### Autenticación (Cuenta ngrok)

Para obtener URLs estables (sin cambiar cada vez):

1. Crea una cuenta en https://ngrok.com/
2. Obtén tu auth token
3. Ejecuta:
   ```bash
   ngrok config add-authtoken <tu-token>
   ```

### Dominio personalizado (Plan profesional)

Con una cuenta profesional puedes usar un dominio personalizado:
```bash
ngrok http 5000 --domain=miapp.ngrok.io
```

## Detener la aplicación

Pulsa **Ctrl+C** en la terminal donde está ejecutándose ngrok.

## Solución de problemas

### ngrok no está en PATH
- Descarga ngrok y colócalo en `C:\Program Files\ngrok`
- O agrega la carpeta donde está ngrok a las variables de entorno PATH

### Puerto 5000 ya en uso
Cambia el puerto en `run.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
```

Luego ejecuta:
```bash
ngrok http 5001
```

### Errores de conexión
- Verifica que tienes internet
- Revisa que el firewall no bloquea ngrok
- Reinicia ngrok

## Notas importantes

⚠️ **Seguridad:**
- La URL de ngrok es pública, cualquiera puede acceder
- Usa autenticación en tu aplicación
- No expongas datos sensibles
- Las URLs cambian cada vez que reconectas (a menos que uses plan profesional)

⚠️ **Límites (plan gratuito):**
- 1 URL por vez
- 40 conexiones/minuto
- Sesiones de 2 horas
- Bandwidth limitado

Para más información: https://ngrok.com/docs
