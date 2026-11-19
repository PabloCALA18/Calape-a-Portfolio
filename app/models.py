from datetime import date
from flask_login import UserMixin
from sqlalchemy.orm import declared_attr
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


# ---------------------------------------------------------------
# ENCAPSULAMIENTO
# El hash de la contraseña es un atributo "privado" (_password_hash).
# Desde afuera nadie lo lee ni lo modifica directo: solo se usa
# a través de set_password() y check_password().
# ---------------------------------------------------------------
class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    _password_hash = db.Column("password_hash", db.String(255), nullable=False)

    perfil = db.relationship("Perfil", backref="usuario", uselist=False,
                             cascade="all, delete-orphan")

    def set_password(self, password):
        self._password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password_hash, password)

    @staticmethod
    def obtener_por_username(username):
        return Usuario.query.filter_by(username=username).first()


@login_manager.user_loader
def cargar_usuario(user_id):
    return db.session.get(Usuario, int(user_id))


# ---------------------------------------------------------------
# ABSTRACCIÓN
# ItemPortfolio es una clase abstracta (__abstract__ = True): no
# crea ninguna tabla, solo define lo que tiene y hace CUALQUIER
# ítem del portfolio (id, perfil, orden, guardar, eliminar...).
# Los detalles de cada tipo quedan en las clases hijas.
# ---------------------------------------------------------------
class ItemPortfolio(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    orden = db.Column(db.Integer, default=0)

    @declared_attr
    def perfil_id(cls):
        return db.Column(db.Integer, db.ForeignKey("perfil.id"), nullable=False)

    # Método abstracto: cada hijo lo implementa a su manera
    def titulo_visible(self):
        raise NotImplementedError("Cada ítem debe definir su título visible")

    def to_dict(self):
        return {"id": self.id, "orden": self.orden, "titulo": self.titulo_visible()}

    def guardar(self):
        db.session.add(self)
        db.session.commit()

    def eliminar(self):
        db.session.delete(self)
        db.session.commit()
        
    def datos(self):
        """Devuelve todas las columnas como diccionario (lo usa el modal de edición)."""
        d = {}
        for col in self.__table__.columns:
            valor = getattr(self, col.key)
            d[col.key] = valor.isoformat() if hasattr(valor, "isoformat") else valor
        return d


class Perfil(db.Model):
    __tablename__ = "perfil"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"),
                           unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    titulo = db.Column(db.String(100))
    acerca_de = db.Column(db.Text)
    foto = db.Column(db.String(255))
    banner = db.Column(db.String(255))
    logo = db.Column(db.String(255))

    redes = db.relationship("RedSocial", backref="perfil",
                            order_by="RedSocial.orden", cascade="all, delete-orphan")
    experiencias = db.relationship("Experiencia", backref="perfil",
                                   order_by="Experiencia.orden", cascade="all, delete-orphan")
    estudios = db.relationship("Educacion", backref="perfil",
                               order_by="Educacion.orden", cascade="all, delete-orphan")
    skills = db.relationship("Skill", backref="perfil",
                             order_by="Skill.orden", cascade="all, delete-orphan")
    proyectos = db.relationship("Proyecto", backref="perfil",
                                order_by="Proyecto.orden", cascade="all, delete-orphan")


# ---------------------------------------------------------------
# HERENCIA
# Todas estas clases heredan de ItemPortfolio: reutilizan id,
# orden, perfil_id, guardar() y eliminar() sin reescribirlos.
# ---------------------------------------------------------------
class RedSocial(ItemPortfolio):
    __tablename__ = "red_social"
    nombre = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    icono = db.Column(db.String(50))

    # POLIMORFISMO: mismo método, resultado distinto en cada clase
    def titulo_visible(self):
        return self.nombre


class Experiencia(ItemPortfolio):
    __tablename__ = "experiencia"
    empresa = db.Column(db.String(100), nullable=False)
    puesto = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    logo = db.Column(db.String(255))

    def titulo_visible(self):  # POLIMORFISMO
        return f"{self.puesto} en {self.empresa}"


class Educacion(ItemPortfolio):
    __tablename__ = "educacion"
    institucion = db.Column(db.String(100), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    anio_inicio = db.Column(db.Integer)
    anio_fin = db.Column(db.Integer)
    logo = db.Column(db.String(255))

    def titulo_visible(self):  # POLIMORFISMO
        return f"{self.titulo} - {self.institucion}"


class Skill(ItemPortfolio):
    __tablename__ = "skill"
    nombre = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.Enum("hard", "soft", "idioma"), nullable=False)
    porcentaje = db.Column(db.Integer, nullable=False)

    def titulo_visible(self):  # POLIMORFISMO
        return f"{self.nombre} ({self.porcentaje}%)"


class Proyecto(ItemPortfolio):
    __tablename__ = "proyecto"
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.Date)
    descripcion = db.Column(db.Text)
    link = db.Column(db.String(255))
    imagen = db.Column(db.String(255))

    def titulo_visible(self):  # POLIMORFISMO
        return self.nombre