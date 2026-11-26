from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
    usuarios = Usuario.query.all()
    if not usuarios:
        print("No hay usuarios en la base")
        raise SystemExit

    print("Usuarios existentes:")
    for u in usuarios:
        print(f" - {u.username!r}")

    username = input("\nUsuario a eliminar: ")
    u = Usuario.obtener_por_username(username)
    if not u:
        print("Ese usuario no existe")
    else:
        print("Se va a borrar también su perfil y TODO su contenido.")
        if input("Escribí SI para confirmar: ") == "SI":
            db.session.delete(u)
            db.session.commit()
            print("Usuario eliminado")
        else:
            print("Cancelado")