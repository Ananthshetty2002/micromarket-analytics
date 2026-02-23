requirement\backend\app\api\endpoints\analytics.py
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
