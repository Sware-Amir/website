import os, sqlite3, shutil
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance', 'db.sqlite3'))
print("DB_PATH:", DB_PATH)
if not os.path.exists(DB_PATH):
    print("ERROR: DB niet gevonden.")
    raise SystemExit(1)

print("Maak backup...")
bak = DB_PATH + f".bak-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
shutil.copy2(DB_PATH, bak)
print("Backup:", bak)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tabellen:", tables)

for t in tables:
    cur.execute(f"PRAGMA table_info('{t}')")
    cols = [row[1] for row in cur.fetchall()]
    print(f"Columns in {t}: {cols}")

# Probeer expliciet 'user' en 'users' en voeg missende kolommen toe
for candidate in ('user', 'users'):
    cur.execute(f"PRAGMA table_info('{candidate}')")
    info = cur.fetchall()
    if info:
        cols = [r[1] for r in info]
        print(f"Found candidate table '{candidate}' with columns: {cols}")
        for col, ddl in (('failed_attempts',"INTEGER NOT NULL DEFAULT 0"),
                         ('locked_until',"DATETIME"),
                         ('lock_count',"INTEGER NOT NULL DEFAULT 0")):
            if col not in cols:
                try:
                    print(f"Adding column {col} to {candidate}...")
                    cur.execute(f"ALTER TABLE '{candidate}' ADD COLUMN {col} {ddl}")
                    print(f"Added {col}")
                except Exception as e:
                    print("FAILED to add", col, ":", e)
            else:
                print(col, "exists")
conn.commit()
conn.close()
print("Done.")