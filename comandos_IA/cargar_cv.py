from app import create_app, db

app = create_app()

with app.app_context():
    with open("cargar_cv.sql", encoding="utf-8") as f:
        lineas = [l for l in f.read().splitlines() if not l.strip().startswith("--")]

    sentencias = [s.strip() for s in "\n".join(lineas).split(";") if s.strip()]

    # Una sola conexión para que @pid valga en todas las sentencias
    with db.engine.begin() as conn:
        for s in sentencias:
            conn.exec_driver_sql(s)

    print(f"Listo: {len(sentencias)} sentencias ejecutadas")