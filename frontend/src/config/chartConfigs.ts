requirement\frontend\src\config\chartConfigs.ts

// Chart configurations for Micromarket Analytics Platform
// Optimized for Recharts with TanStack Query integration

// ============================================
// 1. Product Transaction Report Charts
// ============================================

export const productTransactionCharts = {
  // Margin Analysis - Composed Chart (Bar + Line)
  marginAnalysis: {
    type: "ComposedChart",
    dataKey: "transactions",
    xAxis: { dataKey: "product_code", angle: -45, height: 80 },
    yAxis: [
      { orientation: "left", label: "Amount ($)", yAxisId: "left" },
      { orientation: "right", label: "Margin %", domain: [0, 100], yAxisId: "right" }
    ],
    components: [
      { type: "Bar", dataKey: "line_revenue", name: "Revenue", fill: "#4CAF50", yAxisId: "left" },
      { type: "Bar", dataKey: "line_cost", name: "Cost", fill: "#f44336", yAxisId: "left" },
      { type: "Line", dataKey: "margin_percent", name: "Margin %", stroke: "#2196F3", yAxisId: "right", strokeWidth: 2, dot: false }
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
    margin: { left: 100, right: 30, top: 20, bottom: 20 },
    xAxis: { type: "number", tickFormatter: (val: number) => `$${(val/1000).toFixed(0)}k` },
    yAxis: { dataKey: "product_code", type: "category", width: 100 },
    components: [
      { type: "Bar", dataKey: "total_revenue", fill: "#8884d8", radius: [0, 4, 4, 0], name: "Revenue" }
    ],
    tooltip: { formatter: (val: number) => `$${val.toLocaleString()}` }
  }
};

// ============================================
// 2. Inventory Loss Report Charts
// ============================================

export const inventoryLossCharts = {
  // Loss by Type - Pie Chart
  lossByType: {
    type: "PieChart",
    components: [{
      type: "Pie",
      data: [
        { name: "Shrinkage", valueKey: "summary.total_shrinkage", fill: "#ff4444" },
        { name: "Spoilage", valueKey: "summary.total_spoilage", fill: "#ff8800" },
        { name: "Overage", valueKey: "summary.total_overage", fill: "#44ff44" }
      ],
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

  // Loss by Category - Horizontal Bar
  lossByCategory: {
    type: "BarChart",
    layout: "vertical",
    dataKey: "summary.by_category",
    margin: { left: 100 },
    xAxis: { type: "number", tickFormatter: (val: number) => `$${val}` },
    yAxis: { dataKey: "category", type: "category", width: 100 },
    components: [
      { type: "Bar", dataKey: "total", fill: "#ff5722", name: "Total Loss", radius: [0, 4, 4, 0] }
    ]
  }
};

// ============================================
// 3. Market Sales Report Charts
// ============================================

export const marketSalesCharts = {
  // Revenue by Market - Bar Chart
  revenueByMarket: {
    type: "BarChart",
    dataKey: "markets",
    xAxis: { dataKey: "market_name", angle: -30, height: 60, tickMargin: 10 },
    yAxis: { tickFormatter: (val: number) => `$${(val/1000).toFixed(0)}k` },
    components: [{
      type: "Bar",
      dataKey: "revenue",
      fill: "#8884d8",
      radius: [4, 4, 0, 0],
      label: { position: "top", formatter: (val: number) => `$${(val/1000).toFixed(1)}k`, fontSize: 12 }
    }],
    tooltip: { formatter: (val: number) => `$${val.toLocaleString()}` }
  },

  // Market Contribution - Pie Chart
  marketContribution: {
    type: "PieChart",
    components: [{
      type: "Pie",
      dataKey: "contribution_percent",
      nameKey: "market_name",
      cx: "50%",
      cy: "50%",
      innerRadius: 60,
      outerRadius: 100,
      label: ({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(1)}%`,
      labelLine: true
    }],
    tooltip: {
      formatter: (val: number, name: string, props: any) => [
        `${props?.payload?.revenue?.toLocaleString()} (${(val * 100).toFixed(1)}%)`,
        name
      ]
    }
  },

  // Average Ticket Comparison
  avgTicketComparison: {
    type: "BarChart",
    dataKey: "markets",
    layout: "vertical",
    margin: { left: 100, right: 30 },
    xAxis: { type: "number", tickFormatter: (val: number) => `$${val}` },
    yAxis: { dataKey: "market_name", type: "category", width: 100 },
    components: [{
      type: "Bar",
      dataKey: "avg_ticket",
      fill: "#82ca9d",
      radius: [0, 4, 4, 0],
      label: { position: "right", formatter: (val: number) => `$${val.toFixed(2)}`, fontSize: 11 }
    }]
  },

  // Transaction Count
  transactionCount: {
    type: "BarChart",
    dataKey: "markets",
    xAxis: { dataKey: "market_name", angle: -30, height: 60 },
    yAxis: { allowDecimals: false },
    components: [{
      type: "Bar",
      dataKey: "transaction_count",
      fill: "#ffc658",
      radius: [4, 4, 0, 0]
    }]
  }
};

// ============================================
// 4. Stock Health Report Charts
// ============================================

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

  // Risk Percentage Bar
  riskPercentageBar: {
    type: "BarChart",
    data: [
      { name: "Stockout Risk", valueKey: "risk_distribution.stockout_risk.percentage", fill: "#ff4444" },
      { name: "Healthy", valueKey: "risk_distribution.healthy.percentage", fill: "#44ff44" },
      { name: "Overstock Risk", valueKey: "risk_distribution.overstock_risk.percentage", fill: "#ff8800" },
      { name: "Warning", valueKey: "risk_distribution.warning.percentage", fill: "#ffcc00" }
    ],
    xAxis: { dataKey: "name" },
    yAxis: { domain: [0, 100], tickFormatter: (val: number) => `${val}%` },
    components: [{
      type: "Bar",
      dataKey: "value",
      radius: [4, 4, 0, 0],
      label: { position: "top", formatter: (val: number) => `${val.toFixed(1)}%` }
    }]
  }
};

// ============================================
// Export All Chart Configurations
// ============================================

export const chartConfigs = {
  productTransaction: productTransactionCharts,
  inventoryLoss: inventoryLossCharts,
  marketSales: marketSalesCharts,
  stockHealth: stockHealthCharts
};

// Helper function to get chart config by report type
export const getChartConfig = (reportType: string, chartName: string): any => {
  const config = chartConfigs[reportType as keyof typeof chartConfigs];
  return config?.[chartName as keyof typeof config] || null;
};

// ============================================
// Utility Configurations
// ============================================

export const chartColors = {
  primary: "#8884d8",
  secondary: "#82ca9d",
  tertiary: "#ffc658",
  success: "#44ff44",
  warning: "#ffcc00",
  danger: "#ff4444",
  info: "#2196F3",
  revenue: "#4CAF50",
  cost: "#f44336",
  margin: "#2196F3",
  stockout: "#ff4444",
  healthy: "#44ff44",
  overstock: "#ff8800"
};

export const responsiveContainerConfig = {
  width: "100%",
  height: 400,
  minWidth: 300,
  minHeight: 300
};

export const animationConfig = {
  isAnimationActive: true,
  animationBegin: 0,
  animationDuration: 800,
  animationEasing: "ease-out"
};

export const tooltipStyleConfig = {
  contentStyle: {
    backgroundColor: "rgba(255, 255, 255, 0.95)",
    border: "1px solid #ccc",
    borderRadius: "8px",
    padding: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)"
  },
  labelStyle: {
    color: "#333",
    fontWeight: 600,
    fontSize: "14px"
  }
};

export const legendConfig = {
  verticalAlign: "bottom" as const,
  height: 36,
  iconType: "circle" as const,
  wrapperStyle: { paddingTop: "20px" }
};

export const gridConfig = {
  strokeDasharray: "3 3",
  vertical: false,
  horizontal: true,
  stroke: "#e0e0e0"
};

// ============================================
// Formatters
// ============================================

export const formatters = {
  currency: (value: number): string =>
    `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,

  currencyK: (value: number): string =>
    `$${(value / 1000).toFixed(1)}k`,

  currencyM: (value: number): string =>
    `$${(value / 1000000).toFixed(2)}M`,

  percent: (value: number): string =>
    `${(value).toFixed(1)}%`,

  percentRaw: (value: number): string =>
    `${(value * 100).toFixed(1)}%`,

  number: (value: number): string =>
    value.toLocaleString(),

  compactNumber: (value: number): string => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
    return value.toString();
  },

  date: (value: string | Date): string => {
    const date = typeof value === "string" ? new Date(value) : value;
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric"
    });
  },

  datetime: (value: string | Date): string => {
    const date = typeof value === "string" ? new Date(value) : value;
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  }
};

// ============================================
// Date Range Presets
// ============================================

export const dateRangePresets = {
  today: { label: "Today", days: 0 },
  yesterday: { label: "Yesterday", days: 1 },
  last7Days: { label: "Last 7 Days", days: 7 },
  last30Days: { label: "Last 30 Days", days: 30 },
  thisMonth: { label: "This Month", days: 30 },
  lastMonth: { label: "Last Month", days: 60 },
  thisQuarter: { label: "This Quarter", days: 90 },
  ytd: { label: "Year to Date", days: 365 },
  all: { label: "All Time", days: 3650 }
};

// ============================================
// Table Column Definitions
// ============================================

export const tableColumns = {
  productTransactions: [
    { key: "transaction_number", title: "Transaction", width: 120 },
    { key: "transaction_date", title: "Date", width: 100, format: "date" },
    { key: "location", title: "Location", width: 120 },
    { key: "product_code", title: "SKU", width: 100 },
    { key: "quantity", title: "Qty", width: 80, align: "right" as const },
    { key: "line_revenue", title: "Revenue", width: 100, format: "currency", align: "right" as const },
    { key: "line_margin", title: "Margin", width: 100, format: "currency", align: "right" as const },
    { key: "margin_percent", title: "Margin %", width: 90, format: "percent", align: "right" as const }
  ],

  inventoryLoss: [
    { key: "date", title: "Date", width: 100, format: "date" },
    { key: "micro_market", title: "Location", width: 120 },
    { key: "product_code", title: "SKU", width: 100 },
    { key: "product", title: "Product", width: 150 },
    { key: "change_type", title: "Type", width: 100, format: "badge" },
    { key: "quantity", title: "Qty", width: 80, align: "right" as const },
    { key: "loss_value", title: "Loss Value", width: 100, format: "currency", align: "right" as const },
    { key: "retail_impact", title: "Retail Impact", width: 110, format: "currency", align: "right" as const }
  ],

  marketSales: [
    { key: "market_name", title: "Market", width: 150 },
    { key: "revenue", title: "Revenue", width: 120, format: "currency", align: "right" as const },
    { key: "contribution_percent", title: "Contribution", width: 110, format: "percent", align: "right" as const },
    { key: "transaction_count", title: "Transactions", width: 110, align: "right" as const },
    { key: "avg_ticket", title: "Avg Ticket", width: 100, format: "currency", align: "right" as const }
  ],

  stockHealth: [
    { key: "product_code", title: "SKU", width: 100 },
    { key: "product_name", title: "Product", width: 150 },
    { key: "market_name", title: "Location", width: 120 },
    { key: "category", title: "Category", width: 100 },
    { key: "total_quantity", title: "Current Qty", width: 100, align: "right" as const },
    { key: "max_quantity", title: "Max Qty", width: 100, align: "right" as const },
    { key: "qty_percentage", title: "Stock %", width: 90, format: "percent", align: "right" as const },
    { key: "stock_status", title: "Status", width: 100, format: "badge" },
    { key: "reorder_point", title: "Reorder At", width: 100, align: "right" as const }
  ]
};

// ============================================
// Risk Level Helpers
// ============================================

export const riskLevelConfig = {
  critical: { color: "#ff4444", bgColor: "#ffebee", label: "Critical", icon: "alert-circle" },
  high: { color: "#ff8800", bgColor: "#fff3e0", label: "High", icon: "alert-triangle" },
  medium: { color: "#ffcc00", bgColor: "#fffde7", label: "Medium", icon: "alert" },
  low: { color: "#44ff44", bgColor: "#e8f5e9", label: "Low", icon: "check-circle" },
  healthy: { color: "#44ff44", bgColor: "#e8f5e9", label: "Healthy", icon: "check-circle" },
  warning: { color: "#ffcc00", bgColor: "#fffde7", label: "Warning", icon: "alert" },
  stockout_risk: { color: "#ff4444", bgColor: "#ffebee", label: "Stockout Risk", icon: "alert-circle" },
  overstock_risk: { color: "#ff8800", bgColor: "#fff3e0", label: "Overstock Risk", icon: "alert-triangle" }
};

export const getRiskConfig = (level: string) => {
  return riskLevelConfig[level as keyof typeof riskLevelConfig] || riskLevelConfig.low;
};

// ============================================
// Default Export
// ============================================

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
  tableColumns,
  riskLevelConfig,
  getRiskConfig
};
