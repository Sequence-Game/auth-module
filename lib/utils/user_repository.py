from sqlalchemy.orm import Session
from lib.models import User
from lib.services.hashing_service import hash_password
import uuid

def get_or_create_social_user(db: Session, email: str, external_id: str, provider: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            hashed_password=hash_password(uuid.uuid4().hex) # dummy password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user.id
