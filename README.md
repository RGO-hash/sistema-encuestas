# 🗳️ Sistema de Gestión de Encuestas

Una plataforma web completa y profesional para la gestión integral de encuestas de votación, con características avanzadas de seguridad, análisis de resultados y auditoría.

## 📋 Características Principales

### 1. **Gestión de Participantes**
- Registro individual de participantes con campos personalizables
- Carga en lote desde archivos CSV
- Búsqueda y filtrado en tiempo real
- Validación de emails únicos
- Seguimiento del estado de voto

### 2. **Configuración de Encuestas**
- Crear múltiples cargos/posiciones
- Registrar candidatos/aspirantes por posición
- Ordenamiento customizable de posiciones y candidatos
- Descripción detallada de posiciones y candidatos

### 3. **Sistema de Votación**
- Encuesta accesible solo mediante enlace único por participante
- Validación de email en la URL
- Prevención de votos duplicados
- Opciones de voto: candidato específico, "No sé", "Ninguno", "Abstención", "Voto en Blanco"
- Interfaz intuitiva y responsive

### 4. **Reportes y Resultados**
- Gráficos interactivos con Chart.js (doughnuts, líneas)
- Estadísticas detalladas por posición
- Línea de tiempo de participación
- Exportación a CSV
- Exportación de logs de auditoría (JSON)
- Identificación de ganadores por posición

### 5. **Seguridad y Auditoría**
- Autenticación JWT para administradores
- Log de auditoría completo de todas las acciones
- Trazabilidad de votos (IP, User-Agent)
- Validación de inputs contra inyección
- Protección CSRF
- Sesiones seguras con cookies httpOnly

