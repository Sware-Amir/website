from app import create_app
import os
app = create_app()
print("Flask app SQLALCHEMY_DATABASE_URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))
print("PERMANENT_SESSION_LIFETIME:", app.config.get('PERMANENT_SESSION_LIFETIME'))
print("Using PYTHON:", os.sys.executable)