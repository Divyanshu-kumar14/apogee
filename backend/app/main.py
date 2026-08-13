"""
APOGEE - Main FastAPI Application
Mission awareness dashboard for space operations.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base, SessionLocal
from .routers import health, debris, discovery, alerts
import logging
import asyncio
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background task handle
telemetry_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Starts telemetry generation on startup.
    """
    # Startup
    logger.info("Starting APOGEE application...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Start telemetry generation for ISS (default spacecraft)
    from .routers.health import telemetry_generation_task
    db = SessionLocal()
    
    global telemetry_task
    telemetry_task = asyncio.create_task(telemetry_generation_task("25544", db))
    logger.info("Telemetry generation task started for ISS (NORAD 25544)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down APOGEE application...")
    if telemetry_task:
        telemetry_task.cancel()
        try:
            await telemetry_task
        except asyncio.CancelledError:
            pass
    db.close()
    logger.info("Telemetry generation task stopped")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="APOGEE API",
    description="Mission awareness at every altitude - spacecraft health, debris risk, and scientific discovery",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add performance monitoring middleware
@app.middleware("http")
async def add_performance_monitoring(request: Request, call_next):
    """
    Monitor API response times and log slow requests.
    Adds X-Process-Time header to all responses.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add performance header
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    
    # Log slow requests (> 1 second)
    if process_time > 1.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {process_time:.2f}s"
        )
    
    return response

# Add GZip compression for responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)

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
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts & Explanations"])

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
        "database": "connected",
        "telemetry_generation": "active" if telemetry_task and not telemetry_task.done() else "inactive"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")