from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.config import settings
from app.models.models import User
from app.schemas.api_schemas import UserRegister, UserLogin, TokenResponse, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register(req: UserRegister, db: Session = Depends(get_db)):
    email_clean = req.email.lower().strip()
    existing = db.query(User).filter(User.email == email_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "email_exists", "message": "An account with this email already exists."}},
        )

    # Assign admin if email matches configured ADMIN_EMAIL
    role = "admin" if (settings.ADMIN_EMAIL and email_clean == settings.ADMIN_EMAIL.lower().strip()) else "user"

    user = User(
        email=email_clean,
        password_hash=hash_password(req.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        role=user.role,
    )


@router.post("/login", response_model=TokenResponse)
def login(req: UserLogin, db: Session = Depends(get_db)):
    email_clean = req.email.lower().strip()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "invalid_credentials", "message": "Incorrect email or password."}},
        )

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        email=user.email,
        role=user.role,
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
    )
