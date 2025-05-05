FROM python:3.11-slim

# Evitar prompts y mantener liviano
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=yes \
    DEBIAN_FRONTEND=noninteractive

# Crear y usar el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y git build-essential cmake libprotobuf-dev protobuf-compiler libsentencepiece-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Puerto usado por Cloud Run
EXPOSE 8080

# Comando para arrancar el servidor
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
