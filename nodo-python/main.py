import mysql.connector
import pika
import time

def probar_conexiones():
    print("Esperando 15 segundos a que la infraestructura despierte...")
    time.sleep(15)
    print("Iniciando pruebas de conexión en Nodo Python...")
    
    # 1. Prueba MySQL (BD1 Texto)
    try:
        db = mysql.connector.connect(
            host="mysql-bd1",
            user="root",
            password="rootpassword",
            database="bd1_texto",
            port=3306
        )
        if db.is_connected():
            print("ÉXITO: Conectado a MySQL (BD1_Texto)")
            db.close()
    except Exception as e:
        print(f"ERROR en MySQL: {e}")

    # 2. Prueba RabbitMQ
    try:
        # Pasamos las credenciales exactas del docker-compose
        credentials = pika.PlainCredentials('admin', 'adminpassword')
        parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
        
        connection = pika.BlockingConnection(parameters)
        if connection.is_open:
            print("ÉXITO: Conectado a RabbitMQ")
            connection.close()
    except Exception as e:
        print(f"ERROR en RabbitMQ: {e}")

if __name__ == "__main__":
    probar_conexiones()