"""http server"""

from fastapi import APIRouter

from server.http.interfaces import HttpRouter


def combined_routers(routers: list[HttpRouter]):
    """combine routers"""
    api_router = APIRouter()

    for router in routers:
        api_router.include_router(router.get_router())

    return api_router
