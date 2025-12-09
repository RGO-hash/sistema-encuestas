# 🌐 Guía de Deployment

## Deployment en Producción

### Requisitos Previos
- Servidor Linux (Ubuntu 20.04+ recomendado)
- Python 3.8+
- PostgreSQL 12+ (recomendado)
- Nginx o Apache
- SSL/TLS certificado

---

## Opción 1: Heroku (Más Fácil)

### 1. Preparar proyecto
```bash
# Crear Procfile
echo "web: python run.py" > Procfile

# Crear runtime.txt
echo "python-3.11.0" > runtime.txt

# Git
git init
git add .
git commit -m "Initial commit"
```

### 2. Deploy
```bash
# Instalar Heroku CLI
# Desde: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Crear app
heroku create tu-app-name

# Deploy
git push heroku main

# Setup BD
heroku run python init_db.py

# Ver logs
heroku logs --tail
```

### 3. Configurar Variables
```bash
heroku config:set FLASK_ENV=production
heroku config:set JWT_SECRET_KEY=tu-clave-muy-segura
heroku config:set DATABASE_URL=tu-postgresql-url
heroku config:set MAIL_SERVER=smtp.gmail.com
heroku config:set MAIL_USERNAME=tu-email@gmail.com
heroku config:set MAIL_PASSWORD=tu-contraseña
```

---

## Opción 2: DigitalOcean / AWS / Azure

### 1. Conectar al servidor
```bash
ssh root@tu-servidor-ip
```

### 2. Instalar dependencias
```bash
apt update
apt install python3-pip python3-venv postgresql postgresql-contrib nginx
```

### 3. Clonar proyecto
```bash
cd /var/www
git clone tu-repo-url encuestas
cd encuestas
```

### 4. Configurar Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### 5. Configurar PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE encuestas;
CREATE USER encuestas WITH PASSWORD 'contraseña-segura';
ALTER ROLE encuestas SET client_encoding TO 'utf8';
ALTER ROLE encuestas SET default_transaction_isolation TO 'read committed';
ALTER ROLE encuestas SET default_transaction_deferrable TO on;
ALTER ROLE encuestas SET default_transaction_read_committed TO on;
GRANT ALL PRIVILEGES ON DATABASE encuestas TO encuestas;
\q
```

### 6. Configurar .env
```bash
nano .env
# Agregar:
FLASK_ENV=production
DATABASE_URL=postgresql://encuestas:contraseña@localhost/encuestas
JWT_SECRET_KEY=tu-clave-muy-segura
# ... otras variables
```

### 7. Configurar Gunicorn
```bash
# Crear encuestas.service
sudo nano /etc/systemd/system/encuestas.service
```

```ini
[Unit]
Description=Encuestas Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/encuestas
ExecStart=/var/www/encuestas/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 run:app

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl start encuestas
sudo systemctl enable encuestas
```

### 8. Configurar Nginx
```bash
sudo nano /etc/nginx/sites-available/encuestas
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/encuestas/app/static;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/encuestas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. SSL/TLS con Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

### 10. Inicializar BD
```bash
cd /var/www/encuestas
source venv/bin/activate
python init_db.py
```

---

## Opción 3: Docker

### 1. Crear Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
```

### 2. Crear docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: encuestas
      POSTGRES_USER: encuestas
      POSTGRES_PASSWORD: contraseña-segura
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://encuestas:contraseña-segura@db:5432/encuestas
      FLASK_ENV: production
      JWT_SECRET_KEY: tu-clave-muy-segura
    depends_on:
      - db
    volumes:
      - .:/app

volumes:
  postgres_data:
```

### 3. Deploy
```bash
docker-compose up -d
docker-compose exec web python init_db.py
```

---

## Checklist Pre-Producción

### Seguridad
- [ ] Cambiar JWT_SECRET_KEY a un valor aleatorio fuerte
- [ ] Cambiar credenciales admin por defecto
- [ ] Cambiar contraseña de BD
- [ ] Habilitar HTTPS/SSL
- [ ] Configurar firewall
- [ ] Deshabilitar debug mode (`DEBUG=False`)

### Base de Datos
- [ ] Usar PostgreSQL en lugar de SQLite
- [ ] Configurar backups automáticos
- [ ] Verificar índices de BD
- [ ] Habilitar logging de queries lentas

### Performance
- [ ] Configurar caché (Redis)
- [ ] Optimizar imágenes
- [ ] Comprimir assets (CSS/JS)
- [ ] Usar CDN para archivos estáticos
- [ ] Configurar múltiples workers Gunicorn

### Monitoreo
- [ ] Configurar alertas de errores (Sentry)
- [ ] Monitoreo de uptime (UptimeRobot)
- [ ] Logs centralizados (ELK Stack)
- [ ] Monitoreo de performance (New Relic)

### Configuración
- [ ] CORS solo para dominios permitidos
- [ ] Validar y limitar rate limiting
- [ ] Configurar CORS HTTPS solo
- [ ] Habilitar HSTS
- [ ] Configurar X-Frame-Options

---

## Mantenimiento

### Backups
```bash
# PostgreSQL
pg_dump encuestas > backup.sql

# Restaurar
psql encuestas < backup.sql
```

### Updates
```bash
cd /var/www/encuestas
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python init_db.py
sudo systemctl restart encuestas
```

### Monitoreo de Logs
```bash
# Systemd
sudo journalctl -u encuestas -f

# Nginx
sudo tail -f /var/log/nginx/error.log
```

---

## Troubleshooting

### App no inicia
```bash
# Ver logs
systemctl status encuestas
journalctl -u encuestas -n 50
```

### Errores de BD
```bash
# Conectar a PostgreSQL
psql -U encuestas -d encuestas -h localhost

# Ver tablas
\dt

# Ver usuarios
\du
```

### Performance lenta
```bash
# Ver queries lentas en PostgreSQL
pg_stat_statements

# Revisar logs
tail -f /var/www/encuestas/logs/app.log
```

---

¡Deployment completado! 🚀
