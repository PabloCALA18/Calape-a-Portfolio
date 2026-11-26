-- Toma el perfil que ya creaste con crear_usuario.py
SET @pid = (SELECT id FROM perfil ORDER BY id LIMIT 1);

-- (Opcional) Si querés volver a correr este archivo sin duplicar datos,
-- descomentá estas 5 líneas. OJO: borran lo que ya hayas cargado en esas secciones.
DELETE FROM red_social WHERE perfil_id = @pid;
DELETE FROM experiencia WHERE perfil_id = @pid;
DELETE FROM educacion WHERE perfil_id = @pid;
DELETE FROM skill WHERE perfil_id = @pid;
DELETE FROM proyecto WHERE perfil_id = @pid;

-- ================= PERFIL Y CONTACTO =================
UPDATE perfil SET
  nombre = 'Pablo Calapeña',
  titulo = 'Estudiante · Técnico en Programación',
  acerca_de = 'Estudiante universitario de la UTN. Cuento con sólida formación en desarrollo de software, abarcando tanto frontend como backend, y manejo de diversos lenguajes de programación.',
  email = 'pablocalape@gmail.com',
  telefono = '+54 9 351 810 7091',
  ubicacion = 'Alta Gracia, Córdoba, Argentina'
WHERE id = @pid;

-- ================= REDES SOCIALES =================
INSERT INTO red_social (perfil_id, nombre, url, icono, orden) VALUES
(@pid, 'GitHub', 'https://github.com/PabloCALA18', 'fa-brands fa-github', 1);

-- ================= EXPERIENCIA =================
INSERT INTO experiencia (perfil_id, empresa, puesto, descripcion, fecha_inicio, fecha_fin, orden) VALUES
(@pid, 'Olimpiada Matemática Argentina (OMA)', 'Participante',
 'Participación durante tres años consecutivos en la OMA a nivel provincial, con menciones por desempeño destacado. Experiencia en resolución de problemas complejos.',
 NULL, NULL, 1),
(@pid, 'Venta de alimentos (ámbito escolar)', 'Emprendedor',
 'Emprendimiento personal de 1 año. Generé ingresos constantes mediante la venta de productos, desarrollé habilidades de negociación y trato con clientes, gestioné compras, precios y control de stock, y aprendí a manejar dinero y tomar decisiones comerciales.',
 NULL, NULL, 2);

-- ================= EDUCACIÓN =================
INSERT INTO educacion (perfil_id, institucion, titulo, descripcion, anio_inicio, anio_fin, orden) VALUES
(@pid, 'Instituto Técnico Renault', 'Técnico en Programación',
 'Desarrollo de proyectos de programación tanto en frontend como backend. Resolución de problemas lógicos y matemáticos aplicados a la informática.',
 2018, 2025, 1),
(@pid, 'Universidad Tecnológica Nacional (UTN)', 'Estudiante universitario',
 'Carrera en curso.',
 NULL, NULL, 2);

-- ================= SKILLS =================
-- Hard skills (los porcentajes son una propuesta: ajustalos a tu nivel real)
INSERT INTO skill (perfil_id, nombre, tipo, porcentaje, orden) VALUES
(@pid, 'Python', 'hard', 65, 1),
(@pid, 'JavaScript', 'hard', 60, 2),
(@pid, 'Hojas de cálculo', 'hard', 70, 3);

-- Soft skills (círculos)
INSERT INTO skill (perfil_id, nombre, tipo, porcentaje, orden) VALUES
(@pid, 'Disciplina y responsabilidad', 'soft', 85, 4),
(@pid, 'Autodidacta y proactivo', 'soft', 85, 5),
(@pid, 'Pensamiento analítico y resolutivo', 'soft', 80, 6),
(@pid, 'Comunicación efectiva', 'soft', 75, 7),
(@pid, 'Adaptabilidad a distintos entornos', 'soft', 80, 8),
(@pid, 'Trabajo en equipo', 'soft', 85, 9);

-- Idiomas
INSERT INTO skill (perfil_id, nombre, tipo, porcentaje, orden) VALUES
(@pid, 'Español (nativo)', 'idioma', 100, 10),
(@pid, 'Inglés (B1)', 'idioma', 50, 11),
(@pid, 'Francés (A1)', 'idioma', 15, 12);

-- ================= PROYECTOS =================
INSERT INTO proyecto (perfil_id, nombre, fecha, descripcion, link, orden) VALUES
(@pid, 'Portfolio web full stack', CURDATE(),
 'Portfolio personal desarrollado con Flask, Jinja2 y MySQL. Incluye login con Flask-WTF, modo edición con modales, drag and drop, diseño responsive y base de datos desplegada en Clever Cloud.',
 NULL, 1),
(@pid, 'Proyectos académicos de programación', NULL,
 'Desarrollo de proyectos tanto en frontend como backend, resolución de problemas lógicos y matemáticos aplicados a la informática, y participación activa en trabajos grupales y proyectos tecnológicos escolares.',
 NULL, 2);