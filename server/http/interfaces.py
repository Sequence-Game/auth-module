"""http router"""

from abc import ABC, abstractmethod

from fastapi import APIRouter


class HttpRouter(ABC):
    """HttpRouter"""

    @abstractmethod
    def get_router(self) -> APIRouter:
        """get_router"""
