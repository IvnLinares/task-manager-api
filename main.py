from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get("/")
def root() -> dict[str, str]:
    """
    Root endpoint for the Task Manager API
    """
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
