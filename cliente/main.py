import pika
import json
import uuid
import threading
import time

class ClientePrestamos:
    def __init__(self):
        self.client_id = str(uuid.uuid4())[:8]
        self.cola_respuesta = f"respuesta.{self.client_id}"
        
        # 1. Conexión EXCLUSIVA para PUBLICAR (Hilo Principal)
        self.conn_pub = pika.BlockingConnection(
            pika.ConnectionParameters(host='127.0.0.1', port=5672, credentials=pika.PlainCredentials('admin', 'adminpassword'))
        )
        self.canal_pub = self.conn_pub.channel()

        # Iniciar el hilo en segundo plano para escuchar respuestas
        hilo_escucha = threading.Thread(target=self.escuchar_respuestas, daemon=True)
        hilo_escucha.start()
        
        # Damos una fracción de segundo para que el hilo secundario declare la cola antes de enviar nada
        time.sleep(0.5) 

    def escuchar_respuestas(self):
        # 2. Conexión EXCLUSIVA para CONSUMIR (Hilo Secundario)
        # Al instanciarla dentro de la función del hilo, le pertenece solo a este hilo
        conn_sub = pika.BlockingConnection(
            pika.ConnectionParameters(host='127.0.0.1', port=5672, credentials=pika.PlainCredentials('admin', 'adminpassword'))
        )
        canal_sub = conn_sub.channel()
        
        # Declaramos la cola de respuesta en este canal
        canal_sub.queue_declare(queue=self.cola_respuesta, durable=False)

        def callback(ch, method, properties, body):
            respuesta = json.loads(body)
            print("\n" + "="*50)
            print(f"📩 BORG IA CUBES RESPONDE:\n{respuesta['respuesta']}")
            print("="*50 + "\n> Presiona Enter para continuar...")
            
        canal_sub.basic_consume(queue=self.cola_respuesta, on_message_callback=callback, auto_ack=True)
        
        try:
            canal_sub.start_consuming()
        except Exception as e:
            print(f"Hilo de escucha terminado: {e}")

    def enviar_mensaje(self, tipo, origen, contenido, dni, correo, monto):
        mensaje = {
            "client_id": self.client_id,
            "tipo": tipo,
            "origen": origen,
            "contenido": contenido,
            "dni": dni,
            "correo": correo,
            "monto": monto
        }
        
        # Usamos el canal del hilo principal para publicar
        self.canal_pub.basic_publish(
            exchange='',
            routing_key='cola.ia',
            body=json.dumps(mensaje)
        )
        print(f"\n🚀 {tipo} enviado a través de {origen}...")

    def menu(self):
        opciones = [
            "Solicitud de préstamo", "Consulta de préstamo", "Pagar de préstamo",
            "Evaluación de préstamo", "Aviso de meses no pagados", 
            "Aviso de término de pago", "Refinanciamiento"
        ]
        
        while True:
            print(f"\n--- MENÚ CLIENTE (ID: {self.client_id}) ---")
            for i, opc in enumerate(opciones, 1):
                print(f"{i}. {opc}")
            print("8. Salir")
            
            seleccion = input("Seleccione una opción: ")
            
            if seleccion == '8':
                print("Saliendo...")
                self.conn_pub.close()
                break
                
            try:
                tipo_seleccionado = opciones[int(seleccion) - 1]
                origen = input("¿Canal de envío? (textos/correos): ").lower()
                dni = input("Ingrese su DNI: ")
                correo = input("Ingrese su correo: ")
                monto = input("Monto (Deje en blanco si no aplica): ")
                
                contenido = f"Hola, requiero {tipo_seleccionado}. Mi dni es {dni}, correo {correo} y el monto de {monto}."
                
                self.enviar_mensaje(tipo_seleccionado, origen, contenido, dni, correo, monto)
                input() # Pausa para que no se sobreescriba el menú de inmediato
            except (ValueError, IndexError):
                print("Opción inválida.")
            except Exception as e:
                print(f"Ocurrió un error al enviar: {e}")

if __name__ == "__main__":
    cliente = ClientePrestamos()
    cliente.menu()