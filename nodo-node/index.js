const mariadb = require('mariadb');
const amqp = require('amqplib');

async function probarConexiones() {
    console.log("Esperando 15 segundos a que la infraestructura despierte...");
    await new Promise(r => setTimeout(r, 15000));
    console.log("Iniciando pruebas de conexión en Nodo Node.js...");

    // 1. Prueba MariaDB (BD3 Préstamos) en el puerto 3307
    try {
        const pool = mariadb.createPool({
            host: 'mariadb-bd3',
            user: 'root',
            password: 'rootpassword',
            database: 'bd3_prestamos',
            port: 3306
        });
        const conn = await pool.getConnection();
        console.log("ÉXITO: Conectado a MariaDB (BD3_Prestamos)");
        conn.release();
        await pool.end();
    } catch (err) {
        console.error("ERROR en MariaDB:", err.message);
    }

    // 2. Prueba RabbitMQ
    try {
        // La URL de conexión incluye las credenciales admin:adminpassword
        const connection = await amqp.connect('amqp://admin:adminpassword@rabbitmq:5672');
        console.log("ÉXITO: Conectado a RabbitMQ");
        await connection.close();
    } catch (err) {
        console.error("ERROR en RabbitMQ:", err.message);
    }
}

probarConexiones();