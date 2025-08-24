from database import SessionLocal
from crud import create_user, get_user_by_username
from schemas import UserCreate

def main():
    db = SessionLocal()
    admin_user = get_user_by_username(db, username="admin")
    if admin_user:
        print("Admin user already exists.")
    else:
        admin_create = UserCreate(
            username="admin",
            password="adminpassword", # Please change this in a production environment
            role="admin"
        )
        create_user(db, admin_create)
        print("Admin user created successfully.")
        print("Username: admin")
        print("Password: adminpassword")
    db.close()

if __name__ == "__main__":
    main()
