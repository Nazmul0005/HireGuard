"""
FastAPI chatbot backend with intent classification and multiple response modes.
"""

import os
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from com.mhire.app.services.chatbot.chat_router import router as chat_router
from com.mhire.app.services.verification.verification_router import router as verification_router
from com.mhire.app.services.resume.resume_router import router as resume_router
from com.mhire.app.services.verification_system.face_verification.face_verification_router import router as face_router





# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting up application...")
    yield
    # Shutdown
    logger.info("Shutting down application...")
    # Add any cleanup code here (e.g., closing database connections)

# Create FastAPI app
app = FastAPI(
    title="Rkasim AI Endpoints",
    description="API Documentation for rkasim Project",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers

app.include_router(chat_router)
app.include_router(verification_router)
app.include_router(resume_router)
app.include_router(face_router)

@app.get("/")
async def root():
    return {"message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        workers=1
    )