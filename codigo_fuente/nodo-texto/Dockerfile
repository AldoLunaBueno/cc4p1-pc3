FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Mantiene el contenedor vivo para pruebas o ejecuta el script
CMD ["python", "main.py"]