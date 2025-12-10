# 📚 GUÍA DE IMPLEMENTACIÓN - Sistema de Encuestas Completo

## ✅ Funcionalidades Implementadas

Este documento detalla todas las nuevas funcionalidades que han sido implementadas en el Sistema de Gestión de Encuestas.

---

## 1️⃣ REGISTRO DE PARTICIPANTES PARA VOTAR

### Descripción
Sistema público de registro donde nuevos usuarios pueden crear una cuenta para votar en las encuestas.

### URLs
- **Página de registro**: `GET /registro` o `/participant-register`
- **API de registro**: `POST /api/participant-auth/register`
- **Validar email disponible**: `POST /api/participant-auth/check-email` (AJAX)

### Campos Requeridos
```json
{
    "email": "usuario@ejemplo.com",         // Único a nivel global
    "first_name": "Juan",                   // Mínimo 2 caracteres
    "last_name": "Pérez",                   // Mínimo 2 caracteres
    "password": "SecurePass123",            // Requisitos: 8+ caracteres, mayúscula, minúscula, número
    "password_confirm": "SecurePass123"     // Debe coincidir con password
}
```

### Validaciones Implementadas
✓ **Email único GLOBAL**: Verifica en AdminUser, ParticipantUser y Participant  
✓ **Contraseña segura**: Mínimo 8 caracteres, contiene mayúscula, minúscula y número  
✓ **Confirmación de contraseña**: Las dos contraseñas deben coincidir  
✓ **Validación en tiempo real**: AJAX para verificar email disponibilidad  
✓ **Login automático después del registro**  

### Respuesta Exitosa
```json
{
    "message": "Registro exitoso. Login automático realizado.",
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "email": "usuario@ejemplo.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "full_name": "Juan Pérez",
        "email_confirmed": false
    }
}
```

---

## 2️⃣ LOGIN DE PARTICIPANTES

### Descripción
Permite que participantes registrados ingresen a su cuenta.

### URLs
- **Página de login**: `GET /login-participante` o `/participant-login`
- **API de login**: `POST /api/participant-auth/login`
- **Verificar email**: `GET /api/participant-auth/verify?token=xxx`

### Request
```json
{
    "email": "usuario@ejemplo.com",
    "password": "SecurePass123"
}
```

### Características
✓ Opción "Recuerda mis datos" para guardar email  
✓ Toggle de visibilidad de contraseña  
✓ Redireccionamiento automático a `/votar`  

---

## 3️⃣ REGISTRO DE ASPIRANTES/CANDIDATOS

### Descripción
Permite que participantes registrados se postulen como candidatos para posiciones específicas.

### URLs
- **API de registro**: `POST /api/candidates/register` (requiere JWT)
- **Obtener posiciones disponibles**: `GET /api/candidates/available-positions`
- **Obtener candidatos por posición**: `GET /api/candidates/<position_id>`
- **Detalles de candidato**: `GET /api/candidates/<candidate_id>`

### Request (multipart/form-data)
```
POST /api/candidates/register
Authorization: Bearer {JWT_TOKEN}

Form Data:
- position_id: 1 (ID de posición)
- public_name: "Juan Pérez González" (3-200 caracteres)
- description: "Soy docente con 10 años de experiencia..." (10-2000 caracteres)
- photo: <archivo JPG/PNG/GIF, máximo 5MB> (opcional)
```

### Validaciones
✓ Solo usuarios autenticados pueden postularse  
✓ No permite candidaturas duplicadas para la misma posición  
✓ Solo posiciones activas aceptan nuevos aspirantes  
✓ Validación de formato de imagen  
✓ Límite de tamaño de archivo (5MB)  
✓ Almacenamiento seguro de fotos en `/app/static/uploads/candidates/`  

---

## 4️⃣ ÁREA DE VOTACIÓN PROTEGIDA PARA PARTICIPANTES

### Descripción
Área exclusiva donde participantes autenticados pueden votar en encuestas activas.

### URLs
- **Página de votación**: `GET /votar` o `/vote` (requiere JWT)
- **Obtener encuestas activas**: `GET /api/voting/active-surveys`
- **Enviar votos**: `POST /api/voting/submit-votes`
- **Estado de votación**: `GET /api/voting/vote-status`
- **Información del usuario**: `GET /api/voting/user-info`
- **Mis votos**: `GET /api/voting/my-votes`

