# 1. Usamos una imagen base de Python ligera (Linux)
FROM python:3.11-slim

# 2. Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiamos el archivo de requisitos primero (para aprovechar la caché de Docker)
COPY requirements.txt .

# 4. Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos el resto de tu código al contenedor
COPY . .

# 6. Le decimos a Docker que este contenedor usará el puerto 5000
EXPOSE 5000

# 7. Comando para arrancar la app
CMD ["python", "app.py"]