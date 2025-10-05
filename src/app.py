from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from src.router import api_router
from src.database import engine, Base
from src.config import get_settings

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI Agent Builder API",
    description="API for building voice agents with AI assistance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error", "error": str(exc)}
    )


# Include routers
app.include_router(api_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Agent Builder API", "version": "1.0.0"}


@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Agent Builder API",
        "docs": "/docs",
        "health": "/health",
    }
