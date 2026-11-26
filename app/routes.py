import io
import cloudinary
import cloudinary.uploader
import os
import uuid
from datetime import date
from flask import (render_template, redirect, url_for, flash, request,
                   jsonify, abort, current_app, send_from_directory)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import Date, Integer
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.forms import LoginForm
from app.models import (Usuario, Perfil, RedSocial, Experiencia,
                        Educacion, Skill, Proyecto)
from PIL import Image, ImageOps


def c(nombre, label, tipo="text", opciones=None, req=True):
    """Describe un campo de formulario (se usa para armar los modales)."""
    return {"nombre": nombre, "label": label, "tipo": tipo,
            "opciones": opciones, "req": req}


# Una sola configuración sirve para agregar / editar / eliminar / ordenar
# TODAS las secciones (evita repetir código).
SECCIONES = {
    "experiencia": {
        "modelo": Experiencia, "titulo": "Experiencia", "imagen": "logo",
        "campos": [c("puesto", "Puesto"), c("empresa", "Empresa"),
                   c("fecha_inicio", "Fecha de inicio", "date", req=False),
                   c("fecha_fin", "Fecha de fin (vacío = actual)", "date", req=False),
                   c("descripcion", "Descripción", "textarea", req=False)],
    },
    "educacion": {
        "modelo": Educacion, "titulo": "Educación", "imagen": "logo",
        "campos": [c("titulo", "Carrera / título"), c("institucion", "Institución"),
                   c("anio_inicio", "Año de inicio", "number", req=False),
                   c("anio_fin", "Año de fin (vacío = en curso)", "number", req=False),
                   c("descripcion", "Descripción", "textarea", req=False)],
    },
    "skill": {
        "modelo": Skill, "titulo": "Skill", "imagen": None,
        "campos": [c("nombre", "Nombre"),
                   c("tipo", "Tipo", "select", ["hard", "soft", "idioma"]),
                   c("porcentaje", "Nivel (0 a 100)", "number")],
    },
    "proyecto": {
        "modelo": Proyecto, "titulo": "Proyecto", "imagen": "imagen",
        "campos": [c("nombre", "Nombre"),
                   c("fecha", "Fecha de realización", "date", req=False),
                   c("descripcion", "Descripción", "textarea", req=False),
                   c("link", "Link a la evidencia", "url", req=False)],
    },
    "red_social": {
        "modelo": RedSocial, "titulo": "Red social", "imagen": None,
        "campos": [c("nombre", "Nombre (ej: GitHub)"), c("url", "URL", "url"),
                   c("icono", "Ícono FontAwesome (ej: fa-brands fa-github)", req=False)],
    },
}

EXTENSIONES = {"png", "jpg", "jpeg", "webp", "gif"}


def convertir(modelo, nombre, valor):
    """Convierte el texto del formulario al tipo de la columna (fecha, entero, texto)."""
    tipo = modelo.__table__.columns[nombre].type
    valor = (valor or "").strip()
    if valor == "":
        return None
    if isinstance(tipo, Date):
        return date.fromisoformat(valor)
    if isinstance(tipo, Integer):
        numero = int(valor)
        return max(0, min(100, numero)) if nombre == "porcentaje" else numero
    return valor


def guardar_imagen(archivo, max_lado=1200):
    """Valida, optimiza a WebP y sube a Cloudinary (o a static/ en desarrollo)."""
    if not archivo or not archivo.filename:
        return None
    try:
        img = Image.open(archivo.stream)
        img = ImageOps.exif_transpose(img)
        img.thumbnail((max_lado, max_lado))
        img = img.convert("RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB")
    except Exception:
        flash("El archivo no es una imagen válida")
        return None

    buffer = io.BytesIO()
    img.save(buffer, "webp", quality=82)
    buffer.seek(0)

    # Producción: Cloudinary (las imágenes quedan guardadas para siempre)
    if os.getenv("CLOUDINARY_URL"):
        resultado = cloudinary.uploader.upload(buffer, folder="portfolio", resource_type="image")
        return resultado["secure_url"]

    # Desarrollo local: carpeta static/
    carpeta = os.path.join(current_app.static_folder, "img", "uploads")
    os.makedirs(carpeta, exist_ok=True)
    nombre = f"{uuid.uuid4().hex}.webp"
    with open(os.path.join(carpeta, nombre), "wb") as f:
        f.write(buffer.getvalue())
    return f"uploads/{nombre}"


def llenar(item, cfg):
    """Copia los datos del formulario al objeto."""
    for campo in cfg["campos"]:
        setattr(item, campo["nombre"],
                convertir(type(item), campo["nombre"], request.form.get(campo["nombre"])))
    if cfg["imagen"]:
        ruta = guardar_imagen(request.files.get(cfg["imagen"]))
        if ruta:
            setattr(item, cfg["imagen"], ruta)


