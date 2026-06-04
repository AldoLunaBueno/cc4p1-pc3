CREATE TABLE mensajes_correo (
    id_correo SERIAL PRIMARY KEY,
    id_usuario INT,
    asunto VARCHAR(255),
    cuerpo TEXT,
    fecha_envio TIMESTAMP,
    tipo_correo VARCHAR(50),
    prioridad INT
);