from sqlalchemy.orm import Session
from app.database.database import SessionLocal, init_db
from app.models.models import UserRole  # Make sure this class is defined in models

def seed_user_roles():
    init_db()  # Ensure tables exist

    db: Session = SessionLocal()
    try:
        roles_data = [
            {"role_name": "user", "role_level": 1},
            {"role_name": "admin", "role_level": 2},
            {"role_name": "super_user", "role_level": 3},
        ]

        for role in roles_data:
            existing = db.query(UserRole).filter(UserRole.role_name == role["role_name"]).first()
            if not existing:
                new_role = UserRole(**role)
                db.add(new_role)

        db.commit()
        print("✅ User roles table seeded successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_user_roles()
