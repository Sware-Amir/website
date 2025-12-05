import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
    
    # Bepaal het absolute pad naar de instance folder
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    INSTANCE_PATH = os.path.join(BASE_DIR, 'backend', 'instance')
    
    # Zorg dat de instance folder bestaat
    os.makedirs(INSTANCE_PATH, exist_ok=True)
    
    # Database configuratie met absoluut pad
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{os.path.join(INSTANCE_PATH, 'db.sqlite3')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False