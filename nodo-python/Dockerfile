FROM python:3.10-alpine

WORKDIR /app

# Instalamos las dependencias directamente
RUN pip install mysql-connector-python pika

COPY main.py .

# Mantiene el contenedor vivo para pruebas o ejecuta el script
CMD ["python", "main.py"]