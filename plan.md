### Sprint 1: Infraestructura y Conexiones (COMPLETADO)

**Objetivo:** Levantar las bases de datos y el middleware, y asegurar que los nodos puedan conectarse.

* **Issue 1: Despliegue de Bases de Datos.** [COMPLETADO]
    * **Acción:** Levantar tres instancias locales en contenedores Docker.
    * **Detalle:** BD1 en MySQL, BD2 en PostgreSQL y BD3 en MariaDB. Se optimizó el tiempo de arranque desactivando la persistencia estricta en disco y montando volúmenes en memoria RAM (`tmpfs`), además de implementar `healthchecks`.


* **Issue 2: Despliegue de RabbitMQ.** [COMPLETADO]
    * **Acción:** Levantar el servidor RabbitMQ en un contenedor independiente.
    * **Detalle:** Orquestado junto a las bases de datos con un `healthcheck` para asegurar que está listo antes de que los nodos se conecten.


* **Issue 3: Esqueletos de los Nodos (SO1, SO2, SO3).** [COMPLETADO]
    * **Acción:** Crear la base para los distintos lenguajes usando imágenes Docker con diferentes distribuciones Linux para cumplir el requisito de múltiples SO.
    * **Detalle:** * **nodo-texto (LP1):** Python sobre Alpine Linux.
    * **nodo-correo (LP2):** Java sobre Ubuntu (Jammy).
    * **nodo-prestamo (LP3) y nodo-ia (LPn):** Node.js sobre Debian.





### Sprint 2: Productores, Consumidores y Lógica "Mockeada" (COMPLETADO)

**Objetivo:** Lograr que los datos viajen desde los productores, pasen por la IA y terminen en la base de datos a través de RabbitMQ.

* **Issue 4: Nodos Productores (nodo-texto y nodo-correo).** [COMPLETADO]
    * **Acción:** Integrar el código base de Cristian para la extracción de datos.
    * **Detalle:** `nodo-texto` (Python) y `nodo-correo` (Java) leen sus fuentes, extraen DNI, monto y correo usando expresiones regulares, empaquetan la data en JSON sin usar librerías de terceros y la publican en `cola.ia`.


* **Issue 5: Nodo Borg IA Cubes (nodo-ia).** [COMPLETADO]
    * **Acción:** Procesar las intenciones y aplicar las reglas de negocio.
    * **Detalle:** Escucha `cola.ia`, aplica la lógica de evaluación (if/else) para determinar aprobación, rechazo o refinanciamiento, y publica la decisión final tanto en la cola de respuesta del cliente como en `cola.prestamo`.


* **Issue 6: Nodo MariaDB y Persistencia (nodo-prestamo).** [COMPLETADO]
    * **Acción:** Ejecutar las operaciones CRUD de forma aislada.
    * **Detalle:** Escucha `cola.prestamo` y utiliza un *pool* de conexiones nativo para crear o actualizar registros en las tablas de usuarios, cuentas y préstamos en MariaDB.



### Sprint 3: Concurrencia e Interfaz de Cliente (COMPLETADO)

**Objetivo:** Manejar peticiones y permitir el ingreso manual asíncrono.

* **Issue 7: Implementación de Multihilos (Crucial).** [COMPLETADO]
    * **Acción:** Aplicar concurrencia nativa para evitar bloqueos.
    * **Detalle:** Node.js ya maneja la concurrencia de base de datos asíncronamente mediante su *pool* de conexiones. El cliente en Python ya implementa `threading` (un hilo para el menú y un *daemon thread* para escuchar respuestas de RabbitMQ simultáneamente). Faltaría asegurar que los productores en Java/Python manejen múltiples lecturas concurrentes si se requiere.


* **Issue 8: Cliente de Ingreso Uno por Uno (LPn+1).** [COMPLETADO]
    * **Acción:** Crear la consola interactiva.
    * **Detalle:** Script `client.py` finalizado. Permite seleccionar el tipo de transacción, generar un ID de cliente único, enviar el texto/correo y recibir la respuesta en tiempo real en la terminal.



### Sprint 4: Métricas, Pruebas de Estrés y Empaquetado (PENDIENTE)

**Objetivo:** Cumplir con los requisitos de evaluación de rendimiento y preparar los entregables finales.

* **Issue 9: Script de Estrés (1000 Registros).** [PENDIENTE]
    * **Acción:** Desarrollar un script automatizado.
    * **Detalle:** Inyectar 1000 mensajes aleatorios a RabbitMQ en un bucle rápido para poner a prueba la capacidad de procesamiento del `nodo-ia` y las escrituras del `nodo-prestamo`.


* **Issue 10: Recolección de Métricas.** [PENDIENTE]
    * **Acción:** Instrumentar los nodos para medir el rendimiento.
    * **Detalle:** Registrar latencia total (tiempo desde que el mensaje sale del cliente o productor hasta que se guarda en BD3) y el *throughput* del sistema durante la prueba de estrés.


* **Issue 11: Empaquetado para UNIVIRTUAL.** [PENDIENTE]
    * **Acción:** Preparar los archivos finales.
    * **Detalle:** Exportar los diagramas de arquitectura y protocolo, asegurar que los scripts de BD (`bases_de_datos`) estén limpios, y adjuntar el informe y presentación en PDF para subir todo a UNIVIRTUAL dentro del plazo límite.

    