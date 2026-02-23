"""
Micromarket Analytics Platform - FastAPI Application

Main application entry point with:
- Lifespan management for DB and Redis connections
- CORS middleware
- Analytics router inclusion
- Health check endpoint
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints import analytics
from app.core.logging import logger, log_request
from app.core.redis import init_redis, close_redis
from app.database import init_db, close_db, get_async_db
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.

    Startup:
    - Initialize database connection
    - Initialize Redis cache
    - Log startup

    Shutdown:
    - Close database connections
    - Close Redis connections
    - Log shutdown
    """
    # Startup
    logger.info("Starting up Micromarket Analytics Platform...")

    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    try:
        await init_redis()
        logger.info("Redis initialized successfully")
    except Exception as e:
        logger.error(f"Redis initialization failed: {e}")
        # Continue without cache if Redis fails
        pass

    logger.info("Application startup complete")
    yield

    # Shutdown
    logger.info("Shutting down Micromarket Analytics Platform...")

    try:
        await close_db()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Database shutdown error: {e}")

    try:
        await close_redis()
        logger.info("Redis connections closed")
    except Exception as e:
        logger.error(f"Redis shutdown error: {e}")

    logger.info("Application shutdown complete")


# Initialize FastAPI app with metadata
app = FastAPI(
    title="Micromarket Analytics Platform",
    description="""
    Production-ready analytics API for micromarket operators.

    ## Features

    - **Product Transaction Report**: Line-level transaction analysis with margin calculations
    - **Inventory Loss Report**: Overage/shrinkage/spoilage tracking with risk classification
    - **Market Sales Analysis**: Revenue distribution and contribution analysis
    - **Stock Health Report**: Stock level monitoring with risk categorization

    ## Authentication

    All endpoints require Bearer token authentication. Use demo tokens for testing:
    - `demo-token-1` (admin)
    - `demo-token-2` (manager)
    - `demo-token-3` (analyst)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/api/v1")


@app.get(
    "/",
    tags=["health"],
    summary="Root endpoint",
    response_description="Application status"
)
async def root():
    """
    Root endpoint returning basic application information.
    """
    return {
        "name": "Micromarket Analytics Platform",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs"
    }


@app.get(
    "/health",
    tags=["health"],
    summary="Health check endpoint",
    response_description="Health status of all services"
)
async def health_check(db: AsyncSession = Depends(get_async_db)):
    """
    Comprehensive health check endpoint.

    Verifies:
    - API is responsive
    - Database connection is active
    - Returns health status of all dependent services
    """
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "database": "unknown",
            "redis": "unknown"
        }
    }

    # Check database
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")

    # Check Redis
    try:
        from app.core.redis import redis_client
        if redis_client:
            await redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "not_initialized"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
        logger.error(f"Redis health check failed: {e}")

    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


@app.get(
    "/api/v1/health",
    tags=["health"],
    summary="API health check (v1)",
    include_in_schema=False
)
async def health_check_v1():
    """
    Backward compatible health check at /api/v1/health
    """
    return await health_check()


# Request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """
    Middleware to log all HTTP requests with timing and status.
    """
    from datetime import datetime
    start_time = datetime.utcnow()

    response = await call_next(request)

    duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

    # Skip logging for health checks to reduce noise
    if not request.url.path.endswith("/health"):
        log_request(
            logger,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms
        )

    # Add response time header
    response.headers["X-Response-Time-Ms"] = str(int(duration_ms))

    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "development") == "development",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
