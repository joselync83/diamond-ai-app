# Usa una imagen ligera de Python
FROM python:3.11-slim

# Evita conflictos de permisos con pip
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

# Establece el directorio de trabajo
WORKDIR /app

# Copia e instala dependencias
COPY requirements.txt .
RUN apt-get update && apt-get install -y git && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia el resto de la app
COPY . .

# Expone el puerto 8080 para Cloud Run
EXPOSE 8080

# Comando de arranque para Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
