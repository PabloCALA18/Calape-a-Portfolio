from getpass import getpass
from app import create_app, db
from app.models import Usuario, Perfil

app = create_app()

with app.app_context():
    username = input("Usuario: ")
    password = getpass("Contraseña: ")

    u = Usuario(username=username)
    u.set_password(password)
    u.perfil = Perfil(nombre=input("Tu nombre: "), titulo="Full Stack Developer Jr")

    db.session.add(u)
    db.session.commit()
    print("Usuario creado")