CREATE DATABASE IF NOT EXISTS bd3_prestamos;
USE bd3_prestamos;

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    dni VARCHAR(20),
    correo VARCHAR(100),
    telefono VARCHAR(20),
    direccion TEXT,
    fecha_registro DATETIME
);
CREATE TABLE cuentas (
    id_cuenta INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    saldo DECIMAL(10,2),
    estado VARCHAR(50),
    fecha_apertura DATETIME,
    tipo_cuenta VARCHAR(50),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE prestamos (
    id_prestamo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    monto DECIMAL(10,2),
    tasa_interes DECIMAL(5,2),
    plazo INT,
    estado VARCHAR(50),
    fecha_inicio DATETIME,
    fecha_fin DATETIME,
    tipo_prestamo VARCHAR(50),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);