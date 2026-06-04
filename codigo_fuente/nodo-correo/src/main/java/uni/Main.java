package uni;

import java.sql.Connection;
import java.sql.DriverManager;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.ConnectionFactory;

public class Main {
    // Regex heredados de Cristian
    private static final String REGEX_CORREO = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}";
    private static final String REGEX_DNI = "\\b\\d{8}\\b";
    private static final String REGEX_MONTO = "(?:prestamo|préstamo|credito|crédito|monto|s\\/\\.|\\$)\\s*(?:de\\s*)?(\\d+(?:\\.\\d{1,2})?)";

    public static void main(String[] args) {
        enviar();
    }

    private static void enviar() {
        try {
            // System.out.println("Esperando 15 segundos a que la infraestructura despierte...");
            // Thread.sleep(15000);

            // 1. Conexión a RabbitMQ
            ConnectionFactory factory = new ConnectionFactory();
            factory.setHost("rabbitmq");
            factory.setPort(5672);
            factory.setUsername("admin");
            factory.setPassword("adminpassword");
            
            try (com.rabbitmq.client.Connection mqConn = factory.newConnection();
                 Channel channel = mqConn.createChannel()) {
                 
                channel.queueDeclare("cola.ia", false, false, false, null);

                // 2. Simulación de un correo entrante (Esto normalmente vendría de PostgreSQL)
                String contenidoCorreo = "Estimados, solicito un crédito de 1500.50. Mi DNI es 87654321 y mi correo es cliente@mail.com";
                
                // 3. Extracción de datos con las Regex de Cristian
                String correo = extraer(REGEX_CORREO, contenidoCorreo, 0);
                String dni = extraer(REGEX_DNI, contenidoCorreo, 0);
                String monto = extraer(REGEX_MONTO, contenidoCorreo, 1);

                // 4. Armado manual del JSON (sin librerías de terceros)
                String jsonMsg = String.format(
                    "{\"client_id\":\"correo_1\", \"origen\":\"correos\", \"correo\":\"%s\", \"dni\":\"%s\", \"monto\":\"%s\", \"contenido\":\"%s\"}",
                    correo != null ? correo : "", 
                    dni != null ? dni : "", 
                    monto != null ? monto : "", 
                    contenidoCorreo
                );

                // 5. Publicar en RabbitMQ
                channel.basicPublish("", "cola.ia", null, jsonMsg.getBytes("UTF-8"));
                System.out.println("[Java] Correo procesado y enviado a cola.ia: " + jsonMsg);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    // Helper para aplicar las Regex
    private static String extraer(String regex, String texto, int grupo) {
        Pattern pattern = Pattern.compile(regex, Pattern.CASE_INSENSITIVE);
        Matcher matcher = pattern.matcher(texto);
        if (matcher.find()) {
            return matcher.group(grupo);
        }
        return null;
    }
}