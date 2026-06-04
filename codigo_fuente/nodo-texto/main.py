import mysql.connector
import pika
import json
import time
import traceback

def enviar_a_ia():
    try:
        # 1. Simular lectura desde MySQL (BD1)
        db = mysql.connector.connect(
            host="mysql-bd1",
            user="root",
            password="rootpassword",
            database="bd1_texto",
            port=3306
        )
        cursor = db.cursor(dictionary=True)
        # Simulamos que ingresó un SMS con DNI y Monto
        cursor.execute("""
            INSERT INTO mensajes_texto (id_usuario, contenido, fecha_envio, tipo_mensaje, canal) 
            VALUES (1, 'Hola, mi dni es 12345678 y quiero un prestamo de 500.00', NOW(), 'solicitud', 'sms')
        """)
        db.commit()
        id_msg = cursor.lastrowid
        cursor.execute("SELECT * FROM mensajes_texto WHERE id_mensaje = %s", (id_msg,))
        mensaje_db = cursor.fetchone()

        # 2. Conectar a RabbitMQ (Con tolerancia a fallos de arranque)
        credentials = pika.PlainCredentials('admin', 'adminpassword')
        parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
        for intento in range(5):
            try:
                connection = pika.BlockingConnection(parameters)
                break  # Conexión exitosa, salimos del bucle
            except pika.exceptions.AMQPConnectionError:
                print(f"[Python] El puerto 5672 de RabbitMQ aún no abre. Reintento {intento + 1}/5 en 3 segundos...")
                time.sleep(3)
        
        if not connection:
            raise Exception("Fallo definitivo: RabbitMQ no abrió el puerto a tiempo.")

        channel = connection.channel()
        channel.queue_declare(queue="cola.ia")

        # 3. Empaquetar
        resultado = {
            "client_id": f"sms_{id_msg}",
            "origen": "textos",
            "contenido": mensaje_db["contenido"],
            "fecha": str(mensaje_db["fecha_envio"])
        }

        channel.basic_publish(
            exchange="",
            routing_key="cola.ia",
            body=json.dumps(resultado)
        )
        print(f"[Python] Mensaje de texto enviado a cola.ia: {resultado}")

        connection.close()
        cursor.close()
        db.close()

    except Exception as e:
        print(f"ERROR en Python: {e}")
        # Esto imprimirá la traza completa del error en los logs de Docker
        traceback.print_exc()

if __name__ == "__main__":
    enviar_a_ia()