### Request de Votación
```json
{
    "votes": {
        "1": {
            "type": "candidate",
            "candidate_id": 5
        },
        "2": {
            "type": "blanco"
        }
    }
}
```

### Tipos de Voto Permitidos
- `candidate`: Voto a un candidato específico (requiere `candidate_id`)
- `no_se`: "No sé"
- `ninguno`: "Ninguno"
- `abstencion`: "Abstención"
- `blanco`: "Voto en Blanco"

### Protecciones de Seguridad
✓ **Prevención de votos duplicados**: Un usuario puede votar UNA VEZ por encuesta  
✓ **Validación de posiciones activas**: Solo posiciones activas aceptan votos  
✓ **Validación de candidatos**: Verifica que el candidato exista y sea para la posición correcta  
✓ **Trazabilidad**: Registra IP y User-Agent de cada voto  
✓ **Auditoría**: Log de auditoría de todas las acciones  
✓ **Confirmación modal**: Solicita confirmación antes de enviar votos  

### Respuesta
```json
{
    "message": "Votos registrados exitosamente",
    "votes_count": 5,
    "participant": {
        "has_voted": true,
        "voted_at": "2024-01-15T14:30:00.000000"
    }
}
```

---

## 5️⃣ PÁGINA PÚBLICA DE RESULTADOS

### Descripción
Página accesible SIN autenticación para visualizar resultados de encuestas cerradas.

### URLs
- **Página de resultados**: `GET /resultados` o `/results`
- **Resumen de resultados**: `GET /api/results/summary`
- **Resultados por posición**: `GET /api/results/position/<position_id>`
- **Estadísticas generales**: `GET /api/results/statistics`
- **Línea de tiempo**: `GET /api/results/timeline`

### Datos Mostrados
✓ Resultados de todas las posiciones activas  
✓ Candidatos con votos y porcentajes  
✓ Identificación de ganador por posición  
✓ Desglose de votos especiales (en blanco, abstención, etc.)  
✓ Estadísticas generales: participación, total de votos  
✓ Gráfico de línea temporal de participación  
✓ Datos de participación en tiempo real  

### Respuesta de Resumen
```json
{
    "summary": {
        "total_positions": 5,
        "total_votes_cast": 85,
        "generated_at": "2024-01-15T14:30:00.000000"
    },
    "results": [
        {
            "position_id": 1,
            "position_name": "Presidente",
            "total_votes": 85,
            "candidates": [
                {
                    "id": 1,
                    "name": "Juan Pérez",
                    "vote_count": 45,
                    "percentage": 52.94
                }
            ],
            "winner": { ... },
            "votes_by_type": {
                "candidate": 80,
                "blanco": 3,
                "abstension": 2,
                "ninguno": 0,
                "no_se": 0
            }
        }
    ]
}
```

---

## 6️⃣ VALIDACIÓN DE EMAIL ÚNICO (CRÍTICO)

### Implementación Global
La validación de email único se ha implementado en **TODOS** los modelos de usuario:

```python
# Tablas con validación UNIQUE
- AdminUser.email (UNIQUE, INDEX)
- ParticipantUser.email (UNIQUE, INDEX)
- Participant.email (UNIQUE, INDEX)
```

### Validación en Tiempo Real (Frontend)
```javascript
POST /api/participant-auth/check-email
{
    "email": "usuario@ejemplo.com"
}

Response:
{
    "available": false,
    "message": "Este email ya está registrado"
}
```

### Puntos de Validación
1. **Validación JavaScript** del lado del cliente
2. **Validación servidor** antes de guardar
3. **Función helper** `email_exists_globally()` que verifica todas las tablas
4. **Índices en base de datos** para búsquedas rápidas
5. **Mensajes de error claros** al usuario

---

## 🔐 SEGURIDAD Y AUDITORÍA

### Autenticación JWT
✓ Tokens JWT con expiración de 24 horas  
✓ Identity almacenada como STRING (Flask-JWT-Extended v4.5+ requirement)  
✓ Conversión a INTEGER para consultas de base de datos  
✓ Manejo robusto de errores JWT  

### Protección de Rutas
✓ Rutas públicas sin autenticación: `/registro`, `/resultados`, `/api/results/*`  
✓ Rutas protegidas: `/votar`, `/api/candidates/register`, `/api/voting/*`  
✓ Validación de JWT en cada solicitud  

