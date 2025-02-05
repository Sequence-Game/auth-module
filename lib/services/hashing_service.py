import bcrypt

def hash_password(plain: str) -> str:
    """Hashes a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    """Verifies a plain password against a hashed password"""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))