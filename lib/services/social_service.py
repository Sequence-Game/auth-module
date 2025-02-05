import requests
from lib.config import settings

def verify_google_token(access_token: str) -> dict:
    """Verifies a Google access token and returns user info"""
    # Exchange token for user info
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(settings.SOCIAL_GOOGLE_USERINFO_URL, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # data contains email, sub (user id), etc.
        return {
            "email": data["email"],
            "external_id": data["sub"]
        }
    else:
        raise ValueError("Invalid social token")