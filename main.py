"""entry point for the application"""

from fastapi import FastAPI

from server.http.router import combined_routers


app: FastAPI


def main() -> None:
    """main"""
    global app

    app = FastAPI()

    app.include_router(combined_routers([]))


if __name__ == "__main__":
    import uvicorn

    main()

    uvicorn.run(app, host="127.0.0.1", port=8000)
