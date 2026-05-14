import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.api.auth import create_user, reset_users_table


def run_seed():
    print("Seeding database (wiping old users)...")
    reset_users_table()

    create_user(
        email="admin@graide.com",
        password="adminpassword",
        name="System Admin",
        role="admin",
        subjects="",
    )
    print("Created Admin User: admin@graide.com / adminpassword")

    create_user(
        email="math@graide.com",
        password="password123",
        name="Sarah (Math Teacher)",
        role="teacher",
        subjects="Subject_1",
    )
    print("Created Teacher User: math@graide.com / password123 (Subject_1)")

    create_user(
        email="science@graide.com",
        password="password123",
        name="John (Science Teacher)",
        role="teacher",
        subjects="Subject_2,Subject_3",
    )
    print("Created Teacher User: science@graide.com / password123 (Subject_2, Subject_3)")

    create_user(
        email="english@graide.com",
        password="password123",
        name="Emma (English Teacher)",
        role="teacher",
        subjects="Subject_4,Subject_5",
    )
    print("Created Teacher User: english@graide.com / password123 (Subject_4, Subject_5)")

    print("Seeding complete.")


if __name__ == "__main__":
    run_seed()
