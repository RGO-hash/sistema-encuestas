# 🚀 Guía de Inicio Rápido

## Instalación en 5 minutos

### 1. Verificar Python
```bash
python --version  # Debe ser 3.8 o superior
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (macOS/Linux)
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Inicializar Base de Datos
```bash
python init_db.py
```

### 5. Ejecutar la Aplicación
```bash
python run.py
```

✅ **Listo!** Accede a `http://localhost:5000`

---

## 📝 Configuración Inicial

### Cambiar Credenciales Admin
1. Acceder a `http://localhost:5000`
2. Usar: admin@encuestas.com / admin123
3. Cambiar contraseña (agregar en futuras versiones)

### Configurar Email (Opcional)
1. Copiar `.env.example` a `.env`
2. Actualizar credenciales SMTP
3. Para Gmail: generar contraseña de aplicación

---

## 🎯 Flujo Básico de Uso

### Paso 1: Crear Posiciones
```
Dashboard → Posiciones → Nueva Posición
- Presidente
- Vicepresidente
- Tesorero
```

### Paso 2: Agregar Candidatos
```
Dashboard → Candidatos → Nueva Candidato
- Seleccionar posición
- Agregar 2-3 candidatos por posición
```

### Paso 3: Registrar Participantes
```
Dashboard → Participantes → Nuevo Participante
O cargar CSV:
- Descargar plantilla
- Llenar con datos
- Subir archivo
```

### Paso 4: Enviar Invitaciones
```
Dashboard → Participantes → Enviar Invitaciones
```

### Paso 5: Ver Resultados
```
Resultados → Gráficos en tiempo real
- Exportar CSV
- Exportar auditoría
```

---

## 🔧 Solución de Problemas

### Error: "No module named 'flask'"
```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "SQLite database locked"
```bash
# Eliminar base de datos y recrear
rm app.db
python init_db.py
```

### Puerto 5000 en uso
```bash
# Cambiar puerto en run.py o:
python -m flask run --port 5001
```

### Email no funciona
- Verificar credenciales SMTP en `.env`
- Para Gmail: activar "Aplicaciones menos seguras"
- Usar contraseña de aplicación (2FA)

---

## 📚 Recursos Adicionales

- **Documentación completa:** Ver README.md
- **API Reference:** /api/docs (futuro)
- **Logs:** `/logs/app.log`

---

## 🎓 Próximos Pasos

1. Customizar colores en `/app/static/css/main.css`
2. Agregar más campos a participantes
3. Configurar base de datos PostgreSQL
4. Deploying en producción (Heroku, AWS, etc.)

---

¡Disfruta! 🎉
