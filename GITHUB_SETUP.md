# 🗳️ Sistema de Votación Electrónica

## Descripción

Sistema completo de votación electrónica construido con Flask y SQLite. Permite a los administradores crear encuestas, registrar candidatos y gestionar procesos de votación, mientras que los participantes pueden votar de manera segura con autenticación JWT.

## 🎯 Características Principales

✅ **Autenticación**
- Autenticación de administradores con JWT
- Autenticación de participantes (votantes)
- Sistema de tokens seguros

✅ **Gestión de Encuestas y Candidatos**
- Crear y gestionar encuestas
- Registrar posiciones (cargos)
- Registrar candidatos con fotos y descripciones
- Activar/desactivar encuestas

✅ **Votación**
- Interfaz intuitiva para votantes
- Selección visual de candidatos
- Confirmación de votos antes de enviar
- Prevención de votos duplicados
- Previsualización de candidatos sin necesidad de login

✅ **Resultados**
- Visualización en tiempo real de resultados
- Conteos de votos por posición
- Cálculo automático de porcentajes
- Identificación de ganadores

✅ **Seguridad**
- Validación de datos en backend
- Protección contra votos múltiples
- Endpoints públicos y protegidos
- Base de datos SQLite con relaciones

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Navegador web moderno

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/RGO-hash/sistema-encuestas.git
cd sistema-encuestas
```

### 2. Crear entorno virtual
```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Inicializar la base de datos
```bash
python init_db.py
```

### 5. Ejecutar el servidor
```bash
python run.py
```

El servidor estará disponible en `http://127.0.0.1:5000`

## 💻 Uso de la Aplicación

### Para Administradores

#### Acceso Restringido
1. Ir a `http://127.0.0.1:5000/`
2. Usar las credenciales por defecto:
   - Email: `admin@test.com`
   - Contraseña: `test123`

#### Crear una Nueva Encuesta
1. En el panel de administración, ir a la sección **Encuestas**
2. Hacer clic en **Crear Nueva Encuesta**
3. Completar los detalles (nombre, descripción)
4. Agregar posiciones (cargos)
5. Registrar candidatos para cada posición

#### Registrar Candidatos
1. Ir a la sección **Candidatos**
2. Hacer clic en **Registrar Nuevo Candidato**
3. Completar:
   - Nombre completo
   - Partido/Movimiento
   - Posición (cargo)
   - Descripción (opcional)
   - Foto (opcional)

#### Activar una Encuesta
1. En el panel de encuestas, seleccionar la encuesta
2. Hacer clic en **Activar Encuesta**
3. Los participantes podrán votar inmediatamente

#### Ver Resultados
1. Ir a la sección **Resultados**
2. Visualizar votos en tiempo real
3. Ver porcentajes y ganadores

### Para Participantes (Votantes)

#### Registrarse
1. Ir a `http://127.0.0.1:5000/`
2. Hacer clic en la pestaña **Registro**
3. Completar:
   - Número de cédula/ID
   - Nombre
   - Apellido
   - Correo electrónico
4. Hacer clic en **Registrarse**

#### Votar
1. Ir a la pestaña **Votación**
2. Ingresar credenciales:
   - Email
   - Contraseña (será `nombre_apellido` por defecto)
3. Seleccionar candidatos para cada posición
4. Revisar las selecciones en el modal de confirmación
5. Hacer clic en **Confirmar Votos**
6. Los resultados se mostrarán automáticamente

#### Ver Resultados
1. Ir a la pestaña **Resultados**
2. Visualizar:
   - Total de votos emitidos
   - Votos por candidato
   - Porcentajes por posición

## 📁 Estructura del Proyecto

