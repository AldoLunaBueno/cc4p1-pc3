const amqp = require('amqplib');
const mariadb = require('mariadb');

async function iniciarNodoPrestamo() {

    const pool = mariadb.createPool({
        host: 'mariadb-bd3',
        user: 'root',
        password: 'rootpassword',
        database: 'bd3_prestamos',
        port: 3306,
        connectionLimit: 5
    });

    try {
        const connection = await amqp.connect('amqp://admin:adminpassword@rabbitmq:5672');
        const channel = await connection.createChannel();
        await channel.assertQueue('cola.prestamo', { durable: false });
        
        console.log("Nodo Préstamo (LP3) conectado a BD3 y RabbitMQ");
        console.log("Escuchando órdenes en cola.prestamo...");

        channel.consume('cola.prestamo', async (msg) => {
            if (msg !== null) {
                const orden = JSON.parse(msg.content.toString());
                let conn;
                
                try {
                    conn = await pool.getConnection();
                    
                    if (orden.accion === "GUARDAR") {
                        let idUsuario;
                        
                        // Buscar o crear usuario
                        const usuarios = await conn.query("SELECT id_usuario FROM usuarios WHERE dni = ? OR correo = ? LIMIT 1", [orden.dni, orden.correo]);
                        if (usuarios.length > 0) {
                            idUsuario = usuarios[0].id_usuario;
                        } else {
                            const resUser = await conn.query("INSERT INTO usuarios (nombre, dni, correo, fecha_registro) VALUES (?, ?, ?, NOW())", ["Cliente", orden.dni, orden.correo]);
                            idUsuario = resUser.insertId;
                            await conn.query("INSERT INTO cuentas (id_usuario, saldo, estado, fecha_apertura, tipo_cuenta) VALUES (?, ?, ?, NOW(), ?)", [idUsuario, 0.0, "ACTIVA", "AHORRO"]);
                        }

                        // Insertar préstamo
                        if (orden.monto > 0) {
                            await conn.query(
                                "INSERT INTO prestamos (id_usuario, monto, tasa_interes, plazo, estado, fecha_inicio, fecha_fin, tipo_prestamo) VALUES (?, ?, ?, ?, ?, NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), ?)", 
                                [idUsuario, orden.monto, 12.5, 12, orden.estado, orden.tipo_prestamo]
                            );
                            console.log(`Préstamo guardado en BD3 para usuario ${idUsuario} con estado ${orden.estado}`);
                        }
                    }
                    channel.ack(msg);
                } catch (err) {
                    console.error("Error en persistencia:", err);
                    channel.ack(msg);
                } finally {
                    if (conn) conn.release();
                }
            }
        });
    } catch (err) {
        console.error("ERROR NODO PRÉSTAMO:", err);
    }
}

iniciarNodoPrestamo();