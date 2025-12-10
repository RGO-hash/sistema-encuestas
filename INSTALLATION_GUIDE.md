# 📦 Guía de Instalación y Despliegue - Sistema de Votación Electrónica

## 🌐 Opciones de Ejecución

Elige la opción que mejor se adapte a tu entorno:

---

## Opción 1: Ejecución Local (Recomendado para Desarrollo)

### Requisitos Previos
- Git
- Python 3.8 o superior
- pip

### Pasos

#### 1. Clonar el Repositorio
```bash
git clone https://github.com/RGO-hash/sistema-encuestas.git
cd sistema-encuestas
```

#### 2. Crear Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### 4. Inicializar Base de Datos
```bash
python init_db.py
```

#### 5. Ejecutar Servidor
```bash
python run.py
```

#### 6. Acceder a la Aplicación
Abre tu navegador en: **http://127.0.0.1:5000**

**Tiempo total:** ~5 minutos

---

## Opción 2: Configuración Automática (Windows)

### Pasos Rápidos

#### 1. Clonar y Navegar
```bash
git clone https://github.com/RGO-hash/sistema-encuestas.git
cd sistema-encuestas
```

#### 2. Ejecutar Script de Instalación
```bash
python setup.py
```

El script automáticamente:
- ✓ Verifica Python
- ✓ Crea entorno virtual
- ✓ Instala dependencias
- ✓ Inicializa base de datos
- ✓ Configura variables de entorno

#### 3. Iniciar Servidor
```bash
venv\Scripts\activate
python run.py
```

**Tiempo total:** ~8 minutos

---

## Opción 3: Docker (Recomendado para Producción)

### Requisitos Previos
- Git
- Docker
- Docker Compose

### Pasos

#### 1. Clonar el Repositorio
```bash
git clone https://github.com/RGO-hash/sistema-encuestas.git
cd sistema-encuestas
```

#### 2. Construir y Ejecutar con Docker Compose
```bash
docker-compose up --build
```

#### 3. Acceder a la Aplicación
Abre tu navegador en: **http://localhost:5000**

#### 4. Detener Contenedor
```bash
docker-compose down
```

**Ventajas:**
- ✓ Entorno aislado
- ✓ Sin conflictos de dependencias
- ✓ Fácil de desplegar en producción
- ✓ Funciona en cualquier máquina

**Tiempo total:** ~10 minutos (primera vez)

---

## Opción 4: Deployment en Heroku

### Requisitos Previos
- Cuenta de Heroku (gratis en heroku.com)
- Heroku CLI instalado

### Pasos

#### 1. Clonar y Navegar
```bash
git clone https://github.com/RGO-hash/sistema-encuestas.git
cd sistema-encuestas
```

#### 2. Login en Heroku
```bash
heroku login
```

#### 3. Crear Aplicación
```bash
heroku create nombre-de-tu-app
```

#### 4. Configurar Variables de Entorno
```bash
heroku config:set JWT_SECRET_KEY=tu-clave-secreta-aqui
heroku config:set FLASK_ENV=production
```

#### 5. Desplegar
```bash
git push heroku main
```

#### 6. Inicializar Base de Datos
```bash
heroku run python init_db.py
```

#### 7. Abrir Aplicación
```bash
heroku open
```

**Tu aplicación estará en:** `https://nombre-de-tu-app.herokuapp.com`

---

## Opción 5: Deployment en AWS

### Requisitos Previos
- Cuenta AWS (incluye free tier)
- AWS CLI instalado
- Conocimiento básico de AWS

### Pasos Básicos

#### 1. Usar Elastic Beanstalk
```bash
# Instalar EB CLI
pip install awsebcli

# Inicializar aplicación
eb init -p python-3.11 sistema-votacion

# Crear entorno
eb create votacion-env

# Desplegar
eb deploy
```

#### 2. Configurar Base de Datos RDS (Opcional)
- Usar SQLite para desarrollo
- Cambiar a PostgreSQL para producción
- Actualizar `DATABASE_URL` en variables de entorno

#### 3. Abrir Aplicación
```bash
eb open
```

---

## Opción 6: Deployment en Azure

### Requisitos Previos
- Cuenta Azure
- Azure CLI instalado

### Pasos

#### 1. Login en Azure
```bash
az login
```

#### 2. Crear Grupo de Recursos
```bash
az group create --name votacion-rg --location eastus
```

#### 3. Crear App Service
```bash
az appservice plan create --name votacion-plan --resource-group votacion-rg --sku B1 --is-linux
az webapp create --resource-group votacion-rg --plan votacion-plan --name nombre-de-tu-app --runtime "PYTHON|3.11"
```

#### 4. Desplegar desde GitHub
```bash
az webapp deployment github-actions add --resource-group votacion-rg --name nombre-de-tu-app --repo usuario/repo --branch main --github-token TOKEN
```

---

## 🔧 Troubleshooting

### Problema: Puerto 5000 ya está en uso
**Solución:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :5000
kill -9 <PID>

# O cambiar puerto en run.py
# app.run(debug=True, port=5001)
```

### Problema: ModuleNotFoundError
**Solución:**
```bash
# Asegurar que el venv está activado
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### Problema: Base de datos corrupta
**Solución:**
```bash
# Eliminar BD anterior
rm instance/voting_system.db

# Reinicializar
python init_db.py
```

### Problema: Error de permisos en Linux
**Solución:**
```bash
chmod +x setup.py
python setup.py
```

---

## ✅ Verificación Post-Instalación

Después de instalar, verifica que todo funciona:

```bash
# Test 1: Servidor responde
curl http://127.0.0.1:5000/

# Test 2: API funciona
curl http://127.0.0.1:5000/api/results/summary

# Test 3: Ver logs
python test_api.py
```

---

## 📊 Comparativa de Opciones

| Opción | Velocidad | Dificultad | Escalabilidad | Costo |
|--------|-----------|-----------|---------------|-------|
| Local | ⚡⚡⚡ | Fácil | Baja | Gratis |
| Automática | ⚡⚡ | Muy Fácil | Baja | Gratis |
| Docker | ⚡⚡ | Media | Alta | Gratis |
| Heroku | ⚡ | Fácil | Media | Desde $7 |
| AWS | ⚡ | Difícil | Muy Alta | Desde $5 |
| Azure | ⚡ | Difícil | Muy Alta | Desde $10 |

---

## 🚀 Recomendaciones

- **Desarrollo Local:** Opción 1 o 2
- **Testing/Demo:** Opción 3 (Docker)
- **Producción Pequeña:** Opción 4 (Heroku)
- **Producción Empresarial:** Opción 5 (AWS) o Opción 6 (Azure)

---

## 📞 Soporte

Si tienes problemas:
1. Revisar la sección Troubleshooting
2. Consultar logs de error
3. Crear issue en GitHub
4. Revisar documentación completa en README.md

---

**¡Tu aplicación estará lista en minutos!** 🎉
