from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import allowed_domains
from app.models.user import User
from app.schemas.auth import LoginIn, Token, SignUpIn

router = APIRouter(prefix="/auth", tags=["Auth"])

# Email domain → University mapping
DOMAIN_TO_UNIVERSITY = {
    "cuiatk.edu.pk": "COMSATS Attock University",
    "uni.edu": "University of Education",
}

# New response schema for signup message only
class SignupResponse(BaseModel):
    message: str

@router.post("/signup", response_model=SignupResponse)
def signup(payload: SignUpIn, db: Session = Depends(get_db)):
    domain = payload.email.split("@")[-1].lower()
    if domain not in allowed_domains():
        raise HTTPException(status_code=400, detail="Email domain not allowed")

    username = payload.email.split("@")[0].lower()
    
    if db.query(User).filter(User.id == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Auto-fill university if known
    university = DOMAIN_TO_UNIVERSITY.get(domain)

    user = User(
        id=username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        university=university
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Registration successful. Please login to get your token."}

@router.post("/login", response_model=Token)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(user.id)
    return Token(access_token=token)

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_verified": user.is_verified,
        "university_name": user.university  # 👈 Added
    }