### Auditoría Completa
✓ Tabla `AuditLog` registra todas las acciones  
✓ Información: Action, Entity Type, Admin/User ID, IP, Timestamp  
✓ Acciones auditadas:
  - LOGIN / LOGOUT
  - CREATE (posiciones, candidatos, participantes)
  - VOTE_SUBMITTED
  - EMAIL_VERIFIED

### Trazabilidad de Votos
✓ Cada voto registra:
  - Participante (anonymized)
  - Posición
  - Candidato seleccionado
  - Tipo de voto
  - IP Address
  - User-Agent
  - Timestamp exacto

---

## 📱 INTERFAZ USUARIO

### Diseño Responsivo
✓ Mobile-first con Bootstrap 5  
✓ Gradientes modernos (azul #667eea a púrpura #764ba2)  
✓ Animaciones suaves y transiciones  
✓ Mensajes de confirmación y alerta  

### Componentes Implementados
✓ Formularios con validación en tiempo real  
✓ Modales de confirmación  
✓ Barras de progreso para requisitos de contraseña  
✓ Indicadores de estado (votado/pendiente)  
✓ Gráficos con Chart.js  
✓ Spinner de carga  

---

## 🧪 TESTING DE FUNCIONALIDADES

### Registro de Participante
```bash
# Paso 1: Acceder a la página
GET http://127.0.0.1:5000/registro

# Paso 2: Completar formulario
POST /api/participant-auth/register
{
    "email": "test@ejemplo.com",
    "first_name": "Test",
    "last_name": "Usuario",
    "password": "TestPass123",
    "password_confirm": "TestPass123"
}

# Paso 3: Verificar login automático
# Debería redirigir a /votar con token en localStorage
```

### Postularse como Candidato
```bash
# Requiere estar autenticado como ParticipantUser
curl -X POST http://127.0.0.1:5000/api/candidates/register \
  -H "Authorization: Bearer {JWT_TOKEN}" \
  -F "position_id=1" \
  -F "public_name=Juan Pérez" \
  -F "description=Tengo experiencia..." \
  -F "photo=@foto.jpg"
```

### Votación
```bash
# Paso 1: Obtener encuestas activas
GET /api/voting/active-surveys
Header: Authorization: Bearer {JWT_TOKEN}

# Paso 2: Enviar votos
POST /api/voting/submit-votes
Header: Authorization: Bearer {JWT_TOKEN}
{
    "votes": {
        "1": {"type": "candidate", "candidate_id": 5},
        "2": {"type": "blanco"}
    }
}

# Paso 3: Verificar voto registrado
GET /api/voting/vote-status
```

### Ver Resultados
```bash
# SIN autenticación requerida
GET http://127.0.0.1:5000/resultados

# APIs específicas
GET /api/results/summary
GET /api/results/position/1
GET /api/results/statistics
GET /api/results/timeline
```

---

## 🚀 RUTAS API COMPLETA

### Autenticación Participantes
```
POST   /api/participant-auth/register          → Registrar participante
POST   /api/participant-auth/login             → Login participante
GET    /api/participant-auth/verify?token=xxx → Verificar email
POST   /api/participant-auth/check-email       → Validar disponibilidad
```

### Candidatos/Aspirantes
```
POST   /api/candidates/register                → Postularse como candidato
GET    /api/candidates/available-positions     → Posiciones disponibles
GET    /api/candidates/<position_id>           → Candidatos por posición
GET    /api/candidates/<candidate_id>          → Detalles de candidato
```

### Votación
```
GET    /api/voting/active-surveys              → Encuestas activas
POST   /api/voting/submit-votes                → Enviar votos
GET    /api/voting/vote-status                 → Estado de votación
GET    /api/voting/user-info                   → Info del usuario
GET    /api/voting/my-votes                    → Mis votos registrados
```

### Resultados (Públicos)
```
GET    /api/results/summary                    → Resumen de resultados
GET    /api/results/position/<id>              → Resultados por posición
GET    /api/results/statistics                 → Estadísticas generales
GET    /api/results/timeline                   → Línea temporal
```

---

## 📊 MODELOS DE BASE DE DATOS

### Tablas Relacionadas

**ParticipantUser** (Nuevas autenticación)
```
id, email (UNIQUE), password_hash, first_name, last_name, 
is_active, email_confirmed, confirmation_token, participant_id (FK)
```

**Participant** (Existente, mejorado)
```
id, email (UNIQUE), first_name, last_name, has_voted, created_at, updated_at
```

**Candidate** (Existente)
```
id, position_id (FK), name, description, order, created_at, updated_at
UNIQUE(position_id, name) → Evita duplicados
```

**Vote** (Existente)
```
id, participant_id (FK), position_id (FK), candidate_id (FK), vote_type,
ip_address, user_agent, created_at
UNIQUE(participant_id, position_id) → Un voto por posición por usuario
```

---

## 🐛 MANEJO DE ERRORES

### Códigos HTTP
- **200 OK**: Solicitud exitosa
- **201 CREATED**: Recurso creado
- **400 BAD REQUEST**: Datos inválidos
- **401 UNAUTHORIZED**: Token inválido/faltante
- **403 FORBIDDEN**: Acceso denegado (ej: ya votó)
- **404 NOT FOUND**: Recurso no existe
- **409 CONFLICT**: Email/candidatura duplicados
- **422 UNPROCESSABLE ENTITY**: Datos incompletos
- **500 INTERNAL SERVER ERROR**: Error del servidor

### Mensajes de Error Claros
```json
{
    "error": "Este email ya está registrado"
}
```

---

## 📝 EJEMPLOS DE USO COMPLETO

### Flujo: Registrarse → Postularse → Votar → Ver Resultados

**1. Registro**
```bash
curl -X POST http://127.0.0.1:5000/api/participant-auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo@user.com",
    "first_name": "Carlos",
    "last_name": "Mendez",
    "password": "Seguro123",
    "password_confirm": "Seguro123"
  }'
```

**2. Ver posiciones disponibles**
```bash
curl -X GET http://127.0.0.1:5000/api/candidates/available-positions \
  -H "Authorization: Bearer TOKEN"
```

**3. Postularse como candidato**
```bash
curl -X POST http://127.0.0.1:5000/api/candidates/register \
  -H "Authorization: Bearer TOKEN" \
  -F "position_id=1" \
  -F "public_name=Carlos Mendez" \
  -F "description=Cuento con amplia experiencia en educación"
```

**4. Votar**
```bash
curl -X POST http://127.0.0.1:5000/api/voting/submit-votes \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "votes": {
      "1": {"type": "candidate", "candidate_id": 5},
      "2": {"type": "blanco"}
    }
  }'
```

**5. Ver resultados (público)**
```bash
curl -X GET http://127.0.0.1:5000/api/results/summary
```

---

## 🔧 REQUISITOS TÉCNICOS

### Librerías Utilizadas
- Flask 2.x
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Werkzeug (para seguridad)
- Chart.js (frontend, CDN)

### Base de Datos
- SQLite (desarrollo) / PostgreSQL (producción)
- Índices en emails para búsquedas rápidas
- Constraints UNIQUE para integridad

### Frontend
- Bootstrap 5
- Vanilla JavaScript (ES6)
- Chart.js para gráficos
- Font Awesome para iconos

---

## ✨ CARACTERÍSTICAS DESTACADAS

✅ **Email único a nivel global**: No hay duplicados en todo el sistema  
✅ **Votación segura**: Prevención de múltiples votos  
✅ **Resultados públicos**: Accesibles sin autenticación  
✅ **Auditoría completa**: Log de todas las acciones  
✅ **UI moderna y responsiva**: Diseño profesional  
✅ **Validación en tiempo real**: AJAX y JavaScript  
✅ **Manejo robusto de errores**: Mensajes claros al usuario  
✅ **Trazabilidad de votos**: IP, User-Agent, Timestamp  
✅ **Confirmación modal**: Evita votos accidentales  
✅ **Gráficos interactivos**: Chart.js para resultados  

---

## 📞 SOPORTE Y DOCUMENTACIÓN

Para más información sobre endpoints específicos, consulta:
- Docstrings en cada ruta (comentarios en código)
- Respuestas JSON de ejemplo en cada endpoint
- Logs del servidor para debugging

**Server está ejecutándose en**: http://127.0.0.1:5000

---

**Última actualización**: 9 de Diciembre de 2024  
**Versión**: 2.0 (Funcionalidades completas)
