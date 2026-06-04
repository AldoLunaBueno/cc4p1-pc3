const amqp = require('amqplib');

async function iniciarBorgIA() {

    try {
        const connection = await amqp.connect('amqp://admin:adminpassword@rabbitmq:5672');
        const channel = await connection.createChannel();
        
        await channel.assertQueue('cola.ia', { durable: false });
        await channel.assertQueue('cola.prestamo', { durable: false });
        
        console.log("Borg IA Cubes conectado a RabbitMQ");
        console.log("Escuchando cola.ia...");

        channel.consume('cola.ia', async (msg) => {
            if (msg !== null) {
                const payload = JSON.parse(msg.content.toString());
                const clientId = payload.client_id;
                const tipoSolicitud = payload.tipo || "Evaluación de préstamo"; 
                const montoPrestamo = payload.monto ? parseFloat(payload.monto) : 0.0;
                
                let estadoPrestamo = "PENDIENTE";
                let respuesta = "";

                // ========================================================
                // LÓGICA DE EVALUACIÓN (IA)
                // ========================================================
                if (tipoSolicitud === "Evaluación de préstamo" || tipoSolicitud === "Solicitud de préstamo") {
                    if (montoPrestamo > 50000) {
                        estadoPrestamo = "RECHAZADO";
                        respuesta = `El monto solicitado (S/.${montoPrestamo}) excede el límite automático. Pasa a evaluación manual.`;
                    } else {
                        estadoPrestamo = "APROBADO";
                        respuesta = `Felicidades, su solicitud por S/.${montoPrestamo} ha sido APROBADA de manera preliminar.`;
                    }
                } else if (tipoSolicitud === "Refinanciamiento") {
                    estadoPrestamo = "REFINANCIADO";
                    respuesta = `Ofrecemos una reestructuración de su deuda con nuevas condiciones.`;
                } else {
                    respuesta = `Mensaje categorizado como '${tipoSolicitud}'. Un asesor lo contactará.`;
                }

                // 1. Enviar orden de persistencia al nodo de préstamos
                const ordenDB = {
                    accion: "GUARDAR",
                    dni: payload.dni,
                    correo: payload.correo,
                    monto: montoPrestamo,
                    estado: estadoPrestamo,
                    tipo_prestamo: "PERSONAL"
                };
                channel.sendToQueue('cola.prestamo', Buffer.from(JSON.stringify(ordenDB)));

                // 2. Enviar respuesta al cliente
                const responsePayload = { client_id: clientId, respuesta: respuesta };
                const queueRespuesta = `respuesta.${clientId}`;
                await channel.assertQueue(queueRespuesta, { durable: false });
                channel.sendToQueue(queueRespuesta, Buffer.from(JSON.stringify(responsePayload)));

                console.log(`Decisión tomada para ${clientId}: ${estadoPrestamo}`);
                channel.ack(msg);
            }
        });
    } catch (err) {
        console.error("ERROR IA:", err);
    }
}

iniciarBorgIA();