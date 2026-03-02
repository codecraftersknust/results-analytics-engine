import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.api.auth import create_user, get_user_by_email

def run_seed():
    print("Seeding database...")
    
    # 1. Admin User
    if not get_user_by_email("admin@graide.com"):
        create_user(
            email="admin@graide.com",
            password="adminpassword",
            name="System Admin",
            role="admin",
            subjects=""
        )
        print("Created Admin User: admin@graide.com / adminpassword")
    
    # 2. Math Teacher
    if not get_user_by_email("math@graide.com"):
        create_user(
            email="math@graide.com",
            password="password123",
            name="Sarah (Math Teacher)",
            role="teacher",
            subjects="Mathematics"
        )
        print("Created Teacher User: math@graide.com / password123 (Mathematics)")
        
    # 3. Science Teacher
    if not get_user_by_email("science@graide.com"):
        create_user(
            email="science@graide.com",
            password="password123",
            name="John (Science Teacher)",
            role="teacher",
            subjects="Physics,Chemistry,Biology"
        )
        print("Created Teacher User: science@graide.com / password123 (Sciences)")
        
    # 4. English Teacher
    if not get_user_by_email("english@graide.com"):
        create_user(
            email="english@graide.com",
            password="password123",
            name="Emma (English Teacher)",
            role="teacher",
            subjects="English Literature,English Language"
        )
        print("Created Teacher User: english@graide.com / password123 (English)")

    print("Seeding complete.")

if __name__ == "__main__":
    run_seed()
