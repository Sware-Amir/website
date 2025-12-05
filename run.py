import os
from flask import render_template
from backend.app import create_app, db

# Zorg dat de instance folder bestaat voordat we de app maken
instance_path = os.path.join(os.path.dirname(__file__), 'backend', 'instance')
os.makedirs(instance_path, exist_ok=True)

# Maak de app
app = create_app()

# Registreer de routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/info')
def info():
    return render_template('info.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Maak database tabellen aan
    print("🚀 Starting Flask app on http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)