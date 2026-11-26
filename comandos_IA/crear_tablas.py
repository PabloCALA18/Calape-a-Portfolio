from app import create_app, db
from app import models  # carga los modelos

app = create_app()

with app.app_context():
    db.create_all()
    print("Tablas creadas:")
    for nombre in db.metadata.tables:
        print(" -", nombre)