```
sistema-encuestas/
├── app/                          # Aplicación principal
│   ├── __init__.py              # Inicialización de Flask
│   ├── models.py                # Modelos de base de datos
│   ├── extensions.py            # Extensiones (SQLAlchemy, JWT)
│   ├── routes/                  # Rutas de la API
│   │   ├── auth.py              # Autenticación
│   │   ├── survey.py            # Gestión de encuestas
│   │   ├── candidates.py        # Gestión de candidatos
│   │   ├── participants.py      # Gestión de participantes
│   │   ├── voting.py            # Votación
│   │   ├── voting_participant.py # Votación de participantes
│   │   └── public_results.py    # Resultados públicos
│   ├── services/                # Servicios
│   │   ├── email_service.py     # Envío de correos
│   │   ├── audit_service.py     # Auditoría
│   │   └── report_service.py    # Generación de reportes
│   ├── static/                  # Archivos estáticos
│   │   ├── css/                 # Hojas de estilos
│   │   ├── js/                  # JavaScript
│   │   │   ├── auth.js
│   │   │   ├── voting.js        # Lógica de votación
│   │   │   ├── dashboard.js
│   │   │   └── common.js
│   │   └── img/                 # Imágenes
│   └── templates/               # Plantillas HTML
│       ├── index.html           # Página principal
│       ├── base.html            # Plantilla base
│       └── ...
├── instance/                    # Instancia de la aplicación
├── logs/                        # Logs del sistema
├── run.py                       # Punto de entrada
├── requirements.txt             # Dependencias
├── init_db.py                   # Inicialización de BD
├── README.md                    # Este archivo
└── config.py                    # Configuración

```

## 🔧 Configuración

### Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```
FLASK_ENV=development
FLASK_DEBUG=True
JWT_SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///instance/voting_system.db
```

### Configuración de Base de Datos

La base de datos se crea automáticamente en `instance/voting_system.db` al ejecutar `init_db.py`.

## 🧪 Testing

Se incluyen scripts de prueba:

```bash
# Probar endpoints de API
python test_api.py

# Probar registro de participantes
python test_registration.py

# Probar votación
python test_endpoints.py
```

## 📊 API Endpoints

### Autenticación
- `POST /api/auth/login` - Login de administrador
- `POST /api/auth/logout` - Logout
- `GET /api/auth/user` - Usuario actual

### Encuestas
- `GET /api/surveys` - Listar encuestas
- `POST /api/surveys` - Crear encuesta
- `PUT /api/surveys/<id>` - Actualizar encuesta
- `DELETE /api/surveys/<id>` - Eliminar encuesta

### Candidatos
- `GET /api/candidates` - Listar candidatos
- `POST /api/candidates` - Registrar candidato
- `PUT /api/candidates/<id>` - Actualizar candidato
- `DELETE /api/candidates/<id>` - Eliminar candidato

### Votación
- `GET /api/voting/active-surveys` - Encuestas activas
- `POST /api/voting/submit-votes` - Enviar votos

### Resultados (Público)
- `GET /api/results/summary` - Resumen de resultados

### Participantes
- `POST /api/participant-auth/register` - Registrar participante
- `POST /api/participant-auth/login` - Login de participante

## 🔐 Seguridad

- ✅ Validación de datos en todos los endpoints
- ✅ Autenticación JWT para operaciones sensibles
- ✅ Prevención de votos duplicados
- ✅ Validación de permisos de usuario
- ✅ CORS configurado correctamente

## 🐛 Troubleshooting

### El servidor no inicia
```bash
# Verificar que Python está instalado
python --version

# Verificar que el venv está activado
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### Errores de base de datos
```bash
# Eliminar BD anterior y reinicializar
rm instance/voting_system.db
python init_db.py
```

### Puerto 5000 en uso
```bash
# Cambiar puerto en run.py
# Cambiar: app.run(port=5000)
# Por: app.run(port=5001)
```

## 📝 Licencia

Este proyecto está bajo licencia MIT.

## 👨‍💻 Autor

Desarrollado como un sistema completo de votación electrónica.

## 📞 Soporte

Para reportar bugs o sugerencias, crear un issue en el repositorio de GitHub.

---

**Versión:** 1.0.0  
**Última actualización:** Diciembre 2025
