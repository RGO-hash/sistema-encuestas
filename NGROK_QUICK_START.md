# 🌐 Ejecutar con ngrok

## Opción rápida: Script automático

```bash
python ngrok_setup.py
```

Este script:
1. Te pedirá que ingreses tu authtoken de ngrok (si no lo has configurado)
2. Iniciará el servidor automáticamente
3. Te mostrará tu URL pública

## Pasos para obtener tu authtoken

1. **Crea una cuenta (gratuita)** en https://ngrok.com/signup
2. **Accede a tu dashboard** en https://dashboard.ngrok.com
3. **Copia tu AUTH TOKEN** de la sección "Your Authtoken"
4. **Pégalo cuando el script lo pida**

## ¿Qué sucede después?

Verás algo como:

```
========================================
            APLICACIÓN EN EJECUCIÓN
========================================

📱 URL Local:     http://127.0.0.1:5000
🌐 URL Pública:   https://abc123.ngrok.io
📊 Dashboard:     http://127.0.0.1:4040

💡 Comparte tu URL pública para que otros accedan a tu aplicación
⚠️  La URL cambia cada vez que reconectas

🛑 Pulsa Ctrl+C para detener
```

## URLs disponibles

- **Local**: `http://127.0.0.1:5000` - Solo desde tu máquina
- **Pública**: `https://abc123.ngrok.io` - Desde cualquier lugar
- **Dashboard**: `http://127.0.0.1:4040` - Ver requests en tiempo real

## Instalación manual

Si quieres usar ngrok directamente:

1. **Instalar pyngrok**:
   ```bash
   pip install pyngrok
   ```

2. **Configurar token**:
   ```bash
   python -c "from pyngrok import ngrok; ngrok.set_auth_token('tu_token_aqui')"
   ```

3. **Ejecutar**:
   ```bash
   python run.py &
   python run_ngrok.py
   ```

## Alternativa: ngrok directo

Si tienes ngrok instalado en tu sistema:

1. **Terminal 1** - Ejecuta Flask:
   ```bash
   python run.py
   ```

2. **Terminal 2** - Expone con ngrok:
   ```bash
   ngrok http 5000
   ```

## Solución de problemas

### "Authentication required"
- Asegúrate de que tienes una cuenta en https://ngrok.com
- Obtén tu AUTH TOKEN del dashboard
- Ejecuta: `python ngrok_setup.py`

### Puerto 5000 ocupado
Cambia el puerto en `run.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

Luego ejecuta con:
```bash
ngrok http 5001
```

### No tengo internet
ngrok requiere conexión a internet para funcionar

## Notas

✅ **Ventajas de ngrok:**
- Expone tu app a internet sin hosting
- URL pública automática
- HTTPS incluido
- Fácil testing remoto

⚠️ **Plan gratuito tiene límites:**
- URL cambia cada reconexión (a menos que pagues)
- 40 conexiones/minuto
- 2 horas de sesión máximo
- Bandwidth limitado

## Más información

- https://ngrok.com/docs
- https://github.com/ngrokc/pyngrok
