"""auth router"""

from fastapi import APIRouter

from server.http.router import HttpRouter
from models.auth.interfaces import AuthService


class AuthRouter(HttpRouter):
    """AuthRouter"""

    def __init__(self, auth_service: AuthService):
        self.router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
        self.auth_service = auth_service

        self._register_routes()

    def get_router(self):
        """get router"""
        return self.router

    def _register_routes(self):
        """register routes"""

        @self.router.post("/register")
        def register():
            """register"""
            return {"data": "register"}

        @self.router.post("/login")
        def login():
            """login"""
            return {"data": "login"}

        @self.router.post("/refresh")
        def refresh():
            return {"data": "refresh"}

        @self.router.post("/logout")
        def logout():
            return {"data": "logout"}

        @self.router.post("/social-login")
        def social_login():
            """social login"""
            return {"data": "social login"}