### 6. **Interfaz Profesional**
- Diseño responsive (mobile-first)
- Paleta de colores moderna (azul #4361ee)
- Tipografía Inter/Roboto
- Bootstrap 5 + CSS personalizado
- Animaciones suaves
- Dark mode compatible

## 🛠️ Stack Tecnológico

### Backend
- **Framework:** Flask 3.0
- **ORM:** SQLAlchemy
- **Autenticación:** JWT (Flask-JWT-Extended)
- **Email:** Flask-Mail (SMTP)
- **Base de Datos:** SQLite (desarrollo)
- **Python:** 3.8+

### Frontend
- **HTML5** semántico
- **CSS3** moderno con variables CSS
- **JavaScript ES6+** vanilla (sin frameworks)
- **Bootstrap 5**
- **Chart.js** para gráficos

### Herramientas
- Git para control de versiones
- Estructura modular de carpetas

## 📦 Instalación

### Requisitos Previos
- Python 3.8+
- pip (gestor de paquetes de Python)
- Git

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
```bash
cd "Proyecto final"
```

2. **Crear un entorno virtual**
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
Crear un archivo `.env` en la raíz del proyecto:
```env
FLASK_ENV=development
FLASK_APP=run.py
JWT_SECRET_KEY=tu-clave-secreta-muy-segura

# Configuración de Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicación
MAIL_DEFAULT_SENDER=encuestas@tudominio.com
```

5. **Ejecutar la aplicación**
```bash
python run.py
```

La aplicación estará disponible en: `http://localhost:5000`

## 🚀 Uso

### Primer Acceso (Admin)

Credenciales por defecto (cambiar inmediatamente en producción):
- **Email:** admin@encuestas.com
- **Contraseña:** admin123

### Flujo de Trabajo

#### 1. Configurar la Encuesta
- Acceder al dashboard como administrador
- Crear posiciones/cargos
- Agregar candidatos a cada posición

#### 2. Registrar Participantes
- Opción A: Registrar individuales manualmente
- Opción B: Cargar CSV en lote

**Formato CSV esperado:**
```
email,first_name,last_name,field1,field2,field3
juan@example.com,Juan,Pérez,Departamento,Puesto,Ubicación
maria@example.com,María,García,Departamento,Puesto,Ubicación
```

#### 3. Enviar Invitaciones
- Botón "Enviar Invitaciones"
- Los participantes recibirán email con enlace único
- El enlace incluye email y token de validación

#### 4. Participantes Votan
- Acceder mediante enlace en el email
- Seleccionar voto para cada posición
- Confirmar y enviar voto
- Mensaje de confirmación

#### 5. Visualizar Resultados
- Panel de resultados en tiempo real
- Gráficos interactivos
- Estadísticas de participación
- Exportar reportes

## 📁 Estructura de Carpetas

```
Proyecto final/
├── app/
│   ├── __init__.py                 # Factory de Flask
│   ├── models.py                   # Modelos de BD (SQLAlchemy)
│   ├── extensions.py               # Extensiones (DB, JWT, Mail)
│   ├── routes/
│   │   ├── auth.py                 # Rutas de autenticación
│   │   ├── participants.py         # Rutas de participantes
│   │   ├── survey.py               # Rutas de posiciones y candidatos
│   │   └── voting.py               # Rutas de votación y resultados
│   ├── services/
│   │   ├── email_service.py        # Servicio de envío de emails
│   │   ├── report_service.py       # Servicio de reportes
│   │   └── audit_service.py        # Servicio de auditoría
│   ├── templates/
│   │   ├── base.html               # Template base
│   │   ├── index.html              # Dashboard admin
│   │   ├── survey.html             # Página de encuesta
│   │   ├── results.html            # Página de resultados
│   │   └── modals/
│   │       ├── participant_modal.html
│   │       ├── position_modal.html
│   │       ├── candidate_modal.html
│   │       └── bulk_upload_modal.html
│   └── static/
│       ├── css/
│       │   └── main.css            # Estilos personalizados
│       ├── js/
│       │   ├── auth.js             # Lógica de autenticación
│       │   ├── common.js           # Funciones comunes
│       │   ├── dashboard.js        # Lógica del dashboard
│       │   ├── survey.js           # Lógica de encuesta
│       │   └── results.js          # Lógica de resultados
│       └── img/                    # Imágenes y recursos
├── logs/
│   └── app.log                     # Logs de la aplicación
├── config.py                       # Configuración
├── run.py                          # Punto de entrada
├── requirements.txt                # Dependencias
├── .env                            # Variables de entorno
├── .gitignore                      # Git ignore
└── README.md                       # Este archivo
```

## 🔐 Seguridad

### Implementaciones de Seguridad

1. **Autenticación & Autorización**
   - JWT con tokens seguros
   - Validación de tokens en cada request
   - Control de acceso basado en roles

2. **Protección de Datos**
   - Hashing de contraseñas (Werkzeug)
   - Validación de inputs
   - Protección contra SQL Injection (SQLAlchemy ORM)

3. **Sesiones**
   - Cookies HttpOnly (no accesibles desde JS)
   - Cookies Secure (solo HTTPS en producción)
   - SAMESITE=Lax para CSRF

4. **Auditoría**
   - Log de todas las acciones administrativas
   - Registro de IP y User-Agent
   - Trazabilidad de votos (sin datos personales)

5. **Validación**
   - Formato de email validado
   - Tipos de datos verificados
   - Límites de tamaño configurados

## 📊 Modelos de Base de Datos

### Participants
```sql
- id (PK)
- email (UNIQUE)
- first_name
- last_name
- field1, field2, field3 (opcionales)
- has_voted (BOOL)
- created_at, updated_at
```

### Positions
```sql
- id (PK)
- name (UNIQUE)
- description
- order
- is_active
- created_at, updated_at
```

### Candidates
```sql
- id (PK)
- position_id (FK)
- name
- description
- order
- UNIQUE(position_id, name)
```

### Votes
```sql
- id (PK)
- participant_id (FK)
- position_id (FK)
- candidate_id (FK, nullable)
- vote_type (candidate|no_se|ninguno|abstencion|blanco)
- ip_address
- user_agent
- created_at
- UNIQUE(participant_id, position_id)
```

### AdminUsers
```sql
- id (PK)
- email (UNIQUE)
- password_hash
- full_name
- is_active
- created_at, last_login
```

### AuditLogs
```sql
- id (PK)
- admin_id (FK, nullable)
- action (CREATE|UPDATE|DELETE|LOGIN|etc)
- entity_type
- entity_id
- description
- ip_address
- created_at
```

## 🔧 API REST

### Autenticación
```
POST /api/auth/login
POST /api/auth/register
GET /api/auth/verify
```

### Participantes
```
GET /api/participants                    # Listar
POST /api/participants                   # Crear
GET /api/participants/<id>               # Obtener
PUT /api/participants/<id>               # Actualizar
DELETE /api/participants/<id>            # Eliminar
POST /api/participants/bulk-upload       # Carga en lote
POST /api/participants/send-invitations  # Enviar invitaciones
GET /api/participants/stats              # Estadísticas
```

### Encuestas
```
GET /api/survey/positions
POST /api/survey/positions
PUT /api/survey/positions/<id>
DELETE /api/survey/positions/<id>

GET /api/survey/candidates
POST /api/survey/candidates
PUT /api/survey/candidates/<id>
DELETE /api/survey/candidates/<id>
```

### Votación
```
GET /api/voting/public/positions         # Obtener encuesta (público)
POST /api/voting/public/submit           # Registrar voto (público)
GET /api/voting/results                  # Obtener resultados
GET /api/voting/results/timeline         # Línea de tiempo
GET /api/voting/results/export-csv       # Exportar CSV
GET /api/voting/results/audit-log        # Log de auditoría
GET /api/voting/results/export-audit     # Exportar auditoría
```

## 📧 Configuración de Email

### Gmail (Recomendado)
1. Habilitar autenticación de 2 factores
2. Generar contraseña de aplicación
3. Configurar en `.env`:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=contraseña-de-aplicación
```

### Otros proveedores SMTP
Ajustar `MAIL_SERVER` y `MAIL_PORT` según el proveedor.

## 🧪 Testing

Para agregar más características o customizaciones:

1. **Tests unitarios**: Crear `tests/` con pruebas unitarias
2. **Testing manual**: Usar Postman o similar para APIs

## 📈 Escalabilidad Futura

Para producción, considerar:

- **Base de datos**: PostgreSQL en lugar de SQLite
- **Caché**: Redis para datos frecuentes
- **Búsqueda**: Elasticsearch para búsquedas avanzadas
- **CDN**: CloudFlare para assets estáticos
- **Containerización**: Docker y Docker Compose
- **Orquestación**: Kubernetes para scaling
- **CI/CD**: GitHub Actions, GitLab CI
- **Monitoreo**: Sentry, New Relic

## 🤝 Contribuciones

Este proyecto está disponible para modificaciones y mejoras. 

Sugerencias de mejora:
- Soporte multidioma
- 2FA para administradores
- Dashboard analítico avanzado
- Integración OAuth2
- Mobile app nativa

## 📝 Licencia

Este proyecto es de código abierto. Úsalo libremente.

## 👨‍💻 Autor
Randy Garcia O
100533464
Lab. Programacion 3
Sistema de Encuestas Profesional - 2025

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo cambiar los colores?**
R: Sí, edita las variables CSS en `/app/static/css/main.css`

**P: ¿Puedo agregar más campos a participantes?**
R: Sí, modifica el modelo `Participant` y migra la base de datos

**P: ¿Cómo cambio la contraseña de admin?**
R: Accede a la BD y hasheá con `werkzeug.security.generate_password_hash()`

**P: ¿Puedo usar PostgreSQL?**
R: Sí, cambia `SQLALCHEMY_DATABASE_URI` en `config.py`

**P: ¿Los votos son anónimos?**
R: Sí, solo se registra el tipo de voto, no datos personales

## 📞 Soporte

Para problemas, revisa los logs en `/logs/app.log`

---

**¡Disfruta administrando tus encuestas de forma segura y profesional!** 🎉
