"""
APOGEE - Main FastAPI Application
Mission awareness dashboard for space operations.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import health, debris, discovery
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

# Initialize FastAPI app
app = FastAPI(
    title="APOGEE API",
    description="Mission awareness at every altitude - spacecraft health, debris risk, and scientific discovery",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["Health Monitor"])
app.include_router(debris.router, prefix="/api/debris", tags=["Debris Risk"])
app.include_router(discovery.router, prefix="/api/discovery", tags=["Discovery Module"])

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "APOGEE API",
        "version": "1.0.0",
        "description": "Mission awareness dashboard for space operations",
        "endpoints": {
            "health": "/api/health",
            "debris": "/api/debris",
            "discovery": "/api/discovery",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "APOGEE API",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
