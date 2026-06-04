package uni;

import java.sql.Connection;
import java.sql.DriverManager;
import com.rabbitmq.client.ConnectionFactory;

public class Main {
    public static void main(String[] args) {
        try {
            System.out.println("Esperando 15 segundos a que la infraestructura despierte...");
            Thread.sleep(15000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.out.println("Iniciando pruebas de conexión en Nodo Java...");

        // 1. Prueba PostgreSQL (BD2 Correo) en el puerto 5432
        String pgUrl = "jdbc:postgresql://postgres-bd2:5432/bd2_correo";
        try (Connection conn = DriverManager.getConnection(pgUrl, "root", "rootpassword")) {
            if (conn != null) {
                System.out.println("ÉXITO: Conectado a PostgreSQL (BD2_Correo)");
            }
        } catch (Exception e) {
            System.err.println("ERROR en PostgreSQL: " + e.getMessage());
        }

        // 2. Prueba RabbitMQ
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("rabbitmq");
        factory.setPort(5672);
        factory.setUsername("admin");
        factory.setPassword("adminpassword"); 
        
        try (com.rabbitmq.client.Connection mqConn = factory.newConnection()) {
            if (mqConn.isOpen()) {
                System.out.println("ÉXITO: Conectado a RabbitMQ");
            }
        } catch (Exception e) {
            System.err.println("ERROR en RabbitMQ: " + e.getMessage());
        }
    }
}