# Sistema de Registro de Participantes

## Descripción General

Se ha implementado un nuevo sistema de registro de participantes que permite:

1. **Registro Público**: Los usuarios pueden registrarse sin necesidad de ser administrador
2. **Validación de Email Único**: Cada email solo puede registrarse una vez
3. **Confirmación por Email**: Se envía un email de confirmación que expira en 24 horas
4. **Autenticación**: Los participantes registrados pueden iniciar sesión y obtener un token JWT
5. **Separación de Permisos**: Los participantes NO tienen acceso a funciones de administrador

## Endpoints Disponibles

### Registro de Participantes

#### `POST /api/auth/participant/register`
Registra un nuevo participante.

**Request Body:**
```json
{
  "email": "usuario@example.com",
  "password": "password123",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

**Response (201 Created):**
```json
{
  "message": "Registro exitoso. Por favor confirma tu email",
  "email": "usuario@example.com",
  "user_id": 1
}
```

**Errores:**
- `400`: Faltan campos o email inválido
- `409`: Email ya registrado
- `500`: Error del servidor

### Confirmación de Email

#### `GET /api/auth/participant/confirm/<token>`
Confirma el email del participante usando el token de confirmación.

**Response (200 OK):**
```json
{
  "message": "Email confirmado exitosamente. Ya puedes ingresar.",
  "email": "usuario@example.com"
}
```

**Errores:**
- `400`: Token inválido o expirado

### Iniciar Sesión (Participante)

#### `POST /api/auth/participant/login`
Autentica un participante registrado.

**Request Body:**
```json
{
  "email": "usuario@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "is_active": true,
    "email_confirmed": true,
    "participant_id": 1,
    "created_at": "2025-12-09T21:45:00",
    "updated_at": "2025-12-09T21:45:00"
  },
  "type": "participant"
}
```

**Errores:**
- `400`: Email o contraseña faltantes
- `401`: Credenciales inválidas

### Verificar Token (Participante)

#### `GET /api/auth/participant/verify`
Verifica que el token JWT sea válido.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "is_active": true,
    "email_confirmed": true,
    "participant_id": 1,
    "created_at": "2025-12-09T21:45:00",
    "updated_at": "2025-12-09T21:45:00"
  },
  "type": "participant"
}
```

**Errores:**
- `401`: Token inválido o expirado

## Flujo de Registro Completo

### 1. Registro
El usuario se registra con email, contraseña y nombre.

```bash
POST /api/auth/participant/register
{
  "email": "juan@example.com",
  "password": "micontraseña",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

**Respuesta:**
- Se crea la cuenta de usuario participante (inactiva)
- Se genera un token de confirmación (válido 24 horas)
- Se envía un email de confirmación con el enlace

### 2. Confirmación de Email
El usuario hace clic en el enlace de confirmación en el email.

```
GET /api/auth/participant/confirm/<token>
```

**Lo que ocurre:**
- Se marca el email como confirmado
- Se activa la cuenta del participante
- Se crea automáticamente un registro en la tabla `participants`
- El usuario puede ahora iniciar sesión

### 3. Inicio de Sesión
El usuario inicia sesión con email y contraseña.

```bash
POST /api/auth/participant/login
{
  "email": "juan@example.com",
  "password": "micontraseña"
}
```

**Respuesta:**
- Se retorna un token JWT válido por 24 horas
- El token se usa para acceder a endpoints protegidos

## Validaciones

### Email
- Debe ser un email válido (formato estándar)
- Debe ser único (no puede existir otro usuario o participante con ese email)
- No diferencia mayúsculas/minúsculas en la búsqueda

### Contraseña
- Mínimo 6 caracteres
- Se almacena hasheada (no se puede recuperar, solo resetear)

### Nombres
- Requeridos en el registro
- Se preservan capitalizados

## Base de Datos

### Nueva tabla: `participant_users`
```
- id (PK)
- email (UNIQUE)
- password_hash
- first_name
- last_name
- is_active (bool, default=False)
- email_confirmed (bool, default=False)
- confirmation_token (UNIQUE, nullable)
- confirmation_token_expires (datetime, nullable)
- participant_id (FK a participants)
- created_at
- updated_at
```

## Relación con Tabla `participants`

**Antes:**
La tabla `participants` se usaba solo para participantes importados o creados por admin.

**Después:**
- La tabla `participants` mantiene todos los participantes (admin e importados)
- La tabla `participant_users` es para participantes que se registran ellos mismos
- Cada `ParticipantUser` puede tener un `participant` asociado
- Cuando un usuario registrado confirma su email, se crea automáticamente un participante

## Seguridad

### Contraseñas
- Se hashean usando werkzeug.security
- Se verifican con check_password_hash
- Nunca se retornan en las respuestas de API

### Tokens JWT
- Se generan con Flask-JWT-Extended
- Válidos por 24 horas
- Se incluyen en el header `Authorization: Bearer <token>`

### Tokens de Confirmación
- Se generan aleatoriamente con secrets.token_urlsafe
- Válidos por 24 horas
- Se invalidan después del primer uso

## Ejemplos de Uso

### Con cURL
```bash
# Registro
curl -X POST http://localhost:5000/api/auth/participant/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "password123",
    "first_name": "Juan",
    "last_name": "Pérez"
  }'

# Iniciar sesión
curl -X POST http://localhost:5000/api/auth/participant/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "password123"
  }'
```

### Con JavaScript (Fetch)
```javascript
// Registro
const registerResponse = await fetch('/api/auth/participant/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@example.com',
    password: 'password123',
    first_name: 'Juan',
    last_name: 'Pérez'
  })
});
const registerData = await registerResponse.json();
console.log(registerData);

// Iniciar sesión
const loginResponse = await fetch('/api/auth/participant/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@example.com',
    password: 'password123'
  })
});
const loginData = await loginResponse.json();
const token = loginData.access_token;

// Usar token en peticiones posteriores
const protectedResponse = await fetch('/api/participants/stats', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## Próximos Pasos

### Interfaz Frontend
Crear páginas HTML/JavaScript para:
- Formulario de registro (/register)
- Página de confirmación de email
- Página de login para participantes (/participant-login)
- Dashboard de participante con acceso a encuesta

### Restricciones de Acceso
Asegurar que:
- Los endpoints de admin (GET /api/participants, POST /api/survey/positions, etc.) solo sean accesibles por AdminUser
- Los participantes solo tengan acceso a endpoints públicos y sus propios datos

### Email Configuration
Configurar variables de entorno:
```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_app
MAIL_DEFAULT_SENDER=noreply@encuestas.com
```

## Pruebas

Ejecutar el script de prueba:
```bash
python test_registration.py
```

Este script verifica:
- Registro exitoso
- Rechazo de email duplicado
- Validación de formato de email
- Validación de longitud de contraseña
