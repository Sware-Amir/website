import os
import shutil
import sqlite3
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'db.sqlite3'))

if not os.path.exists(DB_PATH):
    print(f"DB niet gevonden op {DB_PATH}. Controleer dat je vanuit de backend map draait en dat instance/db.sqlite3 bestaat.")
    raise SystemExit(1)

# Backup maken
bak_path = DB_PATH + f".bak-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
shutil.copy2(DB_PATH, bak_path)
print(f"Backup gemaakt: {bak_path}")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Vind users-table (zoek op username + password_hash)
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]

user_table = None
table_cols = []
for t in tables:
    cur.execute(f"PRAGMA table_info('{t}')")
    cols = [row[1] for row in cur.fetchall()]
    if 'username' in cols and 'password_hash' in cols:
        user_table = t
        table_cols = cols
        break

if not user_table:
    print("Kon geen gebruikers-tabel vinden (zoek naar username + password_hash). Tabellen:", tables)
    conn.close()
    raise SystemExit(1)

print(f"Gevonden gebruikers-tabel: {user_table}")
# Voeg kolommen toe indien nodig
if 'failed_attempts' not in table_cols:
    print("Voeg kolom failed_attempts toe...")
    cur.execute(f"ALTER TABLE '{user_table}' ADD COLUMN failed_attempts INTEGER NOT NULL DEFAULT 0")
else:
    print("Kolom failed_attempts bestaat al")

if 'locked_until' not in table_cols:
    print("Voeg kolom locked_until toe...")
    cur.execute(f"ALTER TABLE '{user_table}' ADD COLUMN locked_until DATETIME")
else:
    print("Kolom locked_until bestaat al")

if 'lock_count' not in table_cols:
    print("Voeg kolom lock_count toe...")
    cur.execute(f"ALTER TABLE '{user_table}' ADD COLUMN lock_count INTEGER NOT NULL DEFAULT 0")
else:
    print("Kolom lock_count bestaat al")

conn.commit()
conn.close()
print("Klaar. Herstart de server en probeer opnieuw in te loggen.")