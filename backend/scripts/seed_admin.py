from sqlalchemy.orm import Session
from app.database.database import SessionLocal, init_db
from app.models.models import User
from sqlalchemy import func

def seed_admin_user():
    init_db()

    db: Session = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            new_admin = User(
                id="admin_manual_1",  #can use a UUID or some unique ID here
                email="admin@example.com",
                name="admin_saugat",
                picture="no image available",
                role_level=2,  # admin level
                last_login_at=func.now()
            )
            db.add(new_admin)
            db.commit()
            print("✅ Admin user 'admin_saugat' added successfully.")
        else:
            print("⚠️ Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin_user()
