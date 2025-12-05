import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)

# Base directory van frontend
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))

def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static")
    )

    # Bepaal het absolute pad voor de database
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    INSTANCE_PATH = os.path.join(PROJECT_ROOT, 'backend', 'instance')
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    
    # Configuratie
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "DATABASE_URI", 
        f"sqlite:///{os.path.join(INSTANCE_PATH, 'db.sqlite3')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB max file size

    # Session lifetime
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    # hCaptcha sitekey beschikbaar in templates
    app.config['HCAPTCHA_SITEKEY'] = os.getenv('HCAPTCHA_SITEKEY', '')

    # Initialiseer extensions
    db.init_app(app)
    
    # Talisman met toegestane CDN sources
    csp = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",
            "https://cdn.tailwindcss.com",
            "https://hcaptcha.com",
            "https://*.hcaptcha.com",
            "https://assets.hcaptcha.com"
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",
            "https://hcaptcha.com",
            "https://assets.hcaptcha.com"
        ],
        'frame-src': [
            "'self'",
            "https://hcaptcha.com",
            "https://*.hcaptcha.com",
            "https://assets.hcaptcha.com"
        ]
    }
    Talisman(app, content_security_policy=csp, force_https=False)
    
    limiter.init_app(app)

    # Blueprint importeren en registreren
    from .routes import main_bp
    from .auth import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    return app