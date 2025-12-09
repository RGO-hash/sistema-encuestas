# 🧪 Guía de Testing

## Testing Manual

### 1. Autenticación

#### Login
```
URL: http://localhost:5000
Email: admin@encuestas.com
Contraseña: admin123
✓ Debe iniciar sesión exitosamente
✓ Debe redirigir al dashboard
```

#### Logout
```
Click en Cerrar sesión
✓ Debe eliminar token
✓ Debe redirigir a login
```

### 2. Gestión de Participantes

#### Crear participante individual
```
Dashboard → Participantes → Nueva Participante
- Email: test@example.com
- Nombre: Test
- Apellido: Usuario
- Campos: Rellenar opcionales
✓ Debe aparecer en la lista
✓ Email debe ser único
```

#### Buscar participante
```
Dashboard → Participantes → Buscar "test"
✓ Debe filtrar en tiempo real
✓ Debe mostrar coincidencias
```

#### Carga CSV
```
Dashboard → Participantes → Cargar CSV
- Descargar plantilla
- Rellenar con datos
- Subir archivo
✓ Debe mostrar progreso
✓ Debe mostrar errores (si los hay)
✓ Debe mostrar cantidad cargada
```

### 3. Configuración de Encuesta

#### Crear posición
```
Dashboard → Posiciones → Nueva Posición
- Nombre: Presidente
- Descripción: Líder del equipo
- Orden: 1
✓ Debe aparecer en la lista
✓ Debe mostrarse activa
```

#### Agregar candidatos
```
Dashboard → Candidatos → Nueva Candidato
- Posición: Presidente
- Nombre: Juan Pérez
- Descripción: Experiencia en gestión
✓ Debe aparecer en la tabla
✓ Debe estar asociado a posición
```

### 4. Envío de Invitaciones

#### Enviar invitaciones
```
Dashboard → Participantes → Enviar Invitaciones
- Seleccionar Sí
✓ Debe mostrar confirmación
✓ Debe mostrar cantidad enviada
✓ Participantes deben recibir email (si SMTP está configurado)
```

### 5. Encuesta Pública

#### Acceder a encuesta
```
Desde email → Click en enlace
O construir URL: /survey?email=test@example.com&token=...

✓ Debe mostrar nombre de participante
✓ Debe mostrar todas las posiciones
✓ Debe mostrar candidatos
✓ Debe permitir seleccionar voto
```

#### Votar
```
- Seleccionar candidato o opción especial
- Click en botón
✓ Debe marcar la selección
✓ Debe mostrar confirmación
✓ Debe permitir cambiar voto antes de confirmar
```

#### Confirmar voto
```
- Revisar resumen
- Click en "Confirmar Voto"
✓ Debe mostrar mensaje de éxito
✓ Debe marcar participante como votado
✓ Debe registrar voto en BD
```

#### Prevención de voto duplicado
```
- Intentar acceder nuevamente con mismo email
✓ Debe mostrar error "Ya has votado"
✓ Debe bloquear acceso
```

### 6. Resultados y Reportes

#### Ver resultados
```
Resultados
✓ Debe mostrar gráficos por posición
✓ Debe mostrar estadísticas
✓ Debe mostrar línea de tiempo
✓ Debe identificar ganador
```

#### Exportar CSV
```
Resultados → Descargar CSV
✓ Debe generar archivo
✓ Debe contener datos correctos
✓ Debe ser descargable
```

#### Exportar auditoría
```
Resultados → Exportar Auditoría
✓ Debe generar JSON
✓ Debe contener logs de votos
✓ Debe incluir IP y timestamps
```

### 7. Casos de Borde

#### Email inválido
```
Crear participante con: "invalid.email"
✓ Debe mostrar error
✓ Debe validar formato
```

#### Email duplicado
```
Crear 2 participantes con mismo email
✓ Debe mostrar error "Email ya registrado"
✓ No debe permitir duplicado
```

#### Sin voto seleccionado
```
Ir a encuesta → Click enviar sin seleccionar
✓ Debe mostrar error "Selecciona al menos un voto"
✓ No debe enviar
```

