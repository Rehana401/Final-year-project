"""Quick script to check all registered users in the database."""
import sqlite3

conn = sqlite3.connect("app.db")
conn.row_factory = sqlite3.Row

rows = conn.execute("SELECT username, email, is_admin, createdAt, lastLogin FROM USERS").fetchall()

print(f"\n{'='*60}")
print(f"  Total Registered Users: {len(rows)}")
print(f"{'='*60}\n")

for i, r in enumerate(rows, 1):
    admin_tag = " [ADMIN]" if r["is_admin"] else ""
    last_login = r["lastLogin"] if r["lastLogin"] else "Never logged in"
    print(f"  {i}. {r['username']}{admin_tag}")
    print(f"     Email      : {r['email']}")
    print(f"     Created    : {r['createdAt']}")
    print(f"     Last Login : {last_login}")
    print()

conn.close()
