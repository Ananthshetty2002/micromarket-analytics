requirement\backend\app\database.py
```

```python
"""
Database configuration for async SQLAlchemy with PostgreSQL
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import os

# Database configuration from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@postgres:5432/micromarket"
)

# Create async engine optimized for PostgreSQL 16
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    # Enable prepared statement cache for better performance
    connect_args={
        "statement_cache_size": 5000,
        "prepared_statement_cache_size": 5000,
        "max_cached_statement_lifetime": 600,
    }
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_async_db() -> AsyncSession:
    """
    Dependency for FastAPI to get async database session.

    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables.
    Call this on application startup.
    """
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections.
    Call this on application shutdown.
    """
    await engine.dispose()
```

```python
"""
SQLAlchemy models for Micromarket Analytics Platform
"""
from sqlalchemy import (
    Column, String, Numeric, DateTime, ForeignKey, Integer,
    Boolean, Text, func
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
from decimal import Decimal
import uuid

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class Operator(Base):
    __tablename__ = "operators"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="viewer")  # admin/manager/analyst/viewer
    phone = Column(String(50))
    timezone = Column(String(50), default="UTC")
    preferences = Column(Text)  # JSON string
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    micromarkets = relationship("Micromarket", back_populates="operator")
    chat_sessions = relationship("ChatSession", back_populates="operator")


