# Imagen base de Python
FROM python:3.13-slim

# Evitar buffering de salida
ENV PYTHONUNBUFFERED=1

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto
COPY . .

# Exponer el puerto de Django (por defecto 8000)
EXPOSE 8000

# Comando para ejecutar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
