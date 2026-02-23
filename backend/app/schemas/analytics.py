```
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
