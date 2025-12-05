from app import create_app, db
from app.models import User
import os
import logging

app = create_app()
logger = logging.getLogger(__name__)

def unlock(username):
    with app.app_context():
        u = User.query.filter_by(username=username).first()
        if not u:
            print("Gebruiker niet gevonden")
            return
        u.locked_until = None
        u.failed_attempts = 0
        # reset lock_count optionally
        if hasattr(u, 'lock_count'):
            u.lock_count = 0
        db.session.add(u)
        db.session.commit()
        logger.info(f"User unlocked: {username}")
        print(f"{username} ontgrendeld")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python unlock_user.py <username> <admin_token>")
        raise SystemExit(1)
    # simple token check
    ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
    if not ADMIN_TOKEN:
        print("ADMIN_TOKEN environment variable not set. Set it before running.")
        raise SystemExit(1)
    if sys.argv[2] != ADMIN_TOKEN:
        print("Invalid admin token")
        raise SystemExit(1)
    unlock(sys.argv[1])