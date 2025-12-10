FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio de instancia
RUN mkdir -p instance

# Exponer puerto
EXPOSE 5000

# Variable de entorno
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Comando para iniciar la aplicación
CMD ["python", "run.py"]
