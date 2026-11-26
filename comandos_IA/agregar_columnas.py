from sqlalchemy import inspect
from app import create_app, db

app = create_app()

NUEVAS = {
    "email": "VARCHAR(120)",
    "telefono": "VARCHAR(40)",
    "ubicacion": "VARCHAR(120)",
}

with app.app_context():
    existentes = {c["name"] for c in inspect(db.engine).get_columns("perfil")}
    with db.engine.begin() as conn:
        for nombre, tipo in NUEVAS.items():
            if nombre in existentes:
                print(f"{nombre}: ya existe")
            else:
                conn.exec_driver_sql(f"ALTER TABLE perfil ADD COLUMN {nombre} {tipo}")
                print(f"{nombre}: agregada")