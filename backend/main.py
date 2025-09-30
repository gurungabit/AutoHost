import uvicorn
from app.core.config import settings


def main():
    """Run the FastAPI application"""
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )


if __name__ == "__main__":
    main()
