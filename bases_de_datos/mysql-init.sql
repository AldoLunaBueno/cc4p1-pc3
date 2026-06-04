CREATE DATABASE IF NOT EXISTS bd1_texto;
USE bd1_texto;

CREATE TABLE mensajes_texto (
    id_mensaje INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    contenido TEXT,
    fecha_envio DATETIME,
    tipo_mensaje VARCHAR(50),
    canal VARCHAR(50)
);