#### Página expirada
```
Esperar 30+ minutos → Intentar votar
✓ Debería mostrar error (si tiene validación de expiración)
```

---

## Testing API con cURL

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@encuestas.com","password":"admin123"}'
```

### Listar Participantes
```bash
curl -X GET http://localhost:5000/api/participants \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Crear Participante
```bash
curl -X POST http://localhost:5000/api/participants \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "email":"new@example.com",
    "first_name":"New",
    "last_name":"User"
  }'
```

### Obtener Encuesta
```bash
curl "http://localhost:5000/api/voting/public/positions?email=test@example.com&token=TOKEN"
```

### Registrar Voto
```bash
curl -X POST http://localhost:5000/api/voting/public/submit \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "token":"TOKEN",
    "votes":{"1":{"type":"candidate","candidate_id":1}}
  }'
```

---

## Testing de Seguridad

### 1. Protección JWT
```
Intentar acceder a /api/participants sin token
✓ Debe retornar 401 Unauthorized
```

### 2. Email injection
```
Campo email: "test@example.com\n<script>alert('XSS')</script>"
✓ Debe validar y rechazar
```

### 3. SQL Injection
```
Campo búsqueda: "' OR '1'='1"
✓ Debe escapar y no inyectar
```

### 4. CSRF
```
Intentar POST desde otro dominio
✓ Debe validar CORS
```

### 5. Fuerza bruta
```
Múltiples intentos de login fallidos
✓ Debería limitar intentos (implementar en futuro)
```

---

## Testing de Performance

### 1. Carga de 1000 participantes
```bash
# Generar CSV con 1000 filas
python scripts/generate_csv.py 1000

# Subir
# Medir tiempo de carga
# ✓ Debe completarse en < 5 segundos
```

### 2. Gráficos con muchos votos
```
Crear 500 votos simulados
Ver página de resultados
✓ Los gráficos deben cargar < 2 segundos
```

### 3. Búsqueda con 5000 participantes
```
Escribir en búsqueda
✓ Debe responder < 500ms (con debounce)
```

---

## Checklist de Testing Completo

### Funcionalidad
- [ ] Auth funciona correctamente
- [ ] CRUD de participantes
- [ ] Carga CSV sin errores
- [ ] Posiciones se crean y editan
- [ ] Candidatos se asocian a posiciones
- [ ] Invitaciones se envían
- [ ] Encuesta es accesible
- [ ] Votos se registran
- [ ] Resultados se muestran
- [ ] Exportación funciona

### Seguridad
- [ ] JWT válida
- [ ] Emails únicos
- [ ] Votos no duplicados
- [ ] SQL injection prevenida
- [ ] XSS prevenido
- [ ] CORS configurado

### Interfaz
- [ ] Responsive en móvil
- [ ] Formularios validados
- [ ] Errores mostrados
- [ ] Animaciones suaves
- [ ] Botones funcionan
- [ ] Navegación clara

### Base de Datos
- [ ] Tablas creadas
- [ ] Datos persistentes
- [ ] Índices funcionales
- [ ] Relaciones correctas
- [ ] Sin duplicados

### Performance
- [ ] Página carga < 2s
- [ ] API responde < 200ms
- [ ] Búsqueda rápida
- [ ] Gráficos fluidos

---

## Datos de Prueba

### Admin por defecto
```
Email: admin@encuestas.com
Contraseña: admin123
```

### Participantes de ejemplo
```
juan@example.com - Juan Pérez
maria@example.com - María García
carlos@example.com - Carlos López
ana@example.com - Ana Martínez
francisco@example.com - Francisco Rodríguez
```

### Posiciones
```
Presidente
Vicepresidente
Tesorero
Secretario
```

---

## Debugging

### Ver logs
```bash
tail -f logs/app.log
```

### Conectar a BD
```bash
sqlite3 app.db

# O PostgreSQL
psql -U encuestas -d encuestas
```

### Modo debug en navegador
```javascript
// Abrir consola (F12)
// Ver requests en Network
// Ver errors en Console
```

---

¡Happy Testing! 🚀
