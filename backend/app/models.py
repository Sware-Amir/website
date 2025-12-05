from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    files = db.relationship('File', backref='owner', lazy=True, cascade='all, delete-orphan')

    # Lockout fields
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    lock_count = db.Column(db.Integer, default=0, nullable=False)  # aantal keer geblokkeerd

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # New helpers
    def is_locked(self):
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False

    def register_failed_attempt(self, threshold=5, base_lock_minutes=5, max_lock_minutes=60):
        """
        Tel mislukte pogingen. Als threshold bereikt, zet tijdelijke lock.
        Lockduur groeit met lock_count: base * (2 ** lock_count), capped op max_lock_minutes.
        """
        self.failed_attempts = (self.failed_attempts or 0) + 1
        if self.failed_attempts >= threshold:
            # bereken lockduur
            lock_minutes = min(max_lock_minutes, base_lock_minutes * (2 ** (self.lock_count or 0)))
            self.locked_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
            self.lock_count = (self.lock_count or 0) + 1
            self.failed_attempts = 0
        db.session.add(self)
        db.session.commit()

    def reset_failed_attempts(self):
        self.failed_attempts = 0
        self.locked_until = None
        self.lock_count = 0
        db.session.add(self)
        db.session.commit()

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def get_size_formatted(self):
        """Return file size in human readable format"""
        size_bytes = self.file_size
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"