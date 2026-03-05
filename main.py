from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.api import api_router
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.rate_limit import limiter, _rate_limit_exceeded_handler

# Ensure all models are imported and initialized so SQLAlchemy can map relationships
import app.models  # noqa

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Define allowed origins for CORS
origins = [
    "http://localhost:5173",  # React Frontend default Vite port
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root() -> dict[str, str]:
    """
    Root endpoint for the Task Manager API
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
