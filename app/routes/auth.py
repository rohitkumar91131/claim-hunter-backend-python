from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.models.user import User
from jose import JWTError, jwt
from app.config import settings

router = APIRouter()

# Dependency to get current user from cookie
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse)
def register(response: Response, user: UserCreate, db: Session = Depends(get_db)):
    new_user = AuthService.register_user(db, user)
    tokens = AuthService.create_tokens(new_user)
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Set to True in production
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=False
    )
    
    return new_user

@router.post("/login")
def login(response: Response, user: UserLogin, db: Session = Depends(get_db)):
    db_user = AuthService.authenticate_user(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    tokens = AuthService.create_tokens(db_user)
    
    # Set cookies
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=False
    )
    
    return {"message": "Login successful"}

@router.post("/refresh")
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    
    if not refresh_token:
        raise credentials_exception

    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise credentials_exception
            
        # Verify user still exists
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
             raise credentials_exception

        # Issue new tokens
        tokens = AuthService.create_tokens(user)
        
        # Update access token cookie
        response.set_cookie(
            key="access_token",
            value=tokens["access_token"],
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            samesite="lax",
            secure=False
        )
        
        # Optionally rotate refresh token here too
        
        return {"message": "Token refreshed"}
        
    except JWTError:
        raise credentials_exception

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logout successful"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
