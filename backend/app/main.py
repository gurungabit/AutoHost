from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import connections, automation, websocket


app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    connections.router,
    prefix=f"{settings.api_prefix}/connections",
    tags=["connections"]
)
app.include_router(
    automation.router,
    prefix=f"{settings.api_prefix}/automation",
    tags=["automation"]
)
app.include_router(
    websocket.router,
    prefix=f"{settings.api_prefix}/ws",
    tags=["websocket"]
)


@app.get("/")
async def root():
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
