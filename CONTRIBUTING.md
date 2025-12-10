# 🤝 Contribuyendo al Proyecto

¡Gracias por tu interés en contribuir al Sistema de Votación Electrónica!

## 📋 Cómo Reportar Bugs

Antes de crear un reporte, verifica que el issue no exista.

Cuando reportes un bug, incluye:
- Descripción clara del problema
- Pasos para reproducirlo
- Comportamiento observado
- Comportamiento esperado
- Screenshots si es aplicable
- Tu entorno (OS, Python version, etc.)

## 🎯 Proposición de Mejoras

Las sugerencias de mejoras son bienvenidas. Incluye:
- Caso de uso claro
- Descripción de la solución propuesta
- Ejemplos de cómo funcionaría
- Posibles desventajas

## 💻 Proceso de Contribución

### 1. Fork el Proyecto
```bash
git clone https://github.com/tu-usuario/sistema-encuestas.git
cd sistema-encuestas
```

### 2. Crear Rama Feature
```bash
git checkout -b feature/tu-feature-name
```

### 3. Hacer Cambios
- Sigue el estilo de código existente
- Añade tests si es aplicable
- Actualiza documentación

### 4. Commit Cambios
```bash
git add .
git commit -m "Descripción clara de los cambios"
```

### 5. Push a tu Fork
```bash
git push origin feature/tu-feature-name
```

### 6. Crear Pull Request
- Describe qué hace tu PR
- Referencia issues relacionados
- Asegúrate que pasa todos los tests

## 🎨 Estilo de Código

### Python
```python
# Seguir PEP 8
def funcion_con_nombre_claro(parametro):
    """Docstring explicativo."""
    return resultado
```

### JavaScript
```javascript
// camelCase para variables/funciones
// UPPER_CASE para constantes
const miVariable = 5;
const CONSTANTE = 10;

function funcionClara() {
    // comentarios cuando sea necesario
}
```

### HTML/CSS
```html
<!-- Clases claras y descriptivas -->
<div class="position-voting-section">
    <div class="candidate-card">
```

## 🧪 Testing

Antes de enviar un PR, asegúrate que:

```bash
# Los tests pasen
python test_api.py

# No haya errores de sintaxis
python -m py_compile app/routes/*.py

# El servidor inicie sin errores
python run.py  # Ctrl+C para salir
```

## 📚 Documentación

Si añades nuevas funcionalidades:
- Actualiza README.md
- Añade docstrings en Python
- Documenta endpoints de API
- Incluye ejemplos de uso

## 🚀 Áreas de Contribución

Ideas para contribuir:
- 🐛 Reportar y corregir bugs
- 🎨 Mejorar interfaz de usuario
- 📝 Mejorar documentación
- ✅ Añadir tests
- 🌍 Traducción a otros idiomas
- 📊 Nuevas características de reportes
- 🔐 Mejoras de seguridad
- ⚡ Optimizaciones de rendimiento

## 📋 Checklist para Pull Requests

- [ ] Mi código sigue el estilo del proyecto
- [ ] He actualizado la documentación
- [ ] Añadí tests para nuevas funcionalidades
- [ ] Mis cambios generan warnings en tests
- [ ] Mi rama está actualizada con main

## 💬 Comunicación

- Usa Issues para bugs y features
- Usa Discussions para preguntas
- Sé respetuoso y constructivo
- Mantén conversaciones en público

## 📄 Licencia

Por contribuir, aceptas que tu código esté bajo MIT License.

---

¡Gracias por ayudar a mejorar el proyecto! 🎉
