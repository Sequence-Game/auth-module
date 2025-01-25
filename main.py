"""entry point for the application"""

from fastapi import FastAPI


app: FastAPI


def main() -> None:
    """main"""
    global app

    app = FastAPI()


if __name__ == "__main__":
    import uvicorn

    main()

    uvicorn.run(app, host="127.0.0.1", port=8000)
