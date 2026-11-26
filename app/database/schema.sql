

CREATE TABLE usuario (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE perfil (
  id INT AUTO_INCREMENT PRIMARY KEY,
  usuario_id INT NOT NULL UNIQUE,
  nombre VARCHAR(100) NOT NULL,
  titulo VARCHAR(100),
  acerca_de TEXT,
  foto VARCHAR(255),
  banner VARCHAR(255),
  logo VARCHAR(255),
  FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

CREATE TABLE red_social (
  id INT AUTO_INCREMENT PRIMARY KEY,
  perfil_id INT NOT NULL,
  nombre VARCHAR(50) NOT NULL,
  url VARCHAR(255) NOT NULL,
  icono VARCHAR(50),
  orden INT DEFAULT 0,
  FOREIGN KEY (perfil_id) REFERENCES perfil(id) ON DELETE CASCADE
);

CREATE TABLE experiencia (
  id INT AUTO_INCREMENT PRIMARY KEY,
  perfil_id INT NOT NULL,
  empresa VARCHAR(100) NOT NULL,
  puesto VARCHAR(100) NOT NULL,
  descripcion TEXT,
  fecha_inicio DATE,
  fecha_fin DATE NULL,
  logo VARCHAR(255),
  orden INT DEFAULT 0,
  FOREIGN KEY (perfil_id) REFERENCES perfil(id) ON DELETE CASCADE
);

CREATE TABLE educacion (
  id INT AUTO_INCREMENT PRIMARY KEY,
  perfil_id INT NOT NULL,
  institucion VARCHAR(100) NOT NULL,
  titulo VARCHAR(150) NOT NULL,
  descripcion TEXT,
  anio_inicio YEAR,
  anio_fin YEAR NULL,
  logo VARCHAR(255),
  orden INT DEFAULT 0,
  FOREIGN KEY (perfil_id) REFERENCES perfil(id) ON DELETE CASCADE
);

CREATE TABLE skill (
  id INT AUTO_INCREMENT PRIMARY KEY,
  perfil_id INT NOT NULL,
  nombre VARCHAR(50) NOT NULL,
  tipo ENUM('hard','soft','idioma') NOT NULL,
  porcentaje TINYINT UNSIGNED NOT NULL,
  orden INT DEFAULT 0,
  FOREIGN KEY (perfil_id) REFERENCES perfil(id) ON DELETE CASCADE
);

CREATE TABLE proyecto (
  id INT AUTO_INCREMENT PRIMARY KEY,
  perfil_id INT NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  fecha DATE,
  descripcion TEXT,
  link VARCHAR(255),
  imagen VARCHAR(255),
  orden INT DEFAULT 0,
  FOREIGN KEY (perfil_id) REFERENCES perfil(id) ON DELETE CASCADE
);