def volver():
    return redirect(request.referrer or url_for("index"))


def registrar_rutas(app):
    def img_url(ruta):
        if not ruta:
            return ""
        if ruta.startswith("http"):
            return ruta
        return url_for("static", filename="img/" + ruta)

    app.jinja_env.globals["img_url"] = img_url
    @app.errorhandler(403)  
    @app.errorhandler(404)
    @app.errorhandler(500)
    def error(e):
        codigo = getattr(e, "code", 500)
        mensajes = {403: "No tenés permiso para esto", 404: "Página no encontrada",
                    500: "Algo salió mal en el servidor"}
        return render_template("error.html", codigo=codigo, mensaje=mensajes.get(codigo)), codigo

    @app.errorhandler(413)
    def archivo_grande(e):
        flash("El archivo supera el máximo de 4 MB")
        return redirect(request.referrer or url_for("index"))
    @app.context_processor
    def datos_globales():
        # Disponibles en todas las plantillas
        return {"perfil": Perfil.query.first(), "SECCIONES": SECCIONES}

    # ---------- PÁGINAS ----------
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/descargar-documentacion")
    def descargar_documentacion():
        carpeta = os.path.join(current_app.static_folder, "docs")
        return send_from_directory(carpeta, "documentacion.pdf", as_attachment=True,
                                   download_name="Documentacion_Portfolio.pdf")
    @app.route("/descargar-cv")
    def descargar_cv():
        carpeta = os.path.join(current_app.static_folder, "cv")
        return send_from_directory(carpeta, "cv.pdf", as_attachment=True,
                                   download_name="CV.pdf")

    # ---------- LOGIN / LOGOUT ----------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = LoginForm()
        if form.validate_on_submit():
            usuario = Usuario.obtener_por_username(form.username.data)
            if usuario and usuario.check_password(form.password.data):
                login_user(usuario)
                return redirect(url_for("index"))
            flash("Usuario o contraseña incorrectos")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))

    # ---------- EDICIÓN (todas protegidas con @login_required) ----------
    @app.route("/agregar/<seccion>", methods=["POST"])
    @login_required
    def agregar(seccion):
        cfg = SECCIONES.get(seccion) or abort(404)
        modelo = cfg["modelo"]
        try:
            item = modelo(perfil_id=current_user.perfil.id)
            llenar(item, cfg)
            ultimo = db.session.query(db.func.max(modelo.orden)).filter(
                modelo.perfil_id == current_user.perfil.id).scalar() or 0
            item.orden = ultimo + 1          # se agrega al final
            item.guardar()
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            flash("No se pudo guardar: revisá los datos ingresados")
        return volver()

    @app.route("/editar/<seccion>/<int:id>", methods=["POST"])
    @login_required
    def editar(seccion, id):
        cfg = SECCIONES.get(seccion) or abort(404)
        item = db.get_or_404(cfg["modelo"], id)
        if item.perfil_id != current_user.perfil.id:
            abort(403)
        try:
            llenar(item, cfg)
            item.guardar()
        except (ValueError, SQLAlchemyError):
            db.session.rollback()
            flash("No se pudo guardar: revisá los datos ingresados")
        return volver()

    @app.route("/eliminar/<seccion>/<int:id>", methods=["POST"])
    @login_required
    def eliminar(seccion, id):
        cfg = SECCIONES.get(seccion) or abort(404)
        item = db.get_or_404(cfg["modelo"], id)
        if item.perfil_id != current_user.perfil.id:
            abort(403)
        item.eliminar()
        return volver()

    @app.route("/ordenar/<seccion>", methods=["POST"])
    @login_required
    def ordenar(seccion):
        """Recibe la lista de ids en el nuevo orden (drag and drop)."""
        cfg = SECCIONES.get(seccion) or abort(404)
        ids = (request.get_json() or {}).get("ids", [])
        for posicion, id_ in enumerate(ids):
            item = db.session.get(cfg["modelo"], int(id_))
            if item and item.perfil_id == current_user.perfil.id:
                item.orden = posicion
        db.session.commit()
        return jsonify(ok=True)

    @app.route("/perfil/editar", methods=["POST"])
    @login_required
    def perfil_editar():
        p = current_user.perfil
        p.nombre = request.form.get("nombre", "").strip() or p.nombre
        p.titulo = request.form.get("titulo", "").strip()
        p.acerca_de = request.form.get("acerca_de", "").strip()
        db.session.commit()
        return volver()

    @app.route("/perfil/imagen/<campo>", methods=["POST"])
    @login_required
    def perfil_imagen(campo):
        if campo not in ("foto", "banner", "logo"):
            abort(404)
        ruta = guardar_imagen(request.files.get("archivo"),
                              max_lado=1800 if campo == "banner" else 800)        
        if ruta:
            setattr(current_user.perfil, campo, ruta)
            db.session.commit()
        return volver()