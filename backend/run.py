from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        # create tables if absent (dev convenience)
        db.create_all()
    app.run(host="127.0.0.1", port=5000, debug=True)