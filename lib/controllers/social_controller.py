from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from lib.schemas import SocialLoginRequest, TokenResponse
from lib.services.social_service import verify_google_token
from lib.services.auth_service import issue_tokens
from lib.utils.dependencies import get_db
from lib.utils.user_repository import get_or_create_social_user

router = APIRouter()

@router.post("/social-login", response_model=TokenResponse)
def social_login(req: SocialLoginRequest, db: Session = Depends(get_db)):
    if req.provider == "google":
        user_info = verify_google_token(req.access_token)
        user_id = get_or_create_social_user(db, user_info["email"], user_info["external_id"], provider="google")
        access, refresh = issue_tokens(db, user_id)
        return TokenResponse(access_token=access, refresh_token=refresh)
    else:
        raise HTTPException(status_code=400, detail="Unsupported provider")
