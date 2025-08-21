from sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch user by email."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, name: str, email: str, password: str, role: str) -> User:
    """Create and store a new user."""
    try:
        db_user = User(name=name, email=email, password=password, role=role)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        print("❌ CRUD create_user error:", e)
        import traceback
        traceback.print_exc()
        raise
