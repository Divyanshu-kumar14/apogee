"""
APOGEE Backend - Development Server
Run this script to start the FastAPI development server.
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("=" * 60)
    print("APOGEE - Mission Awareness Dashboard")
    print("Starting FastAPI development server...")
    print("=" * 60)
    print("\nAPI Documentation available at:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("\nPress CTRL+C to stop the server\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
