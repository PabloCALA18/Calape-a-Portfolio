from sqlalchemy import inspect, text
from app import create_app, db

app = create_app()

with app.app_context():
    print("Tablas:", inspect(db.engine).get_table_names())
    for tabla in ("usuario", "perfil", "experiencia", "educacion", "skill", "proyecto"):
        cantidad = db.session.execute(text(f"SELECT COUNT(*) FROM {tabla}")).scalar()
        print(f"{tabla}: {cantidad} filas")