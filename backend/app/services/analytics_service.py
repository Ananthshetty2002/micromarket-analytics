# services/analytics_service.py
from sqlalchemy import select, func, case, desc, literal_column, CTE
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from app.models import Sale, SaleItem, Product, Inventory, InventoryMovement, Micromarket
from app.schemas.analytics import (
    ProductTransactionReport, TransactionLineItem, TransactionSummary,
    InventoryLossReport, LossItem, LossSummary,
    MarketSalesReport, MarketSalesItem,
    StockHealthReport, StockHealthItem, RiskCategory
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
            {
                "product_code": row.product_code,
                "product_description": row.product_description,
                "total_revenue": float(row.total_revenue)
            }
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
                (abs(InventoryMovement.quantity) * InventoryMovement.unit_cost).label("loss_value"),
                (abs(InventoryMovement.quantity) * InventoryMovement.unit_price).label("retail_impact")
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
        totals = {"shrinkage": 0, "spoilage": 0, "overage": 0}
        by_location = {}
        by_category = {}

        for row in rows:
            loss_val = float(row.loss_value) if row.loss_value else 0
            retail_val = float(row.retail_impact) if row.retail_impact else 0

            if row.change_type in totals:
                totals[row.change_type] += loss_val

            # Aggregate by location
            if row.micro_market not in by_location:
                by_location[row.micro_market] = {"shrinkage": 0, "spoilage": 0, "overage": 0, "total": 0}
            by_location[row.micro_market][row.change_type] += loss_val
            by_location[row.micro_market]["total"] += loss_val

            # Aggregate by category
            if row.category not in by_category:
                by_category[row.category] = {"shrinkage": 0, "spoilage": 0, "overage": 0, "total": 0}
            by_category[row.category][row.change_type] += loss_val
            by_category[row.category]["total"] += loss_val

        # Get total inventory value for percentage calculation
        inventory_value_query = select(func.sum(Inventory.quantity_on_hand * Product.unit_cost)).join(
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
