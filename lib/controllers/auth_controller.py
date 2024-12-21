from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from lib.schemas import UserLoginRequest, TokenResponse, RegisterRequest, LogoutRequest
from lib.services.auth_service import (
    authenticate_user, issue_tokens, refresh_access_token, logout, register_user
)
from lib.utils.dependencies import get_db

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user_id = register_user(db, req.email, req.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    access, refresh = issue_tokens(db, user_id)
    return TokenResponse(access_token=access, refresh_token=refresh)

@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user_id = authenticate_user(db, req.email, req.password)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access, refresh = issue_tokens(db, user_id)
    return TokenResponse(access_token=access, refresh_token=refresh)

@router.post("/refresh", response_model=TokenResponse)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    try:
        new_access = refresh_access_token(db, refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return TokenResponse(access_token=new_access, token_type="bearer")

@router.post("/logout")
def do_logout(req: LogoutRequest, db: Session = Depends(get_db)):
    logout(db, req.refresh_token)
    return {"detail": "Logged out successfully."}
