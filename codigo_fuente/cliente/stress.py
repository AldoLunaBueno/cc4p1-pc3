import pika
import json
import uuid
import time
import random
import threading

class PruebaEstres:
    def __init__(self, total_mensajes=1000):
        self.total_mensajes = total_mensajes
        self.mensajes_recibidos = 0
        
        self.client_id = f"stresstest_{str(uuid.uuid4())[:8]}"
        self.cola_respuesta = f"respuesta.{self.client_id}"
        
        # Variables para calcular la latencia promedio matemáticamente
        self.suma_tiempos_envio = 0
        self.suma_tiempos_recepcion = 0
        
        # Conexiones independientes (Thread-safe)
        self.conn_pub = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1', 5672, credentials=pika.PlainCredentials('admin', 'adminpassword')))
        self.canal_pub = self.conn_pub.channel()
        
        self.conn_sub = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1', 5672, credentials=pika.PlainCredentials('admin', 'adminpassword')))
        self.canal_sub = self.conn_sub.channel()
        self.canal_sub.queue_declare(queue=self.cola_respuesta, durable=False)

        # Evento para sincronizar el final de la prueba
        self.prueba_terminada = threading.Event()

    def escuchar(self):
        def callback(ch, method, properties, body):
            # Sumamos el tiempo exacto en que llega la respuesta
            self.suma_tiempos_recepcion += time.time()
            self.mensajes_recibidos += 1
            
            # Imprimir progreso en la misma línea
            print(f"⏳ Recibiendo respuestas... {self.mensajes_recibidos}/{self.total_mensajes}", end="\r")
            
            if self.mensajes_recibidos >= self.total_mensajes:
                self.prueba_terminada.set()
                ch.stop_consuming()

        self.canal_sub.basic_consume(queue=self.cola_respuesta, on_message_callback=callback, auto_ack=True)
        try:
            self.canal_sub.start_consuming()
        except Exception:
            pass # Se ignora el error forzado al cerrar la conexión en caso de timeout

    def inyectar_carga(self):
        tipos = ["Solicitud de préstamo", "Consulta de préstamo", "Evaluación de préstamo", "Refinanciamiento"]
        
        print(f"🚀 Iniciando inyección de {self.total_mensajes} registros en RabbitMQ...")
        tiempo_inicio_total = time.time()
        
        for i in range(self.total_mensajes):
            tipo = random.choice(tipos)
            dni = str(random.randint(10000000, 99999999))
            monto = round(random.uniform(500, 60000), 2)
            
            mensaje = {
                "client_id": self.client_id, # Usamos SIEMPRE la misma cola base para el ruteo de retorno
                "tipo": tipo,
                "origen": "textos",
                "contenido": f"Requiero {tipo}. DNI {dni}, monto {monto}.",
                "dni": dni,
                "correo": f"user{dni}@test.com",
                "monto": monto
            }
            
            # Sumamos el tiempo exacto en que sale el mensaje
            self.suma_tiempos_envio += time.time()
            
            self.canal_pub.basic_publish(
                exchange='',
                routing_key='cola.ia',
                body=json.dumps(mensaje)
            )

        print("✅ Inyección completada. Esperando procesamiento de la IA y BD3...")
        
        # Esperar a que el consumidor termine, pero con un LÍMITE DE TIEMPO (Timeout)
        termino_bien = self.prueba_terminada.wait(timeout=30)
        tiempo_fin_total = time.time()
        
        print("\n" + "="*50)
        if not termino_bien:
            print("❌ ERROR/TIMEOUT: El tiempo de espera se agotó (30s sin completar).")
            print(f"Diagnóstico: Se enviaron {self.total_mensajes} mensajes pero solo retornaron {self.mensajes_recibidos}.")
            print("Acción recomendada: Revisa los contenedores con 'docker logs app-nodo-ia' para ver si hubo un colapso en la base de datos o fallo de ruteo.")
        else:
            # ==========================================
            # CÁLCULO DE MÉTRICAS EXACTAS
            # ==========================================
            tiempo_total_ejecucion = tiempo_fin_total - tiempo_inicio_total
            throughput = self.total_mensajes / tiempo_total_ejecucion
            latencia_promedio = (self.suma_tiempos_recepcion - self.suma_tiempos_envio) / self.total_mensajes
            
            print("📊 RESULTADOS DE LA PRUEBA DE ESTRÉS")
            print("="*50)
            print(f"Registros procesados : {self.mensajes_recibidos} / {self.total_mensajes}")
            print(f"Tiempo total         : {tiempo_total_ejecucion:.2f} segundos")
            print(f"Throughput           : {throughput:.2f} mensajes / segundo")
            print(f"Latencia promedio    : {latencia_promedio * 1000:.2f} milisegundos por mensaje")
        print("="*50)
        
        # Forzar el cierre para liberar hilos
        self.conn_pub.close()
        self.conn_sub.close()

if __name__ == "__main__":
    # Prueba primero con 2 para confirmar, luego súbelo a 1000
    prueba = PruebaEstres(1000) 
    
    hilo = threading.Thread(target=prueba.escuchar, daemon=True)
    hilo.start()
    
    prueba.inyectar_carga()