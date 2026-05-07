-- TABLA: usuarios

CREATE TABLE IF NOT EXISTS usuarios (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    nombre    VARCHAR(100) NOT NULL,
    correo    VARCHAR(150) NOT NULL,
    telefono  VARCHAR(20)  NOT NULL,
    fecha_nac DATE         NOT NULL
);

-- TABLA: mascotas

CREATE TABLE IF NOT EXISTS mascotas (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    nombre     VARCHAR(100) NOT NULL,
    tipo       VARCHAR(50)  NOT NULL,
    raza       VARCHAR(100) NOT NULL,
    edad       INT          NOT NULL,
    id_usuario INT          NOT NULL
);


-- DATOS DE PRUEBA

INSERT INTO usuarios (nombre, correo, telefono, fecha_nac) VALUES
    ('Valentina Ríos',    'valentina@petshop.com', '3101234567', '1995-03-12'),
    ('Andrés Castillo',   'andres@petshop.com',    '3209876543', '1988-07-24'),
    ('Camila Herrera',    'camila@petshop.com',    '3154561234', '2000-11-05'),
    ('Diego Bermúdez',    'diego@petshop.com',     '3008887766', '1992-01-30'),
    ('Sofía Mora',        'sofia@petshop.com',     '3172223344', '1998-09-18');

INSERT INTO mascotas (nombre, tipo, raza, edad, id_usuario) VALUES
    ('Toby',    'Perro',  'Golden Retriever', 3, 1),
    ('Mishi',   'Gato',   'Siamés',           5, 2),
    ('Coco',    'Perro',  'Beagle',           2, 2),
    ('Nube',    'Gato',   'Persa',            4, 3),
    ('Bóxer',   'Perro',  'Bóxer',            6, 4),
    ('Piolín',  'Pájaro', 'Canario',          1, 5),
    ('Manchas', 'Perro',  'Dálmata',          7, 1),
    ('Luna',    'Gato',   'Angora',           3, 5);
