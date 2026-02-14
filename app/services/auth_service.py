from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from fastapi import HTTPException, status

class AuthService:
    @staticmethod
    def register_user(db: Session, user: UserCreate):
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = User(
            name=user.name,
            email=user.email,
            password_hash=hash_password(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, user: UserLogin):
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user:
            return None
        if not verify_password(user.password, db_user.password_hash):
            return None
        return db_user

    @staticmethod
    def create_tokens(user: User):
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
