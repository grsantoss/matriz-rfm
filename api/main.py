#!/usr/bin/env python
# RFM Insights - Main Application Entry Point

import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
from config.logging_config import setup_logging
logger = setup_logging(debug_mode=os.getenv('DEBUG', 'False').lower() == 'true')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import routers and middleware

from ..api.src.routes.rfm_api import router as rfm_router
from ..api.src.routes.auth_routes import router as auth_router
from ..api.src.routes.marketplace import router as marketplace_router
from ..api.src.controllers.middleware import RateLimiter, RequestValidator
from ..api.src.controllers.monitoring import MonitoringMiddleware
from ..api.src.models.api_utils import get_api_prefix

# Create FastAPI application
app = FastAPI(
    title="RFM Insights API",
    description="API for RFM analysis and customer segmentation",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Add rate limiting middleware
app.add_middleware(RateLimiter)

# Add request validation middleware
app.add_middleware(RequestValidator)

# Include routers with API prefix
api_prefix = get_api_prefix()
app.include_router(auth_router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
app.include_router(rfm_router, prefix=f"{api_prefix}/rfm", tags=["RFM Analysis"])
app.include_router(marketplace_router, prefix=f"{api_prefix}/marketplace", tags=["Marketplace"])

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "rfm-insights"}

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run application
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 