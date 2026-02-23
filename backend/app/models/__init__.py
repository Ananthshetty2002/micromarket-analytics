"""
SQLAlchemy models for Micromarket Analytics Platform
"""

from sqlalchemy import (
    Column, String, Numeric, DateTime, ForeignKey, Integer,
    Boolean, Text, func, case, select
)
from sqlalchemy.orm import relationship, declarative_base, selectinload
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

**Recharts Frontend Configurations:**

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
    type: "GaugeChart",  // Custom or use Pie with single value
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
    dataKey: "risk_distribution.healthy.items",  // Sample from all categories
    xAxis: {
      dataKey: "qty_percentage",
      type: "number",
      domain: [0, 100],
+      ticks: [0, 25, 30, 70, 90, 100],
+      label: "Stock Level %"
+    },
+    yAxis: { label: "Product Count" },
+    components: [{
+      type: "Bar",
+      dataKey: "total_quantity",
+      fill: "#8884d8"
+    }]
+  },
+
+  // Critical Stock Alert List
+  criticalStockList: {
+    type: "table",  // Use Recharts Cell components or standard table
+    dataKey: "below_reorder_threshold",
+    columns: [
+      { key: "product_code", title: "SKU" },
+      { key: "product_name", title: "Product" },
+      { key: "market_name", title: "Location" },
+      { key: "total_quantity", title: "Current Qty" },
+      { key: "reorder_point", title: "Reorder At" },
+      {
+        key: "stock_status",
+        title: "Status",
+        render: (val: string) => ({
+          stockout_risk: { color: "red", label: "Critical" },
+          healthy: { color: "green", label: "Healthy" },
+          overstock_risk: { color: "orange", label: "Overstock" },
+          warning: { color: "yellow", label: "Warning" }
+        })[val] || { color: "gray", label: "Unknown" }
+      }
+    ]
+  }
+};
+
+// Export all chart configurations
+export const chartConfigs = {
+  productTransaction: productTransactionCharts,
+  inventoryLoss: inventoryLossCharts,
+  marketSales: marketSalesCharts,
+  stockHealth: stockHealthCharts
+};
+
+// Helper function to get chart config by report type
+export const getChartConfig = (reportType: string, chartName: string) => {
+  const config = chartConfigs[reportType as keyof typeof chartConfigs];
+  return config?.[chartName as keyof typeof config] || null;
+};
+
+// Default colors for charts
+export const chartColors = {
+  primary: "#8884d8",
+  secondary: "#82ca9d",
+  success: "#44ff44",
+  warning: "#ffcc00",
+  danger: "#ff4444",
+  info: "#2196F3",
+  revenue: "#4CAF50",
+  cost: "#f44336",
+  margin: "#2196F3"
+};
+
+// Responsive chart container config
+export const responsiveContainerConfig = {
+  width: "100%",
+  height: 400,
+  minWidth: 300,
+  minHeight: 300
+};
+
+// Animation config for charts
+export const animationConfig = {
+  isAnimationActive: true,
+  animationBegin: 0,
+  animationDuration: 1000,
+  animationEasing: "ease-out"
+};
+
+// Tooltip style config
+export const tooltipStyleConfig = {
+  contentStyle: {
+    backgroundColor: "#fff",
+    border: "1px solid #ccc",
+    borderRadius: "4px",
+    padding: "10px"
+  },
+  labelStyle: {
+    color: "#333",
+    fontWeight: "bold"
+  }
+};
+
+// Legend config
+export const legendConfig = {
+  verticalAlign: "bottom",
+  height: 36,
+  iconType: "circle"
+};
+
+// Grid config for cartesian charts
+export const gridConfig = {
+  strokeDasharray: "3 3",
+  vertical: false,
+  horizontal: true
+};
+
+// Label formatter helpers
+export const formatters = {
+  currency: (value: number) => `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
+  currencyK: (value: number) => `$${(value / 1000).toFixed(1)}k`,
+  percent: (value: number) => `${(value * 100).toFixed(1)}%`,
+  number: (value: number) => value.toLocaleString(),
+  compactNumber: (value: number) => {
+    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
+    if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
+    return value.toString();
+  }
+};
+
+// Date range presets for filters
+export const dateRangePresets = {
+  today: { label: "Today", days: 0 },
+  yesterday: { label: "Yesterday", days: 1 },
+  last7Days: { label: "Last 7 Days", days: 7 },
+  last30Days: { label: "Last 30 Days", days: 30 },
+  thisMonth: { label: "This Month", days: 30 },
+  lastMonth: { label: "Last Month", days: 60 },
+  thisQuarter: { label: "This Quarter", days: 90 },
+  ytd: { label: "Year to Date", days: 365 }
+};
+
+// Table column definitions for reports
+export const tableColumns = {
+  productTransactions: [
+    { key: "transaction_number", title: "Transaction", width: 120 },
+    { key: "transaction_date", title: "Date", width: 100, format: "date" },
+    { key: "location", title: "Location", width: 120 },
+    { key: "product_code", title: "SKU", width: 100 },
+    { key: "quantity", title: "Qty", width: 80, align: "right" },
+    { key: "line_revenue", title: "Revenue", width: 100, format: "currency", align: "right" },
+    { key: "line_margin", title: "Margin", width: 100, format: "currency", align: "right" },
+    { key: "margin_percent", title: "Margin %", width: 90, format: "percent", align: "right" }
+  ],
+  inventoryLoss: [
+    { key: "date", title: "Date", width: 100, format: "date" },
+    { key: "micro_market", title: "Location", width: 120 },
+    { key: "product_code", title: "SKU", width: 100 },
+    { key: "product", title: "Product", width: 150 },
+    { key: "change_type", title: "Type", width: 100, format: "badge" },
+    { key: "quantity", title: "Qty", width: 80, align: "right" },
+    { key: "loss_value", title: "Loss Value", width: 100, format: "currency", align: "right" },
+    { key: "retail_impact", title: "Retail Impact", width: 110, format: "currency", align: "right" }
+  ],
+  marketSales: [
+    { key: "market_name", title: "Market", width: 150 },
+    { key: "revenue", title: "Revenue", width: 120, format: "currency", align: "right" },
+    { key: "contribution_percent", title: "Contribution", width: 110, format: "percent", align: "right" },
+    { key: "transaction_count", title: "Transactions", width: 110, align: "right" },
+    { key: "avg_ticket", title: "Avg Ticket", width: 100, format: "currency", align: "right" }
+  ],
+  stockHealth: [
+    { key: "product_code", title: "SKU", width: 100 },
+    { key: "product_name", title: "Product", width: 150 },
+    { key: "market_name", title: "Location", width: 120 },
+    { key: "category", title: "Category", width: 100 },
+    { key: "total_quantity", title: "Current Qty", width: 100, align: "right" },
+    { key: "max_quantity", title: "Max Qty", width: 100, align: "right" },
+    { key: "qty_percentage", title: "Stock %", width: 90, format: "percent", align: "right" },
+    { key: "stock_status", title: "Status", width: 100, format: "badge" },
+    { key: "reorder_point", title: "Reorder At", width: 100, align: "right" }
+  ]
+};
+
+// Export all configurations
+export default {
+  chartConfigs,
+  getChartConfig,
+  chartColors,
+  formatters,
+  responsiveContainerConfig,
+  animationConfig,
+  tooltipStyleConfig,
+  legendConfig,
+  gridConfig,
+  dateRangePresets,
+  tableColumns
+};
```

**Key Features of This Implementation:**

1. **Async SQLAlchemy 2.0** - All queries use async/await pattern with proper session management
2. **Calculated Fields at DB Level** - Line revenue, cost, margin calculated in SQL for performance
3. **Strategic Indexing** - Composite indexes on (market_id, date), foreign keys, and partial indexes for low stock
4. **Redis Caching** - 2-10 minute TTL per report type based on data volatility
5. **Clean Architecture** - Service layer separation with Pydantic schemas for type safety
6. **Optimized for PostgreSQL 16** - Uses CTEs, window functions, and efficient aggregations
7. **Recharts Ready** - Complete frontend configuration with formatters, colors, and responsive containers
8. **Error Handling** - Comprehensive try/catch with structured logging and HTTP exceptions
9. **Pagination** - All list endpoints support limit/offset with total count
10. **Docker Compose Ready** - Single-server deployment with Nginx, FastAPI, PostgreSQL, Redis
