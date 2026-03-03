import sys
import os
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.api.auth import create_user, DB_FILE

def reset_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS users")
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            subjects TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def run_seed():
    print("Seeding database (wiping old users)...")
    reset_db()
    
    # 1. Admin User
    create_user(
        email="admin@graide.com",
        password="adminpassword",
        name="System Admin",
        role="admin",
        subjects=""
    )
    print("Created Admin User: admin@graide.com / adminpassword")
    
    # 2. Math Teacher (Mapping to Subject_1)
    create_user(
        email="math@graide.com",
        password="password123",
        name="Sarah (Math Teacher)",
        role="teacher",
        subjects="Subject_1"
    )
    print("Created Teacher User: math@graide.com / password123 (Subject_1)")
        
    # 3. Science Teacher (Mapping to Subject_2 & 3)
    create_user(
        email="science@graide.com",
        password="password123",
        name="John (Science Teacher)",
        role="teacher",
        subjects="Subject_2,Subject_3"
    )
    print("Created Teacher User: science@graide.com / password123 (Subject_2, Subject_3)")
        
    # 4. English Teacher (Mapping to Subject_4 & 5)
    create_user(
        email="english@graide.com",
        password="password123",
        name="Emma (English Teacher)",
        role="teacher",
        subjects="Subject_4,Subject_5"
    )
    print("Created Teacher User: english@graide.com / password123 (Subject_4, Subject_5)")

    print("Seeding complete.")

if __name__ == "__main__":
    run_seed()