class Micromarket(Base):
    __tablename__ = "micromarkets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    operator_id = Column(String(36), ForeignKey("operators.id"), nullable=False)
    name = Column(String(255), nullable=False)
    code = Column(String(100), unique=True, nullable=False)
    address = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    timezone = Column(String(50), default="UTC")
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    status = Column(String(50), default="active")  # active/inactive/maintenance
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    operator = relationship("Operator", back_populates="micromarkets")
    inventory = relationship("Inventory", back_populates="market")
    sales = relationship("Sale", back_populates="market")
    movements = relationship("InventoryMovement", back_populates="market")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    code = Column(String(100))
    description = Column(Text)
    parent_id = Column(String(36), ForeignKey("categories.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    barcode = Column(String(100), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(String(36), ForeignKey("categories.id"), index=True)
    unit_price = Column(Numeric(10, 2), default=0)
    cost_price = Column(Numeric(10, 2), default=0)
    currency = Column(String(3), default="USD")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    market_id = Column(String(36), ForeignKey("micromarkets.id"), nullable=False, index=True)
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    quantity_available = Column(Integer, default=0)
    reorder_point = Column(Integer, default=0)
    max_stock_level = Column(Integer, default=0)
    last_counted_at = Column(DateTime)
    status = Column(String(50), default="in_stock")  # in_stock/low_stock/out_of_stock
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="inventory")
    market = relationship("Micromarket", back_populates="inventory")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    market_id = Column(String(36), ForeignKey("micromarkets.id"), nullable=False, index=True)
    sale_date = Column(DateTime, nullable=False, index=True)
    transaction_number = Column(String(100), unique=True, nullable=False)
    channel = Column(String(50), default="pos")  # pos/online/manual
    total_amount = Column(Numeric(10, 2), default=0)
    item_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    market = relationship("Micromarket", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", lazy="selectin")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    sale_id = Column(String(36), ForeignKey("sales.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    market_id = Column(String(36), ForeignKey("micromarkets.id"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
    user_name = Column(String(100))
    movement_type = Column(String(50), nullable=False)  # overage, shrinkage, spoilage, adjustment
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2))
    total_cost = Column(Numeric(10, 2))
    unit_price = Column(Numeric(10, 2))
    total_price = Column(Numeric(10, 2))
    reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    market = relationship("Micromarket", back_populates="movements")
    product = relationship("Product")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    operator_id = Column(String(36), ForeignKey("operators.id"), nullable=False)
    market_id = Column(String(36), ForeignKey("micromarkets.id"))
    title = Column(String(255))
    message_count = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    operator = relationship("Operator", back_populates="chat_sessions")
```

```python
"""
Redis client configuration for caching and pub/sub
"""
import redis.asyncio as redis
from typing import Optional
import os

# Redis connection settings
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Global redis client instance
redis_client: Optional[redis.Redis] = None


async def init_redis() -> redis.Redis:
    """Initialize Redis connection"""
    global redis_client
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_keepalive=True,
        health_check_interval=30
    )
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        await init_redis()
    return redis_client


class RedisCache:
    """Helper class for Redis caching operations"""

    @staticmethod
    async def get(key: str) -> Optional[str]:
        """Get value from cache"""
        client = await get_redis()
        return await client.get(key)

    @staticmethod
    async def set(key: str, value: str, expire: int = 300):
        """Set value in cache with expiration (seconds)"""
        client = await get_redis()
        await client.setex(key, expire, value)

    @staticmethod
    async def setex(key: str, seconds: int, value: str):
        """Set value with expiration"""
        client = await get_redis()
        await client.setex(key, seconds, value)

    @staticmethod
    async def delete(key: str):
        """Delete key from cache"""
        client = await get_redis()
        await client.delete(key)

    @staticmethod
    async def delete_pattern(pattern: str):
        """Delete all keys matching pattern"""
        client = await get_redis()
        keys = await client.keys(pattern)
        if keys:
            await client.delete(*keys)

    @staticmethod
    async def flush():
        """Flush all cache (use with caution)"""
        client = await get_redis()
        await client.flushdb()


# Convenience functions for direct import
async def cache_get(key: str) -> Optional[str]:
    return await RedisCache.get(key)


async def cache_set(key: str, value: str, expire: int = 300):
    return await RedisCache.set(key, value, expire)


async def cache_delete(key: str):
    return await RedisCache.delete(key)
```

```python
"""
FastAPI Analytics Endpoints for Micromarket Platform

Provides 4 production-ready report endpoints:
1. Product Transaction Report
2. Inventory Loss Report (Overage/Shrinkage/Spoilage)
3. Market Sales Analysis
4. Stock Health Report

Features:
- Redis caching with configurable TTL
- Pagination support
- Comprehensive error handling
- P95 < 300ms performance target
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import hashlib

from app.database import get_async_db
from app.services.analytics_service import (
    ProductTransactionService,
    InventoryLossService,
    MarketSalesService,
    StockHealthService
)
from app.schemas.analytics import (
    ProductTransactionReport,
    InventoryLossReport,
    MarketSalesReport,
    StockHealthReport
)
from app.core.redis import redis_client
from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter(prefix="/analytics", tags=["analytics"])


def generate_cache_key(prefix: str, **params) -> str:
    """
    Generate deterministic cache key from parameters.

    Uses MD5 hash of sorted JSON parameters to ensure consistent keys
    regardless of parameter order.
    """
    param_str = json.dumps(params, sort_keys=True, default=str)
    hash_key = hashlib.md5(param_str.encode()).hexdigest()
    return f"analytics:{prefix}:{hash_key}"


@router.get(
    "/product-transactions",
    response_model=ProductTransactionReport,
    summary="Product Transaction Report",
    description="""
    Generate detailed transaction report with revenue, cost, and margin calculations.

    **Calculations:**
    - Line Revenue = Quantity × Price
    - Line Cost = Quantity × Cost
    - Gross Margin = Revenue − Cost
    - Margin % = (Margin / Revenue) × 100
    - Return Rate = Returns / Total Quantity

    **Features:**
    - Pagination support (limit/offset)
    - Date range filtering
    - Market filtering
    - Top 10 products by revenue included
    - Redis cached for 5 minutes
    """,
    response_description="Transaction report with line items and summary"
)
async def get_product_transactions(
    market_id: Optional[str] = Query(
        None,
        description="Filter by micromarket ID",
        example="550e8400-e29b-41d4-a716-446655440000"
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Start date filter (ISO 8601)",
        example="2025-01-01T00:00:00Z"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="End date filter (ISO 8601)",
        example="2025-01-31T23:59:59Z"
    ),
    limit: int = Query(
        1000,
        ge=1,
        le=5000,
        description="Records per page (max 5000)"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Pagination offset"
    ),
    use_cache: bool = Query(
        True,
        description="Use Redis cache for performance"
    ),
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
) -> ProductTransactionReport:
    """
    Get Product Transaction Report with line-level calculations.

    Returns detailed transaction data with calculated fields and summary metrics.
    Optimized for P95 < 300ms response time through database indexing and caching.
    """
    request_start = datetime.utcnow()

    try:
        # Generate cache key from all query parameters
        cache_key = generate_cache_key(
            "product_transactions",
            market_id=market_id,
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
            limit=limit,
            offset=offset,
            user_id=current_user.id
        )

        # Check Redis cache
        if use_cache:
            try:
                cached_data = await redis_client.get(cache_key)
                if cached_data:
                    logger.info(
                        f"Cache hit for product-transactions",
                        extra={
                            "cache_key": cache_key,
                            "user_id": current_user.id,
                            "duration_ms": (datetime.utcnow() - request_start).total_seconds() * 1000
                        }
                    )
                    cached_json = json.loads(cached_data)
                    return ProductTransactionReport(**cached_json)
            except Exception as cache_error:
                logger.warning(f"Cache read error: {cache_error}")
                # Continue without cache

        # Fetch data from service layer
        result = await ProductTransactionService.get_transactions(
            db=db,
            market_id=market_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        # Build response
        response = ProductTransactionReport(
            report_type="product_transactions",
            generated_at=datetime.utcnow(),
            filters={
                "market_id": market_id,
                "start_date": start_date,
                "end_date": end_date
            },
            data=result["transactions"],
            summary=result["summary"],
            pagination=result["pagination"]
        )

        # Cache successful response (5 minutes TTL)
        if use_cache:
            try:
                await redis_client.setex(
                    cache_key,
                    300,  # 5 minutes
                    json.dumps(response.model_dump(), default=str)
                )
            except Exception as cache_error:
                logger.warning(f"Cache write error: {cache_error}")

        # Log performance metrics
        duration_ms = (datetime.utcnow() - request_start).total_seconds() * 1000
        logger.info(
            f"Product transaction report generated",
            extra={
                "duration_ms": duration_ms,
                "record_count": len(result["transactions"]),
                "total_count": result["pagination"]["total"],
                "user_id": current_user.id
            }
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error generating product transaction report: {str(e)}",
            extra={"user_id": current_user.id},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get(
    "/inventory-loss",
    response_model=InventoryLossReport,
    summary="Overage/Shrinkage/Spoilage Report",
    description="""
    Generate inventory loss report with risk classification.

    **Calculations:**
    - Loss Value = Quantity × Cost
    - Retail Impact = Quantity × ProductPrice
    - Shrinkage % = (Total Shrinkage / Total Inventory Value) × 100

    **Risk Classification:**
    - Critical: Shrinkage > 5%
    - High: Shrinkage 2-5%
    - Medium: Shrinkage 1-2%
    - Low: Shrinkage < 1%

    **Cached for 10 minutes** (loss data changes less frequently)
    """,
    response_description="Inventory loss report with aggregations and risk assessment"
)
async def get_inventory_loss(
    market_id: Optional[str] = Query(
        None,
        description="Filter by micromarket ID"
    ),
    start_date: Optional[datetime] = Query(
        None,
        description="Start date filter"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="End date filter"
    ),
    change_type: Optional[str] = Query(
        None,
        regex="^(overage|shrinkage|spoilage)$",
        description="Filter by specific change type"
    ),
    use_cache: bool = Query(True, description="Use Redis cache"),
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
) -> InventoryLossReport:
    """
    Get Overage/Shrinkage/Spoilage Report.

    Tracks inventory adjustments, calculates loss values, and provides
    risk classification based on shrinkage percentages.
    """
    request_start = datetime.utcnow()

    try:
        cache_key = generate_cache_key(
            "inventory_loss",
            market_id=market_id,
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
            change_type=change_type,
            user_id=current_user.id
        )

        # Check cache
        if use_cache:
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    logger.info("Cache hit for inventory-loss")
                    return InventoryLossReport(**json.loads(cached))
            except Exception as cache_error:
                logger.warning(f"Cache read error: {cache_error}")

        # Fetch data
        result = await InventoryLossService.get_loss_report(
            db=db,
            market_id=market_id,
            start_date=start_date,
            end_date=end_date,
            change_type=change_type
        )

        response = InventoryLossReport(
            report_type="inventory_loss",
            generated_at=datetime.utcnow(),
            filters={
                "market_id": market_id,
                "start_date": start_date,
                "end_date": end_date,
                "change_type": change_type
            },
            items=result["items"],
            summary=result["summary"]
        )

        # Cache for 10 minutes
        if use_cache:
            try:
                await redis_client.setex(
                    cache_key,
                    600,  # 10 minutes
                    json.dumps(response.model_dump(), default=str)
                )
            except Exception as cache_error:
                logger.warning(f"Cache write error: {cache_error}")

        duration_ms = (datetime.utcnow() - request_start).total_seconds() * 1000
        logger.info(
            f"Inventory loss report generated",
            extra={
                "duration_ms": duration_ms,
                "item_count": len(result["items"]),
                "risk_level": result["summary"].risk_level,
                "user_id": current_user.id
            }
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating inventory loss report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get(
    "/market-sales",
    response_model=MarketSalesReport,
    summary="Micro Market Sales Analysis",
    description="""
    Analyze sales performance across all markets with contribution percentages.

    **Calculations:**
    - Revenue per Location (sum of all sales)
    - Contribution % = Market Revenue / Total Revenue × 100
    - Concentration Ratio = Top 3 Markets % of Total Revenue

    **Features:**
    - Ranked by revenue (highest first)
    - Identifies highest and lowest performing markets
    - Average ticket size per market
    - Transaction counts
    """,
    response_description="Market sales analysis with rankings and contribution metrics"
)
async def get_market_sales(
    start_date: Optional[datetime] = Query(
        None,
        description="Filter sales from this date"
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter sales until this date"
    ),
    use_cache: bool = Query(True, description="Use Redis cache"),
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
) -> MarketSalesReport:
    """
    Get Micro Market Sales Analysis.

    Provides market-level revenue analysis with contribution percentages
    and concentration metrics for portfolio assessment.
    """
    request_start = datetime.utcnow()

    try:
        cache_key = generate_cache_key(
            "market_sales",
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
            user_id=current_user.id
        )

        # Check cache
        if use_cache:
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    logger.info("Cache hit for market-sales")
                    return MarketSalesReport(**json.loads(cached))
            except Exception as cache_error:
                logger.warning(f"Cache read error: {cache_error}")

        # Fetch data
        result = await MarketSalesService.get_market_sales(
            db=db,
            start_date=start_date,
            end_date=end_date
        )

        response = MarketSalesReport(
            report_type="market_sales",
            generated_at=datetime.utcnow(),
            filters={
                "start_date": start_date,
                "end_date": end_date
            },
            markets=result["markets"],
            summary=result["summary"]
        )

        # Cache for 5 minutes
        if use_cache:
            try:
                await redis_client.setex(
                    cache_key,
                    300,
                    json.dumps(response.model_dump(), default=str)
                )
            except Exception as cache_error:
                logger.warning(f"Cache write error: {cache_error}")

        duration_ms = (datetime.utcnow() - request_start).total_seconds() * 1000
        logger.info(
            f"Market sales report generated",
            extra={
                "duration_ms": duration_ms,
                "market_count": len(result["markets"]),
                "total_revenue": result["summary"].total_revenue,
                "user_id": current_user.id
            }
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating market sales report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get(
    "/stock-health",
    response_model=StockHealthReport,
    summary="Stock Analysis Report",
    description="""
    Analyze stock levels with risk classification and reorder alerts.

    **Stock Classification:**
    - Stockout Risk: < 25% of max stock
    - Healthy: 30-70% of max stock
    - Overstock Risk: > 90% of max stock
    - Warning: 25-30% or 70-90% (transition zones)

    **Includes:**
    - Risk category distribution (% and counts)
    - Products below reorder threshold
    - Critical stockout alerts
    - Overstock recommendations

    **Cached for 2 minutes** (stock changes frequently)
    """,
    response_description="Stock health report with risk classification"
)
async def get_stock_health(
    market_id: Optional[str] = Query(
        None,
        description="Filter by specific market"
    ),
    use_cache: bool = Query(True, description="Use Redis cache"),
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
) -> StockHealthReport:
    """
    Get Stock Health Report.

    Classifies inventory into risk categories based on stock levels
    relative to maximum stock settings. Identifies products needing
    immediate attention (stockouts or overstock).
    """
    request_start = datetime.utcnow()

    try:
        cache_key = generate_cache_key(
            "stock_health",
            market_id=market_id,
            user_id=current_user.id
        )

        # Check cache
        if use_cache:
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    logger.info("Cache hit for stock-health")
                    return StockHealthReport(**json.loads(cached))
            except Exception as cache_error:
                logger.warning(f"Cache read error: {cache_error}")

        # Fetch data
        result = await StockHealthService.get_stock_health(
            db=db,
            market_id=market_id
        )

        response = StockHealthReport(
            report_type="stock_health",
            generated_at=datetime.utcnow(),
            filters={"market_id": market_id},
            risk_distribution=result["risk_distribution"],
            below_reorder_threshold=result["below_reorder_threshold"],
            summary=result["summary"]
        )

        # Cache for 2 minutes (stock data changes frequently)
        if use_cache:
            try:
                await redis_client.setex(
                    cache_key,
                    120,  # 2 minutes
                    json.dumps(response.model_dump(), default=str)
                )
            except Exception as cache_error:
                logger.warning(f"Cache write error: {cache_error}")

        duration_ms = (datetime.utcnow() - request_start).total_seconds() * 1000
        logger.info(
            f"Stock health report generated",
            extra={
                "duration_ms": duration_ms,
                "total_products": result["summary"].total_products,
                "critical_stockouts": result["summary"].critical_stockouts,
                "user_id": current_user.id
            }
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating stock health report: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.post(
    "/clear-cache",
    summary="Clear Analytics Cache",
    description="Manually clear Redis cache for analytics endpoints. Requires admin role.",
    status_code=status.HTTP_204_NO_CONTENT
)
async def clear_analytics_cache(
    pattern: str = Query(
        "analytics:*",
        description="Redis key pattern to clear"
    ),
    current_user = Depends(get_current_user)
):
    """
    Clear Redis cache for analytics reports.

    Only accessible by admin users. Useful when data is updated
    and reports need immediate refresh.
    """
    # Check admin role
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    try:
        # Find and delete matching keys
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
            logger.info(
                f"Cache cleared",
                extra={
                    "pattern": pattern,
                    "keys_deleted": len(keys),
                    "user_id": current_user.id
                }
            )
        return None

    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )
```

```python
# services/analytics_service.py
from sqlalchemy import select, func, case, desc, literal_column
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from app.models import Sale, SaleItem, Product, Inventory, InventoryMovement, Micromarket, Category
from app.schemas.analytics import (
    TransactionLineItem, TransactionSummary, TopProduct,
    LossItem, LossSummary,
    MarketSalesItem,
    StockHealthItem
)


class ProductTransactionService:
    """Service for Product Transaction Report analytics"""

    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        market_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Generate Product Transaction Report with line-level calculations
        """
        # Build base query with line calculations
        line_revenue = SaleItem.quantity * SaleItem.unit_price
        line_cost = SaleItem.quantity * SaleItem.unit_cost
        line_margin = line_revenue - line_cost

        query = (
            select(
                Sale.id.label("sale_id"),
                Sale.transaction_number,
                Sale.sale_date,
                Micromarket.name.label("location"),
                Product.sku.label("product_code"),
                Product.name.label("product_description"),
                SaleItem.quantity,
                SaleItem.unit_price.label("price"),
                SaleItem.unit_cost.label("cost"),
                line_revenue.label("line_revenue"),
                line_cost.label("line_cost"),
                line_margin.label("line_margin"),
                case(
                    (line_revenue > 0, (line_margin / line_revenue) * 100),
                    else_=0
                ).label("margin_percent"),
                case(
                    (SaleItem.quantity < 0, True),
                    else_=False
                ).label("is_return")
            )
            .join(Sale, SaleItem.sale_id == Sale.id)
            .join(Product, SaleItem.product_id == Product.id)
            .join(Micromarket, Sale.market_id == Micromarket.id)
        )

        # Apply filters
        if market_id:
            query = query.where(Sale.market_id == market_id)
        if start_date:
            query = query.where(Sale.sale_date >= start_date)
        if end_date:
            query = query.where(Sale.sale_date <= end_date)

        # Get total count for pagination
        count_query = select(func.count()).select_from(query.subquery())
        total_count = await db.scalar(count_query)

        # Execute paginated query
        query = query.order_by(desc(Sale.sale_date)).limit(limit).offset(offset)
        result = await db.execute(query)
        rows = result.all()

        # Calculate totals
        total_revenue = sum(row.line_revenue for row in rows)
        total_cost = sum(row.line_cost for row in rows)
        total_margin = total_revenue - total_cost
        return_quantity = sum(abs(row.quantity) for row in rows if row.is_return)
        total_quantity = sum(abs(row.quantity) for row in rows)
        return_rate = (return_quantity / total_quantity * 100) if total_quantity > 0 else 0

        # Get top 10 products by revenue
        top_products_query = (
            select(
                Product.sku.label("product_code"),
                Product.name.label("product_description"),
                func.sum(SaleItem.quantity * SaleItem.unit_price).label("total_revenue")
            )
            .join(SaleItem, Product.id == SaleItem.product_id)
            .join(Sale, SaleItem.sale_id == Sale.id)
            .where(Sale.sale_date >= (start_date or datetime.utcnow() - timedelta(days=30)))
        )

        if market_id:
            top_products_query = top_products_query.where(Sale.market_id == market_id)

        top_products_query = (
            top_products_query
            .group_by(Product.id, Product.sku, Product.name)
            .order_by(desc("total_revenue"))
            .limit(10)
        )

        top_products_result = await db.execute(top_products_query)
        top_products = [
            TopProduct(
                product_code=row.product_code,
                product_description=row.product_description,
                total_revenue=float(row.total_revenue)
            )
            for row in top_products_result.all()
        ]

        return {
            "transactions": [
                TransactionLineItem(
                    transaction_number=row.transaction_number,
                    transaction_date=row.sale_date,
                    location=row.location,
                    product_code=row.product_code,
                    product_description=row.product_description,
                    quantity=row.quantity,
                    price=float(row.price),
                    cost=float(row.cost),
                    line_revenue=float(row.line_revenue),
                    line_cost=float(row.line_cost),
                    line_margin=float(row.line_margin),
                    margin_percent=float(row.margin_percent),
                    is_return=row.is_return
                ) for row in rows
            ],
            "summary": TransactionSummary(
                total_revenue=float(total_revenue),
                total_cost=float(total_cost),
                total_margin=float(total_margin),
                overall_margin_percent=(float(total_margin / total_revenue * 100) if total_revenue > 0 else 0),
                return_rate=return_rate,
                total_transactions=total_count,
                top_products=top_products
            ),
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        }


class InventoryLossService:
    """Service for Overage/Shrinkage/Spoilage Report"""

    @staticmethod
    async def get_loss_report(
        db: AsyncSession,
        market_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        change_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Inventory Loss Report with risk classification
        """
        # Base query for movements
        query = (
            select(
                InventoryMovement.id,
                Micromarket.name.label("micro_market"),
                InventoryMovement.user_name,
                InventoryMovement.created_at.label("date"),
                Product.name.label("product"),
                Product.sku.label("product_code"),
                Category.name.label("category"),
                InventoryMovement.movement_type.label("change_type"),
                InventoryMovement.quantity,
                InventoryMovement.unit_cost.label("cost"),
                InventoryMovement.total_cost,
                InventoryMovement.unit_price.label("product_price"),
                InventoryMovement.total_price,
                (func.abs(InventoryMovement.quantity) * InventoryMovement.unit_cost).label("loss_value"),
                (func.abs(InventoryMovement.quantity) * InventoryMovement.unit_price).label("retail_impact")
            )
            .join(Product, InventoryMovement.product_id == Product.id)
            .join(Micromarket, InventoryMovement.market_id == Micromarket.id)
            .join(Category, Product.category_id == Category.id)
        )

        # Apply filters
        if market_id:
            query = query.where(InventoryMovement.market_id == market_id)
        if start_date:
            query = query.where(InventoryMovement.created_at >= start_date)
        if end_date:
            query = query.where(InventoryMovement.created_at <= end_date)
        if change_type:
            query = query.where(InventoryMovement.movement_type == change_type)
        else:
            query = query.where(InventoryMovement.movement_type.in_(["shrinkage", "spoilage", "overage"]))

        query = query.order_by(desc(InventoryMovement.created_at))
        result = await db.execute(query)
        rows = result.all()

        # Calculate totals by type
        totals = {"shrinkage": 0.0, "spoilage": 0.0, "overage": 0.0}
        by_location: Dict[str, Dict[str, float]] = {}
        by_category: Dict[str, Dict[str, float]] = {}

        for row in rows:
            loss_val = float(row.loss_value) if row.loss_value else 0
            retail_val = float(row.retail_impact) if row.retail_impact else 0

            if row.change_type in totals:
                totals[row.change_type] += loss_val

            # Aggregate by location
            if row.micro_market not in by_location:
                by_location[row.micro_market] = {"shrinkage": 0.0, "spoilage": 0.0, "overage": 0.0, "total": 0.0}
            by_location[row.micro_market][row.change_type] += loss_val
            by_location[row.micro_market]["total"] += loss_val

            # Aggregate by category
            if row.category not in by_category:
                by_category[row.category] = {"shrinkage": 0.0, "spoilage": 0.0, "overage": 0.0, "total": 0.0}
            by_category[row.category][row.change_type] += loss_val
            by_category[row.category]["total"] += loss_val

        # Get total inventory value for percentage calculation
        inventory_value_query = select(func.sum(Inventory.quantity_on_hand * Product.cost_price)).join(
            Product, Inventory.product_id == Product.id
        )
        if market_id:
            inventory_value_query = inventory_value_query.where(Inventory.market_id == market_id)

        total_inventory_value = await db.scalar(inventory_value_query) or 1

        shrinkage_percent = (totals["shrinkage"] / float(total_inventory_value)) * 100

        # Risk classification
        risk_level = "low"
        if shrinkage_percent > 5:
            risk_level = "critical"
        elif shrinkage_percent > 2:
            risk_level = "high"
        elif shrinkage_percent > 1:
            risk_level = "medium"

        return {
            "items": [
                LossItem(
                    micro_market=row.micro_market,
                    user_name=row.user_name,
                    date=row.date,
                    product=row.product,
                    product_code=row.product_code,
                    category=row.category,
                    change_type=row.change_type,
                    quantity=row.quantity,
                    cost=float(row.cost) if row.cost else 0,
                    total_cost=float(row.total_cost) if row.total_cost else 0,
                    product_price=float(row.product_price) if row.product_price else 0,
                    total_price=float(row.total_price) if row.total_price else 0,
                    loss_value=float(row.loss_value) if row.loss_value else 0,
                    retail_impact=float(row.retail_impact) if row.retail_impact else 0
                ) for row in rows
            ],
            "summary": LossSummary(
                total_shrinkage=totals["shrinkage"],
                total_spoilage=totals["spoilage"],
                total_overage=totals["overage"],
                shrinkage_percent=shrinkage_percent,
                total_loss=totals["shrinkage"] + totals["spoilage"],
                risk_level=risk_level,
                by_location=by_location,
                by_category=by_category
            )
        }


class MarketSalesService:
    """Service for Micro Market Sales Analysis"""

    @staticmethod
    async def get_market_sales(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate Market Sales Analysis with contribution percentages
        """
        # Calculate total revenue first
        total_revenue_query = select(func.sum(Sale.total_amount))
        if start_date:
            total_revenue_query = total_revenue_query.where(Sale.sale_date >= start_date)
        if end_date:
            total_revenue_query = total_revenue_query.where(Sale.sale_date <= end_date)

        total_revenue = await db.scalar(total_revenue_query) or 0

        # Market-level aggregation
        query = (
            select(
                Micromarket.id.label("market_id"),
                Micromarket.name.label("market_name"),
                func.sum(Sale.total_amount).label("revenue"),
                func.count(Sale.id).label("transaction_count"),
                func.avg(Sale.total_amount).label("avg_ticket")
            )
            .join(Sale, Micromarket.id == Sale.market_id)
            .group_by(Micromarket.id, Micromarket.name)
        )

        if start_date:
            query = query.where(Sale.sale_date >= start_date)
        if end_date:
            query = query.where(Sale.sale_date <= end_date)

        query = query.order_by(desc("revenue"))
        result = await db.execute(query)
        rows = result.all()

        markets = []
        highest_revenue = None
        lowest_revenue = None

        for idx, row in enumerate(rows):
            contribution = (float(row.revenue) / float(total_revenue) * 100) if total_revenue > 0 else 0

            market_data = MarketSalesItem(
                market_id=row.market_id,
                market_name=row.market_name,
                revenue=float(row.revenue),
                transaction_count=row.transaction_count,
                avg_ticket=float(row.avg_ticket) if row.avg_ticket else 0,
                contribution_percent=contribution
            )
            markets.append(market_data)

            if idx == 0:
                highest_revenue = {"name": row.market_name, "revenue": float(row.revenue)}
            if idx == len(rows) - 1:
                lowest_revenue = {"name": row.market_name, "revenue": float(row.revenue)}

        # Calculate concentration ratio (top 3 markets % of total)
        top_3_revenue = sum(m.revenue for m in markets[:3])
        concentration_ratio = (top_3_revenue / float(total_revenue) * 100) if total_revenue > 0 else 0

        return {
            "markets": markets,
            "summary": {
                "total_revenue": float(total_revenue),
                "total_markets": len(markets),
                "highest_revenue_market": highest_revenue,
                "lowest_revenue_market": lowest_revenue,
                "concentration_ratio": concentration_ratio,
                "avg_revenue_per_market": float(total_revenue) / len(markets) if markets else 0
            }
        }


class StockHealthService:
    """Service for Stock Analysis Report"""

    @staticmethod
    async def get_stock_health(
        db: AsyncSession,
        market_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate Stock Health Report with risk classification
        """
        # Calculate percentage and classify
        qty_percentage = case(
            (Inventory.max_stock_level > 0,
             (Inventory.quantity_on_hand * 100.0) / Inventory.max_stock_level),
            else_=0
        )

        stock_status = case(
            (qty_percentage < 25, "stockout_risk"),
            ((qty_percentage >= 30) & (qty_percentage <= 70), "healthy"),
            (qty_percentage > 90, "overstock_risk"),
            else_= "warning"
        )

        query = (
            select(
                Micromarket.name.label("market_name"),
                Category.name.label("category"),
                Product.name.label("product_name"),
                Product.sku.label("product_code"),
                Inventory.quantity_on_hand.label("total_quantity"),
                Inventory.max_stock_level.label("max_quantity"),
                qty_percentage.label("qty_percentage"),
                stock_status.label("stock_status"),
                Inventory.reorder_point,
                (Inventory.quantity_on_hand < Inventory.reorder_point).label("below_reorder")
            )
            .join(Product, Inventory.product_id == Product.id)
            .join(Micromarket, Inventory.market_id == Micromarket.id)
            .join(Category, Product.category_id == Category.id)
            .where(Product.is_active == True)
        )

        if market_id:
            query = query.where(Inventory.market_id == market_id)

        result = await db.execute(query)
        rows = result.all()

        # Classify into risk categories
        risk_categories = {
            "stockout_risk": [],
            "healthy": [],
            "overstock_risk": [],
            "warning": []
        }

        below_reorder_items = []

        for row in rows:
            item = StockHealthItem(
                market_name=row.market_name,
                category=row.category,
                product_name=row.product_name,
                product_code=row.product_code,
                total_quantity=row.total_quantity,
                max_quantity=row.max_quantity or 0,
                qty_percentage=float(row.qty_percentage) if row.qty_percentage else 0,
                stock_status=row.stock_status,
                reorder_point=row.reorder_point
            )

            risk_categories[row.stock_status].append(item)

            if row.below_reorder:
                below_reorder_items.append(item)

        total_products = len(rows)

        return {
            "risk_distribution": {
                "stockout_risk": {
                    "count": len(risk_categories["stockout_risk"]),
                    "percentage": (len(risk_categories["stockout_risk"]) / total_products * 100) if total_products > 0 else 0,
                    "items": risk_categories["stockout_risk"][:50]  # Limit items
                },
                "healthy": {
                    "count": len(risk_categories["healthy"]),
                    "percentage": (len(risk_categories["healthy"]) / total_products * 100) if total_products > 0 else 0,
                    "items": risk_categories["healthy"][:50]
                },
                "overstock_risk": {
                    "count": len(risk_categories["overstock_risk"]),
                    "percentage": (len(risk_categories["overstock_risk"]) / total_products * 100) if total_products > 0 else 0,
                    "items": risk_categories["overstock_risk"][:50]
                },
                "warning": {
                    "count": len(risk_categories["warning"]),
                    "percentage": (len(risk_categories["warning"]) / total_products * 100) if total_products > 0 else 0,
                    "items": risk_categories["warning"][:50]
                }
            },
            "below_reorder_threshold": below_reorder_items[:100],
            "summary": {
                "total_products": total_products,
                "critical_stockouts": len(risk_categories["stockout_risk"]),
                "overstock_items": len(risk_categories["overstock_risk"]),
                "healthy_percentage": (len(risk_categories["healthy"]) / total_products * 100) if total_products > 0 else 0
            }
        }
```

```python
# schemas/analytics.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ==================== Shared Base Schemas ====================

class PaginationInfo(BaseModel):
    total: int
    limit: int
    offset: int


class ReportFilter(BaseModel):
    market_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ==================== Product Transaction Report Schemas ====================

class TransactionLineItem(BaseModel):
    transaction_number: str
    transaction_date: datetime
    location: str
    product_code: str
    product_description: str
    quantity: int
    price: float
    cost: float
    line_revenue: float = Field(..., description="Quantity × Price")
    line_cost: float = Field(..., description="Quantity × Cost")
    line_margin: float = Field(..., description="Revenue − Cost")
    margin_percent: float = Field(..., description="(Margin / Revenue) × 100")
    is_return: bool

    class Config:
        from_attributes = True


class TopProduct(BaseModel):
    product_code: str
    product_description: str
    total_revenue: float


class TransactionSummary(BaseModel):
    total_revenue: float
    total_cost: float
    total_margin: float
    overall_margin_percent: float
    return_rate: float = Field(..., description="Percentage of returned items")
    total_transactions: int
    top_products: List[TopProduct]


class ProductTransactionReport(BaseModel):
    report_type: str = "product_transactions"
    generated_at: datetime
    filters: Dict[str, Any]
    data: List[TransactionLineItem]
    summary: TransactionSummary
    pagination: PaginationInfo


# ==================== Inventory Loss Report Schemas ====================

class LossItem(BaseModel):
    micro_market: str
    user_name: str
    date: datetime
    product: str
    product_code: str
    category: str
    change_type: str
    quantity: int
    cost: float
    total_cost: float
    product_price: float
    total_price: float
    loss_value: float = Field(..., description="Quantity × Cost")
    retail_impact: float = Field(..., description="Quantity × ProductPrice")

    class Config:
        from_attributes = True


class LossSummary(BaseModel):
    total_shrinkage: float
    total_spoilage: float
    total_overage: float
    shrinkage_percent: float = Field(..., description="(Total Shrinkage / Total Inventory Value) × 100")
    total_loss: float
    risk_level: str
    by_location: Dict[str, Dict[str, float]]
    by_category: Dict[str, Dict[str, float]]


class InventoryLossReport(BaseModel):
    report_type: str = "inventory_loss"
    generated_at: datetime
    filters: Dict[str, Any]
    items: List[LossItem]
    summary: LossSummary


# ==================== Market Sales Report Schemas ====================

class MarketSalesItem(BaseModel):
    market_id: str
    market_name: str
    revenue: float
    transaction_count: int
    avg_ticket: float
    contribution_percent: float = Field(..., description="Market revenue / Total revenue × 100")

    class Config:
        from_attributes = True


class MarketSalesSummary(BaseModel):
    total_revenue: float
    total_markets: int
    highest_revenue_market: Dict[str, Any]
    lowest_revenue_market: Dict[str, Any]
    concentration_ratio: float = Field(..., description="Top 3 markets % of total revenue")
    avg_revenue_per_market: float


class MarketSalesReport(BaseModel):
    report_type: str = "market_sales"
    generated_at: datetime
    filters: Dict[str, Any]
    markets: List[MarketSalesItem]
    summary: MarketSalesSummary


# ==================== Stock Health Report Schemas ====================

class StockHealthItem(BaseModel):
    market_name: str
    category: str
    product_name: str
    product_code: str
    total_quantity: int
    max_quantity: int
    qty_percentage: float
    stock_status: str
    reorder_point: int

    class Config:
        from_attributes = True


class RiskCategory(BaseModel):
    count: int
    percentage: float
    items: List[StockHealthItem]


class StockHealthDistribution(BaseModel):
    stockout_risk: RiskCategory
    healthy: RiskCategory
    overstock_risk: RiskCategory
    warning: RiskCategory


class StockHealthSummary(BaseModel):
    total_products: int
    critical_stockouts: int
    overstock_items: int
    healthy_percentage: float


class StockHealthReport(BaseModel):
    report_type: str = "stock_health"
    generated_at: datetime
    filters: Dict[str, Any]
    risk_distribution: StockHealthDistribution
    below_reorder_threshold: List[StockHealthItem]
    summary: StockHealthSummary
```

```typescript
// frontend/src/config/chartConfigs.ts

// 1. Product Transaction Report Charts
export const productTransactionCharts = {
  // Margin Analysis - Composed Chart (Bar + Line)
  marginAnalysis: {
    type: "ComposedChart",
    dataKey: "transactions",
    xAxis: { dataKey: "product_code", angle: -45, height: 80 },
    yAxis: [
      { orientation: "left", label: "Amount ($)" },
      { orientation: "right", label: "Margin %", domain: [0, 100] }
    ],
    components: [
      { type: "Bar", dataKey: "line_revenue", name: "Revenue", fill: "#4CAF50", yAxisId: "left" },
      { type: "Bar", dataKey: "line_cost", name: "Cost", fill: "#f44336", yAxisId: "left" },
      { type: "Line", dataKey: "margin_percent", name: "Margin %", stroke: "#2196F3", yAxisId: "right", strokeWidth: 2 }
    ],
    tooltip: {
      formatter: (value: number, name: string) => {
        if (name.includes("%")) return [`${value.toFixed(1)}%`, name];
        return [`$${value.toFixed(2)}`, name];
      }
    }
  },

  // Top Products - Horizontal Bar
  topProducts: {
    type: "BarChart",
    layout: "vertical",
    dataKey: "summary.top_products",
    margin: { left: 100 },
    xAxis: { type: "number", tickFormatter: (val: number) => `$${(val/1000).toFixed(0)}k` },
    yAxis: { dataKey: "product_code", type: "category", width: 100 },
    components: [
      { type: "Bar", dataKey: "total_revenue", fill: "#8884d8", radius: [0, 4, 4, 0] }
    ],
    tooltip: { formatter: (val: number) => `$${val.toLocaleString()}` }
  }
};

// 2. Inventory Loss Report Charts
export const inventoryLossCharts = {
  // Loss by Type - Pie Chart
  lossByType: {
    type: "PieChart",
    data: [
      { name: "Shrinkage", valueKey: "summary.total_shrinkage", color: "#ff4444" },
      { name: "Spoilage", valueKey: "summary.total_spoilage", color: "#ff8800" },
      { name: "Overage", valueKey: "summary.total_overage", color: "#44ff44" }
    ],
    components: [{
      type: "Pie",
      dataKey: "value",
      nameKey: "name",
      cx: "50%",
      cy: "50%",
      innerRadius: 60,
      outerRadius: 100,
      paddingAngle: 5,
      label: ({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(1)}%`
    }],
    tooltip: {
      formatter: (value: number, name: string) => [`$${value.toFixed(2)}`, name]
    }
  },

  // Loss by Location - Stacked Bar
  lossByLocation: {
    type: "BarChart",
    dataKey: "summary.by_location",
    xAxis: { dataKey: "location" },
    yAxis: { tickFormatter: (val: number) => `$${val}` },
    components: [
      { type: "Bar", dataKey: "shrinkage", stackId: "a", fill: "#ff4444", name: "Shrinkage" },
      { type: "Bar", dataKey: "spoilage", stackId: "a", fill: "#ff8800", name: "Spoilage" },
      { type: "Bar", dataKey: "overage", stackId: "a", fill: "#44ff44", name: "Overage" }
    ],
    tooltip: { formatter: (val: number) => `$${val.toFixed(2)}` }
  },

  // Risk Level Indicator
  riskIndicator: {
    type: "GaugeChart",
    data: [{ name: "Risk", value: "summary.risk_level" }],
    colors: {
      low: "#44ff44",
      medium: "#ffcc00",
      high: "#ff8800",
      critical: "#ff4444"
    }
  }
};

// 3. Market Sales Report Charts
export const marketSalesCharts = {
  // Revenue by Market - Bar Chart
  revenueByMarket: {
    type: "BarChart",
    dataKey: "markets",
    xAxis: { dataKey: "market_name", angle: -30, height: 60 },
    yAxis: { tickFormatter: (val: number) => `$${(val/1000).toFixed(0)}k` },
    components: [{
      type: "Bar",
      dataKey: "revenue",
      fill: "#8884d8",
      radius: [4, 4, 0, 0],
      label: { position: "top", formatter: (val: number) => `$${(val/1000).toFixed(1)}k` }
    }],
    tooltip: { formatter: (val: number) => `$${val.toLocaleString()}` }
  },

  // Market Contribution - Pie Chart
  marketContribution: {
    type: "PieChart",
    dataKey: "markets",
    components: [{
      type: "Pie",
      dataKey: "contribution_percent",
      nameKey: "market_name",
      cx: "50%",
      cy: "50%",
      innerRadius: 60,
      outerRadius: 100,
      label: ({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(1)}%`
    }],
    tooltip: {
      formatter: (val: number, name: string, props: any) => [
        `${props.payload.revenue.toLocaleString()} (${(val * 100).toFixed(1)}%)`,
        name
      ]
    }
  },

  // Average Ticket Comparison
  avgTicketComparison: {
    type: "BarChart",
    dataKey: "markets",
    layout: "vertical",
    margin: { left: 100 },
    xAxis: { type: "number", tickFormatter: (val: number) => `$${val}` },
    yAxis: { dataKey: "market_name", type: "category", width: 100 },
    components: [{
      type: "Bar",
      dataKey: "avg_ticket",
      fill: "#82ca9d",
      radius: [0, 4, 4, 0],
      label: { position: "right", formatter: (val: number) => `$${val.toFixed(2)}` }
    }]
  }
};

// 4. Stock Health Report Charts
export const stockHealthCharts = {
  // Risk Distribution - Donut Chart
  riskDistribution: {
    type: "PieChart",
    components: [{
      type: "Pie",
      data: [
        { name: "Stockout Risk", valueKey: "risk_distribution.stockout_risk.count", fill: "#ff4444" },
        { name: "Healthy", valueKey: "risk_distribution.healthy.count", fill: "#44ff44" },
        { name: "Overstock Risk", valueKey: "risk_distribution.overstock_risk.count", fill: "#ff8800" },
        { name: "Warning", valueKey: "risk_distribution.warning.count", fill: "#ffcc00" }
      ],
      dataKey: "value",
      nameKey: "name",
      cx: "50%",
      cy: "50%",
      innerRadius: 80,
      outerRadius: 120,
      paddingAngle: 5,
      label: ({ name, percent, value }: any) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`
    }],
    tooltip: { formatter: (value: number, name: string) => [`${value} products`, name] }
  },

  // Stock Level Distribution - Histogram
  stockLevelHistogram: {
    type: "BarChart",
    dataKey: "risk_distribution.healthy.items",
    xAxis: {
      dataKey: "qty_percentage",
      type: "number",
      domain: [0, 100],
      ticks: [0, 25, 30, 70, 90, 100],
      label: "Stock Level %"
    },
    yAxis: { label: "Product Count" },
    components: [{
      type: "Bar",
      dataKey: "total_quantity",
      fill: "#8884d8"
    }]
  },

  // Critical Stock Alert List
  criticalStockList: {
    type: "table",
    dataKey: "below_reorder_threshold",
    columns: [
      { key: "product_code", title: "SKU" },
      { key: "product_name", title: "Product" },
      { key: "market_name", title: "Location" },
      { key: "total_quantity", title: "Current Qty" },
      { key: "reorder_point", title: "Reorder At" },
      {
        key: "stock_status",
        title: "Status",
        render: (val: string) => ({
          stockout_risk: { color: "red", label: "Critical" },
          healthy: { color: "green", label: "Healthy" },
          overstock_risk: { color: "orange", label: "Overstock" },
          warning: { color: "yellow", label: "Warning" }
        })[val] || { color: "gray", label: "Unknown" }
      }
    ]
  }
};

// Export all chart configurations
export const chartConfigs = {
  productTransaction: productTransactionCharts,
  inventoryLoss: inventoryLossCharts,
  marketSales: marketSalesCharts,
  stockHealth: stockHealthCharts
};

// Helper function to get chart config by report type
export const getChartConfig = (reportType: string, chartName: string) => {
  const config = chartConfigs[reportType as keyof typeof chartConfigs];
  return config?.[chartName as keyof typeof config] || null;
};

// Default colors for charts
export const chartColors = {
  primary: "#8884d8",
  secondary: "#82ca9d",
  success: "#44ff44",
  warning: "#ffcc00",
  danger: "#ff4444",
  info: "#2196F3",
  revenue: "#4CAF50",
  cost: "#f44336",
  margin: "#2196F3"
};

// Responsive chart container config
export const responsiveContainerConfig = {
  width: "100%",
  height: 400,
  minWidth: 300,
  minHeight: 300
};

// Animation config for charts
export const animationConfig = {
  isAnimationActive: true,
  animationBegin: 0,
  animationDuration: 1000,
  animationEasing: "ease-out"
};

// Tooltip style config
export const tooltipStyleConfig = {
  contentStyle: {
    backgroundColor: "#fff",
    border: "1px solid #ccc",
    borderRadius: "4px",
    padding: "10px"
  },
  labelStyle: {
    color: "#333",
    fontWeight: "bold"
  }
};

// Legend config
export const legendConfig = {
  verticalAlign: "bottom",
  height: 36,
  iconType: "circle"
};

// Grid config for cartesian charts
export const gridConfig = {
  strokeDasharray: "3 3",
  vertical: false,
  horizontal: true
};

// Label formatter helpers
export const formatters = {
  currency: (value: number) => `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
  currencyK: (value: number) => `$${(value / 1000).toFixed(1)}k`,
  percent: (value: number) => `${(value * 100).toFixed(1)}%`,
  number: (value: number) => value.toLocaleString(),
  compactNumber: (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
    return value.toString();
  }
};

// Date range presets for filters
export const dateRangePresets = {
  today: { label: "Today", days: 0 },
  yesterday: { label: "Yesterday", days: 1 },
  last7Days: { label: "Last 7 Days", days: 7 },
  last30Days: { label: "Last 30 Days", days: 30 },
  thisMonth: { label: "This Month", days: 30 },
  lastMonth: { label: "Last Month", days: 60 },
  thisQuarter: { label: "This Quarter", days: 90 },
  ytd: { label: "Year to Date", days: 365 }
};

// Table column definitions for reports
export const tableColumns = {
  productTransactions: [
    { key: "transaction_number", title: "Transaction", width: 120 },
    { key: "transaction_date", title: "Date", width: 100, format: "date" },
    { key: "location", title: "Location", width: 120 },
    { key: "product_code", title: "SKU", width: 100 },
    { key: "quantity", title: "Qty", width: 80, align: "right" },
    { key: "line_revenue", title: "Revenue", width: 100, format: "currency", align: "right" },
    { key: "line_margin", title: "Margin", width: 100, format: "currency", align: "right" },
    { key: "margin_percent", title: "Margin %", width: 90, format: "percent", align: "right" }
  ],
  inventoryLoss: [
    { key: "date", title: "Date", width: 100, format: "date" },
    { key: "micro_market", title: "Location", width: 120 },
    { key: "product_code", title: "SKU", width: 100 },
    { key: "product", title: "Product", width: 150 },
    { key: "change_type", title: "Type", width: 100, format: "badge" },
    { key: "quantity", title: "Qty", width: 80, align: "right" },
    { key: "loss_value", title: "Loss Value", width: 100, format: "currency", align: "right" },
    { key: "retail_impact", title: "Retail Impact", width: 110, format: "currency", align: "right" }
  ],
  marketSales: [
    { key: "market_name", title: "Market", width: 150 },
    { key: "revenue", title: "Revenue", width: 120, format: "currency", align: "right" },
    { key: "contribution_percent", title: "Contribution", width: 110, format: "percent", align: "right" },
    { key: "transaction_count", title: "Transactions", width: 110, align: "right" },
    { key: "avg_ticket", title: "Avg Ticket", width: 100, format: "currency", align: "right" }
  ],
  stockHealth: [
    { key: "product_code", title: "SKU", width: 100 },
    { key: "product_name", title: "Product", width: 150 },
    { key: "market_name", title: "Location", width: 120 },
    { key: "category", title: "Category", width: 100 },
    { key: "total_quantity", title: "Current Qty", width: 100, align: "right" },
    { key: "max_quantity", title: "Max Qty", width: 100, align: "right" },
    { key: "qty_percentage", title: "Stock %", width: 90, format: "percent", align: "right" },
    { key: "stock_status", title: "Status", width: 100, format: "badge" },
    { key: "reorder_point", title: "Reorder At", width: 100, align: "right" }
  ]
};

// Export all configurations
export default {
  chartConfigs,
  getChartConfig,
  chartColors,
  formatters,
  responsiveContainerConfig,
  animationConfig,
  tooltipStyleConfig,
  legendConfig,
  gridConfig,
  dateRangePresets,
  tableColumns
};
```

```sql
-- migrations/001_initial_schema.sql
-- Initial schema for Micromarket Analytics Platform
-- Optimized for PostgreSQL 16

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- CORE TABLES
-- ============================================

-- Operators (Users)
CREATE TABLE operators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'viewer',
    phone VARCHAR(50),
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences TEXT,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Categories
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100),
    description TEXT,
    parent_id UUID REFERENCES categories(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Micromarkets
CREATE TABLE micromarkets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operator_id UUID NOT NULL REFERENCES operators(id),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(100) UNIQUE NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    timezone VARCHAR(50) DEFAULT 'UTC',
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku VARCHAR(100) UNIQUE NOT NULL,
    barcode VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id UUID REFERENCES categories(id),
    unit_price NUMERIC(10, 2) DEFAULT 0,
    cost_price NUMERIC(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES products(id),
    market_id UUID NOT NULL REFERENCES micromarkets(id),
    quantity_on_hand INTEGER DEFAULT 0,
    quantity_reserved INTEGER DEFAULT 0,
    quantity_available INTEGER DEFAULT 0,
    reorder_point INTEGER DEFAULT 0,
    max_stock_level INTEGER DEFAULT 0,
    last_counted_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'in_stock',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, market_id)
);

-- Sales
CREATE TABLE sales (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    market_id UUID NOT NULL REFERENCES micromarkets(id),
    sale_date TIMESTAMP NOT NULL,
    transaction_number VARCHAR(100) UNIQUE NOT NULL,
    channel VARCHAR(50) DEFAULT 'pos',
    total_amount NUMERIC(10, 2) DEFAULT 0,
    item_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sale Items
CREATE TABLE sale_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sale_id UUID NOT NULL REFERENCES sales(id),
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    unit_cost NUMERIC(10, 2) NOT NULL,
    total_price NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inventory Movements (for loss tracking)
CREATE TABLE inventory_movements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    market_id UUID NOT NULL REFERENCES micromarkets(id),
    product_id UUID NOT NULL REFERENCES products(id),
    user_name VARCHAR(100),
    movement_type VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_cost NUMERIC(10, 2),
    total_cost NUMERIC(10, 2),
    unit_price NUMERIC(10, 2),
    total_price NUMERIC(10, 2),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    operator_id UUID NOT NULL REFERENCES operators(id),
    market_id UUID REFERENCES micromarkets(id),
    title VARCHAR(255),
    message_count INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Product indexes
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_barcode ON products(barcode);

-- Sale indexes
CREATE INDEX idx_sales_market ON sales(market_id);
CREATE INDEX idx_sales_date ON sales(sale_date DESC);
CREATE INDEX idx_sales_transaction ON sales(transaction_number);

-- Composite indexes for common query patterns
CREATE INDEX idx_sales_market_date ON sales(market_id, sale_date DESC);
CREATE INDEX idx_sale_items_sale ON sale_items(sale_id);
CREATE INDEX idx_sale_items_product ON sale_items(product_id);

-- Inventory indexes
CREATE INDEX idx_inventory_market ON inventory(market_id);
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_inventory_status ON inventory(status);

-- Partial index for low stock (performance optimization)
CREATE INDEX idx_low_stock ON inventory(quantity_available)
    WHERE quantity_available < reorder_point;

-- Movement indexes
CREATE INDEX idx_movements_type ON inventory_movements(movement_type);
CREATE INDEX idx_movements_market ON inventory_movements(market_id);
CREATE INDEX idx_movements_date ON inventory_movements(created_at DESC);

-- ============================================
-- VIEWS FOR ANALYTICS
-- ============================================

-- Daily sales summary view
CREATE VIEW vw_daily_sales AS
SELECT
    market_id,
    DATE(sale_date) as sale_day,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_ticket
FROM sales
GROUP BY market_id, DATE(sale_date);

-- Product performance view
CREATE VIEW vw_product_performance AS
SELECT
    p.id as product_id,
    p.sku,
    p.name,
    SUM(si.quantity) as total_quantity_sold,
    SUM(si.total_price) as total_revenue,
    SUM(si.quantity * si.unit_cost) as total_cost,
    SUM(si.total_price) - SUM(si.quantity * si.unit_cost) as total_margin
FROM products p
JOIN sale_items si ON p.id = si.product_id
GROUP BY p.id, p.sku, p.name;
```

```yaml
# docker-compose.yml
version: "3.8"

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: micromarket
      POSTGRES_PASSWORD: ${DB_PASSWORD:-secure_password}
      POSTGRES_DB: micromarket
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/migrations:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U micromarket"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  api:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://micromarket:${DB_PASSWORD:-secure_password}@postgres:5432/micromarket
      REDIS_HOST: redis
      REDIS_PORT: 6379
      SECRET_KEY: ${SECRET_KEY:-your-secret-key-change-in-production}
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend/app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    restart: unless-stopped

  # Celery Worker
  worker:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://micromarket:${DB_PASSWORD:-secure_password}@postgres:5432/micromarket
      REDIS_HOST: redis
      REDIS_PORT: 6379
    depends_on:
      - postgres
      - redis
    command: celery -A app.tasks worker --loglevel=info --concurrency=4
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
