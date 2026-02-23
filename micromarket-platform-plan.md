# Micromarket Business Intelligence Platform - Complete Planning Document

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Odoo 18.0 Compatibility](#odoo-180-compatibility)
4. [Operator-Friendly Interface Design](#operator-friendly-interface-design)
5. [Database Schema](#database-schema)
6. [Data Flow Diagrams](#data-flow-diagrams)
7. [Technology Stack](#technology-stack)
8. [Implementation Phases](#implementation-phases)
9. [Success Criteria](#success-criteria)

---

## Executive Summary

This platform provides business intelligence for micromarket operators, integrating with Odoo 18.0 Inventory Management System. The platform features a dashboard, AI chat bot (MCP-based), analytics with easy section switching, reporting, and data input capabilities. It supports both manual file uploads (initial phase) and direct API integration (future phase).

**Key Features:**
- Odoo 18.0 report compatibility
- Four main analysis sections with sub-analysis switching
- MCP-based AI chat bot for natural language queries
- File upload and API integration capabilities
- Operator-friendly, mobile-responsive interface

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER                                 │
├─────────────────┬─────────────────┬─────────────────┬─────────────────────────┤
│   Dashboard     │   AI Chat Bot   │   Analytics     │   Reporting & Data    │
│   (Visual KPIs) │   (MCP Server)  │   (Switchable   │   Input               │
│                 │                 │   Sections)     │   (Upload/API)        │
└────────┬────────┴────────┬────────┴────────┬────────┴───────────┬───────────┘
         │                 │                 │                    │
         └─────────────────┴─────────────────┴────────────────────┘
                                    │
                           ┌────────▼────────┐
                           │   API GATEWAY    │
                           │  (Auth/Rate Limit)│
                           └────────┬────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────────────┐
│                         BUSINESS LOGIC LAYER                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │  Analytics   │ │   Reporting  │ │  Data Input  │ │  Scheduler Service   │  │
│  │   Engine     │ │   Generator  │ │  Validator   │ │  (for API sync)      │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────────────┐ │
│  │                     AI/MCP Server Integration Layer                       │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐     │ │
│  │  │  MCP Server  │ │  LLM Engine  │ │  Context     │ │  Tool        │     │ │
│  │  │  (Stdio/SSE) │ │  (Claude/etc)│ │  Manager     │ │  Registry    │     │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘     │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────┬───────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────────────┐
│                          DATA LAYER                                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │  PostgreSQL  │ │    Redis     │ │  File Store  │ │   Vector DB          │  │
│  │  (Primary DB)│ │   (Cache)    │ │  (Reports)   │ │ (AI Embeddings)      │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────┘
                                    │
                           ┌────────▼────────┐
                           │  EXTERNAL APIs  │
                           │  (Odoo 18.0 ERP)│
                           └─────────────────┘
```

---

## Odoo 18.0 Compatibility

### Supported Report Types

| Report Category | Odoo 18.0 Report Name | File Format | Data Contents |
|-----------------|----------------------|-------------|---------------|
| **Sales** | Sales Analysis Report | XLSX, CSV | Order lines, products, quantities, prices, dates, salesperson |
| **Inventory** | Stock Inventory Report | XLSX, CSV | Product quantities, locations, lot numbers, expiry dates |
| **Inventory** | Inventory Valuation | XLSX, PDF | Product costs, valuations, stock moves |
| **Inventory** | Stock Moves Report | XLSX, CSV | All stock movements (in/out/transfers) |
| **Purchasing** | Purchase Analysis | XLSX, CSV | Vendor info, purchase orders, lead times |
| **POS** | Point of Sale Orders | XLSX, CSV | Session data, payments, products sold |
| **Accounting** | Invoice Analysis | XLSX, CSV | Customer invoices, payments, aging |

### Odoo 18.0 Data Mapping Schema

```yaml
odoo_18_mapping:
  
  sales_report:
    required_columns:
      - order_date: "date"
      - product_name: "product_id/name"
      - product_sku: "product_id/default_code"
      - quantity: "product_uom_qty"
      - unit_price: "price_unit"
      - total_amount: "price_subtotal"
      - location: "order_id/warehouse_id/name"
      - salesperson: "salesman_id/name"
      - state: "state"
    
  inventory_report:
    required_columns:
      - product_name: "product_id/name"
      - product_sku: "product_id/default_code"
      - location: "location_id/complete_name"
      - quantity_on_hand: "quantity"
      - reserved_quantity: "reserved_quantity"
      - available_quantity: "available_quantity"
      - lot_number: "lot_id/name"
      - expiry_date: "expiration_date"
      - category: "product_id/categ_id/name"
    
  stock_moves_report:
    required_columns:
      - date: "date"
      - product_name: "product_id/name"
      - product_sku: "product_id/default_code"
      - source_location: "location_id/complete_name"
      - dest_location: "location_dest_id/complete_name"
      - quantity: "product_uom_qty"
      - move_type: "picking_type_id/name"
      - status: "state"
```

---

## Operator-Friendly Interface Design

### Main Navigation Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏠 Dashboard    📊 Analytics    🤖 AI Assistant    📑 Reports    ⚙️ Settings │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📊 ANALYTICS HUB                                      [? Help]     │   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │  │   SALES     │  │  INVENTORY  │  │  LOCATION   │  │   BUSINESS  │ │   │
│  │  │   📈        │  │   📦        │  │   📍        │  │    TYPE     │ │   │
│  │  │  [Active]   │  │  [Click]    │  │  [Click]    │  │   [Click]   │ │   │
│  │  │  Green      │  │   Blue      │  │   Orange    │  │   Purple    │ │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  Sub-Analysis Switcher:  [Trend] [Performance] [Forecast]   │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Section-Specific Switcher Layouts

#### Sales Analysis Section
```
┌─────────────────────────────────────────────────────────────────┐
│  🔀 QUICK SWITCH:                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Overview │ │ Trends   │ │ Products │ │ Compare  │ │ Export │ │
│  │   [●]    │ │   [○]    │ │   [○]    │ │   [○]    │ │  [↓]   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│                                                                 │
│  📅 Period: [Today ▼]  📍 Location: [All Locations ▼]           │
│                                                                 │
│  [Main Content Area - Charts/Tables based on selection]         │
└─────────────────────────────────────────────────────────────────┘
```

#### Inventory Analysis Section
```
┌─────────────────────────────────────────────────────────────────┐
│  🔀 QUICK SWITCH:                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Stock    │ │ Movement │ │ Alerts   │ │ Valuation│ │ Reorder│ │
│  │ Levels   │ │ Analysis │ │          │ │          │ │ Points │ │
│  │   [●]    │ │   [○]    │ │   [○]    │ │   [○]    │ │  [○]   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│                                                                 │
│  🚨 Alert Filter: [All] [Low Stock] [Overstock] [Expiring]      │
│                                                                 │
│  [Main Content Area - Inventory-specific visualizations]        │
└─────────────────────────────────────────────────────────────────┘
```

#### Location Analysis Section
```
┌─────────────────────────────────────────────────────────────────┐
│  🔀 QUICK SWITCH:                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Compare  │ │ Heatmap  │ │ Top      │ │ Location │ │ Trends │ │
│  │ Locations│ │          │ │ Performer│ │ Details  │ │        │ │
│  │   [●]    │ │   [○]    │ │   [○]    │ │   [○]    │ │  [○]   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│                                                                 │
│  🗺️ Map View: [On/Off Toggle]  📊 Metric: [Sales ▼]             │
│                                                                 │
│  [Main Content Area - Location-based analysis]                  │
└─────────────────────────────────────────────────────────────────┘
```

#### Business Type Analysis Section
```
┌─────────────────────────────────────────────────────────────────┐
│  🔀 QUICK SWITCH:                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Category │ │ Margin   │ │ Cross-Sell│ │ Seasonal │ │ Mix    │ │
│  │ Mix      │ │ Analysis │ │ Analysis  │ │ Trends   │ │ Optimization│
│  │   [●]    │ │   [○]    │ │   [○]    │ │   [○]    │ │  [○]   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│                                                                 │
│  🏷️ Categories: [All] [Snacks] [Beverages] [Fresh] [Frozen]     │
│                                                                 │
│  [Main Content Area - Category-based analysis]                  │
└─────────────────────────────────────────────────────────────────┘
```

### Color-Coded Analysis Sections

| Section | Primary Color | Hex Code | Icon | Usage |
|---------|--------------|----------|------|-------|
| Sales | Green | #10B981 | 📈 | Revenue, growth, positive metrics |
| Inventory | Blue | #3B82F6 | 📦 | Stock levels, movements |
| Location | Orange | #F59E0B | 📍 | Geographic, comparative |
| Business Type | Purple | #8B5CF6 | 🏷️ | Categories, classifications |
| Alerts | Red | #EF4444 | 🚨 | Warnings, urgent actions |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Alt + 1` | Switch to Sales Analysis |
| `Alt + 2` | Switch to Inventory Analysis |
| `Alt + 3` | Switch to Location Analysis |
| `Alt + 4` | Switch to Business Type Analysis |
| `Alt + C` | Open AI Chat |
| `Alt + U` | Upload File |
| `Alt + R` | Generate Report |
| `Esc` | Close modal/return to dashboard |

### Quick Action Buttons

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚡ QUICK ACTIONS                                               │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐   │
│  │ 📤 Upload  │ │ 🤖 Ask AI  │ │ 📊 Report  │ │ 🔔 Alerts  │   │
│  │   Report   │ │  Question  │ │  Generate  │ │   View     │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### Core Tables

```sql
-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) DEFAULT 'operator',
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    default_location_id UUID,
    default_analysis_view VARCHAR(50) DEFAULT 'sales_overview',
    dashboard_layout JSONB,
    notification_settings JSONB,
    theme VARCHAR(20) DEFAULT 'light',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- BUSINESS STRUCTURE
-- ============================================

CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    manager_name VARCHAR(200),
    manager_phone VARCHAR(20),
    manager_email VARCHAR(255),
    operating_hours JSONB,
    is_active BOOLEAN DEFAULT true,
    odoo_warehouse_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE business_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    typical_categories JSONB,
    default_margin_percent DECIMAL(5,2),
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    location_id UUID REFERENCES locations(id),
    type_id UUID REFERENCES business_types(id),
    operator_id UUID REFERENCES users(id),
    odoo_company_id VARCHAR(100),
    settings JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- PRODUCT MASTER DATA
-- ============================================

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES categories(id),
    odoo_category_id VARCHAR(100),
    attributes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category_id UUID REFERENCES categories(id),
    unit_of_measure VARCHAR(50) DEFAULT 'units',
    cost_price DECIMAL(12, 2),
    selling_price DECIMAL(12, 2),
    supplier_info JSONB,
    barcode VARCHAR(100),
    odoo_product_id VARCHAR(100),
    odoo_template_id VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INVENTORY DATA
-- ============================================

CREATE TABLE inventory_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID REFERENCES locations(id),
    product_id UUID REFERENCES products(id),
    quantity_on_hand DECIMAL(12, 3) DEFAULT 0,
    quantity_reserved DECIMAL(12, 3) DEFAULT 0,
    quantity_available DECIMAL(12, 3) DEFAULT 0,
    reorder_point DECIMAL(12, 3),
    max_stock_level DECIMAL(12, 3),
    lot_number VARCHAR(100),
    expiry_date DATE,
    valuation DECIMAL(15, 2),
    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    odoo_quant_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_movements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID REFERENCES locations(id),
    product_id UUID REFERENCES products(id),
    movement_type VARCHAR(50),
    source_location VARCHAR(200),
    destination_location VARCHAR(200),
    quantity DECIMAL(12, 3),
    unit_cost DECIMAL(12, 2),
    reference_document VARCHAR(100),
    movement_date TIMESTAMP,
    odoo_move_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- SALES DATA
-- ============================================

CREATE TABLE sales_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID REFERENCES locations(id),
    product_id UUID REFERENCES products(id),
    transaction_date TIMESTAMP NOT NULL,
    quantity DECIMAL(12, 3) NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    discount_amount DECIMAL(12, 2) DEFAULT 0,
    tax_amount DECIMAL(12, 2) DEFAULT 0,
    payment_method VARCHAR(50),
    salesperson VARCHAR(100),
    customer_type VARCHAR(50),
    session_id VARCHAR(100),
    odoo_order_id VARCHAR(100),
    odoo_order_line_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sales_daily_summary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID REFERENCES locations(id),
    summary_date DATE NOT NULL,
    total_transactions INTEGER DEFAULT 0,
    total_quantity DECIMAL(12, 3) DEFAULT 0,
    total_revenue DECIMAL(15, 2) DEFAULT 0,
    total_cost DECIMAL(15, 2) DEFAULT 0,
    gross_profit DECIMAL(15, 2) DEFAULT 0,
    unique_products_sold INTEGER DEFAULT 0,
    average_transaction_value DECIMAL(12, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location_id, summary_date)
);

-- ============================================
-- DATA IMPORT & API MANAGEMENT
-- ============================================

CREATE TABLE data_imports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id),
    import_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255),
    file_size_bytes BIGINT,
    odoo_version VARCHAR(20) DEFAULT '18.0',
    report_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    records_processed INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    error_log JSONB,
    mapping_config JSONB,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_connections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id),
    connection_name VARCHAR(100) NOT NULL,
    odoo_url VARCHAR(500) NOT NULL,
    odoo_version VARCHAR(20) DEFAULT '18.0',
    database_name VARCHAR(100) NOT NULL,
    api_key_encrypted TEXT,
    username VARCHAR(100),
    is_active BOOLEAN DEFAULT false,
    last_sync_at TIMESTAMP,
    sync_frequency_minutes INTEGER DEFAULT 60,
    sync_status VARCHAR(50) DEFAULT 'never_run',
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sync_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    connection_id UUID REFERENCES api_connections(id),
    job_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'running',
    records_synced INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- ============================================
-- ANALYTICS & REPORTING
-- ============================================

CREATE TABLE saved_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    sub_type VARCHAR(50),
    filters JSONB,
    visualization_config JSONB,
    is_favorite BOOLEAN DEFAULT false,
    last_accessed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE generated_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    report_type VARCHAR(100) NOT NULL,
    parameters JSONB,
    file_path VARCHAR(500),
    file_format VARCHAR(20),
    status VARCHAR(50) DEFAULT 'generating',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    download_count INTEGER DEFAULT 0
);

-- ============================================
-- AI/MCP CONTEXT
-- ============================================

CREATE TABLE chat_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(200),
    context JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES chat_conversations(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tool_calls JSONB,
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_context_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id),
    context_type VARCHAR(50),
    context_data JSONB,
    valid_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_sales_location_date ON sales_transactions(location_id, transaction_date);
CREATE INDEX idx_sales_product_date ON sales_transactions(product_id, transaction_date);
CREATE INDEX idx_inventory_location_product ON inventory_snapshots(location_id, product_id);
CREATE INDEX idx_inventory_expiry ON inventory_snapshots(expiry_date) WHERE expiry_date IS NOT NULL;
CREATE INDEX idx_movements_location_date ON inventory_movements(location_id, movement_date);
CREATE INDEX idx_imports_business_type ON data_imports(business_id, import_type);
```

---

## Data Flow Diagrams

### File Upload Flow (Odoo 18.0 Reports)

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User    │────▶│  Drag & Drop │────▶│  File Type   │────▶│  File Size   │
│          │     │    Zone      │     │  Validation  │     │  Check       │
└──────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                  │
                                                                  ▼
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Store   │◀────│  Parse Data  │◀────│  Validate    │◀────│  Detect      │
│  Records │     │  to Tables   │     │  Schema      │     │  Odoo 18.0   │
│          │     │              │     │  (Columns)   │     │  Format      │
└──────────┘     └──────────────┘     └──────────────┘     └──────────────┘
      │
      ▼
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│  Update  │────▶│  Aggregate   │────▶│  Update      │────▶│  Notify  │
│  Raw     │     │  Metrics     │     │  Dashboard   │     │  User    │
│  Tables  │     │  (Summary)   │     │  Cache       │     │          │
└──────────┘     └──────────────┘     └──────────────┘     └──────────┘
      │
      ▼
┌──────────┐
│  MCP     │
│  Context │
│  Refresh │
└──────────┘

DETAILED STEPS:
1. User selects report type from dropdown (Sales/Inventory/Stock Moves/etc.)
2. System shows Odoo 18.0 template preview with expected columns
3. User uploads file (CSV/XLSX)
4. System validates file structure against Odoo 18.0 schema
5. Data is parsed and mapped to internal tables
6. Validation errors shown with row numbers (if any)
7. Preview of first 10 rows for user confirmation
8. On confirm: data committed to database
9. Dashboards and AI context auto-refresh
```

### API Integration Flow (Odoo 18.0)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Scheduler  │────▶│  API         │────▶│  Odoo 18.0   │────▶│  Fetch       │
│  (Cron Job) │     │  Connection  │     │  JSON-RPC    │     │  Data        │
│             │     │  Check       │     │  API         │     │  (Paginated) │
└─────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                     │
                                                                     ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Update     │◀────│  Transform   │◀────│  Map to      │◀────│  Validate    │
│  Database   │     │  & Enrich    │     │  Internal    │     │  Schema      │
│             │     │              │     │  Schema      │     │              │
└──────┬──────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │
       ├──────────────────────────────────────────────────────────────────────┐
       │                                                                      │
       ▼                                                                      ▼
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Trigger    │────▶│  Recalculate │────▶│  Update      │────▶│  Push to     │
│  Analytics  │     │  KPIs        │     │  Dashboard   │     │  MCP Context │
│  Engine     │     │              │     │  (WebSocket) │     │  Store       │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘

SYNC TYPES:
├─ Full Sync: Weekly - Complete data refresh
├─ Incremental: Hourly - Only changed records (using write_date)
├─ Real-time: Webhooks - Immediate updates (if supported)
└─ On-demand: User triggered - Manual refresh button
```

### Analysis Switcher Flow

```
User Action: Click "Inventory" Tab
                    │
                    ▼
┌─────────────────────────────────┐
│ 1. Capture Current State        │
│    - Save filters to session    │
│    - Record scroll position     │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ 2. Load Inventory Section       │
│    - Fetch inventory data       │
│    - Apply default filters      │
│    - Load sub-analysis tabs     │
│    │ Stock Levels (default)     │
│    │ Movement Analysis          │
│    │ Alerts                     │
│    │ Valuation                  │
│    │ Reorder Points             │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ 3. Render Interface             │
│    - Show tab switcher          │
│    - Display default sub-view   │
│    - Preserve common filters    │
│      (date range, location)     │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│ 4. Enable Sub-Switching         │
│    User clicks "Alerts" tab     │
│    │                            │
│    ├─ Instant tab switch (no    │
│    │  page reload)              │
│    ├─ Fetch alert-specific data │
│    ├─ Update URL: /analytics/   │
│    │  inventory/alerts          │
│    └─ Update breadcrumb         │
└─────────────────────────────────┘

STATE MANAGEMENT:
├─ URL encodes: /analytics/{section}/{sub-section}?filters...
├─ Browser back button works
├─ Deep linking supported
└─ Filter persistence across switches
```

---

## Technology Stack

### Frontend
| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| Framework | React/Next.js 14 | SSR support, App Router, rich ecosystem |
| UI Library | Tailwind CSS + Headless UI | Customizable, accessible, responsive |
| Charts | Recharts + D3.js | Interactive visualizations |
| State Management | Zustand | Lightweight, TypeScript-friendly |
| Maps | Mapbox GL JS | Location visualization |
| Icons | Lucide React | Clean, modern icon set |

### Backend
| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| API Framework | Node.js + Express or Python + FastAPI | MCP server compatibility |
| Database | PostgreSQL 15 | Relational data, JSON support |
| Cache | Redis 7 | Session, real-time data, job queues |
| Queue | Bull (Redis-based) | Background job processing |
| Vector DB | Pinecone or Weaviate | AI embeddings storage |
| ORM | Prisma (Node) or SQLAlchemy (Python) | Type-safe database access |

### AI/MCP Layer
| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| MCP Server | TypeScript SDK | Standard protocol implementation |
| LLM | Claude 3.5 Sonnet or GPT-4 | Natural language understanding |
| Embeddings | text-embedding-3-large | Semantic search quality |
| Context Management | Custom + Redis | Fast context retrieval |

### Infrastructure
| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| Hosting | AWS/GCP/Azure | Scalable, managed services |
| Containerization | Docker + Kubernetes | Deployment consistency |
| CI/CD | GitHub Actions | Automated testing/deployment |
| Monitoring | Datadog or Grafana | Performance tracking |
| Object Storage | AWS S3 | Report file storage |

---

## Implementation Phases

### Phase 1: Foundation & File Upload (Weeks 1-4)

**Week 1: Project Setup**
- [ ] Initialize repository with Next.js + TypeScript
- [ ] Setup PostgreSQL database with initial schema
- [ ] Configure Tailwind CSS with custom theme
- [ ] Setup development environment (Docker)
- [ ] Create basic folder structure

**Week 2: Authentication & User Management**
- [ ] Implement JWT-based authentication
- [ ] Create login/register pages
- [ ] Setup user roles (admin, operator, viewer)
- [ ] User profile management
- [ ] Password reset functionality

**Week 3: File Upload System for Odoo 18.0**
- [ ] Create upload interface with drag-and-drop
- [ ] Implement Odoo 18.0 report parsers:
  - Sales Analysis Report parser
  - Inventory Report parser
  - Stock Moves Report parser
- [ ] Column validation against Odoo 18.0 schemas
- [ ] Error handling with row-level feedback
- [ ] Data preview before commit

**Week 4: Data Storage & Basic Dashboard**
- [ ] Complete data import pipeline
- [ ] Create database tables for sales, inventory
- [ ] Build basic dashboard layout
- [ ] Implement KPI cards (total sales, stock levels)
- [ ] Setup Redis for caching

**Deliverables:**
- Working file upload for Odoo 18.0 reports
- Basic dashboard with key metrics
- User authentication system

---

### Phase 2: Analysis Interface & Switcher (Weeks 5-8)

**Week 5: Analysis Switcher Component**
- [ ] Build main analysis navigation (Sales, Inventory, Location, Business Type)
- [ ] Implement sub-analysis tabs within each section
- [ ] Create URL-based routing for deep linking
- [ ] State persistence across tab switches
- [ ] Mobile-responsive switcher design

**Week 6: Sales Analysis Module**
- [ ] Sales Overview: Total sales, growth charts
- [ ] Sales Trends: Time-series visualization
- [ ] Product Performance: Top/bottom sellers
- [ ] Comparison Tools: Period-over-period
- [ ] Export functionality (CSV/PDF)

**Week 7: Inventory Analysis Module**
- [ ] Stock Levels: Current inventory view
- [ ] Movement Analysis: In/out/transfer tracking
- [ ] Alerts: Low stock, overstock, expiring
- [ ] Valuation: Inventory value calculations
- [ ] Reorder Points: Automated suggestions

**Week 8: Location & Business Type Analysis**
- [ ] Location Comparison: Side-by-side metrics
- [ ] Heatmap Visualization: Geographic performance
- [ ] Business Type Mix: Category analysis
- [ ] Margin Analysis: Profitability by category
- [ ] Cross-selling Opportunities

**Deliverables:**
- Complete analysis switcher interface
- All four analysis modules functional
- Interactive charts and visualizations

---

### Phase 3: AI Chat Bot & MCP Server (Weeks 9-12)

**Week 9: MCP Server Setup**
- [ ] Setup MCP server with stdio/SSE transport
- [ ] Define resources (inventory://, sales://)
- [ ] Implement tool registry
- [ ] Create context management system
- [ ] Connect to vector database

**Week 10: MCP Tools Development**
- [ ] `query_inventory(location, product)` tool
- [ ] `analyze_sales(period, location)` tool
- [ ] `generate_forecast(product, days)` tool
- [ ] `compare_locations(metric)` tool
- [ ] `get_alerts(severity)` tool

**Week 11: Chat Interface**
- [ ] Build chat UI component
- [ ] Integrate with MCP server
- [ ] Implement conversation history
- [ ] Add suggested questions
- [ ] Context-aware responses

**Week 12: AI Enhancements**
- [ ] Prompt templates for business insights
- [ ] Natural language to query translation
- [ ] Alert summarization
- [ ] Recommendation engine
- [ ] Multi-turn conversation support

**Deliverables:**
- Functional AI chat bot
- MCP server with business tools
- Natural language querying capability

---

### Phase 4: Reporting & API Integration (Weeks 13-16)

**Week 13: Reporting Engine**
- [ ] Report template builder
- [ ] Scheduled report generation
- [ ] Email delivery system
- [ ] Report history and versioning
- [ ] Custom report creation UI

**Week 14: Odoo 18.0 API Connector**
- [ ] API connection configuration UI
- [ ] Odoo 18.0 JSON-RPC client
- [ ] Authentication handling
- [ ] Field mapping interface
- [ ] Connection testing

**Week 15: Scheduled Sync**
- [ ] Background job scheduler (Bull/Agenda)
- [ ] Incremental sync logic
- [ ] Conflict resolution
- [ ] Sync monitoring dashboard
- [ ] Error handling and retries

**Week 16: Migration Tools**
- [ ] Data migration from file-based to API-based
- [ ] Historical data preservation
- [ ] Validation and reconciliation
- [ ] Rollback capabilities

**Deliverables:**
- Automated report generation
- Odoo 18.0 API integration
- Scheduled data synchronization

---

### Phase 5: Advanced Features & Optimization (Weeks 17-20)

**Week 17: Advanced Analytics**
- [ ] Machine learning forecasting
- [ ] Anomaly detection
- [ ] Correlation analysis
- [ ] Predictive inventory alerts
- [ ] Demand planning

**Week 18: Performance Optimization**
- [ ] Database query optimization
- [ ] Implement materialized views
- [ ] CDN setup for static assets
- [ ] Caching strategy refinement
- [ ] Load testing

**Week 19: Mobile App (PWA)**
- [ ] Progressive Web App setup
- [ ] Offline capability
- [ ] Push notifications
- [ ] Mobile-optimized charts
- [ ] Quick actions

**Week 20: Final Polish**
- [ ] User acceptance testing
- [ ] Documentation
- [ ] Training materials
- [ ] Production deployment
- [ ] Monitoring setup

**Deliverables:**
- Production-ready platform
- Complete documentation
- User training materials

---

## Success Criteria

### By Phase

| Phase | Success Criteria | Measurement |
|-------|-----------------|-------------|
| **Phase 1** | Upload Odoo 18.0 reports with <5% error rate | Test with 50 sample reports |
| **Phase 2** | Switch between analysis sections in <2 seconds | Performance testing |
| **Phase 3** | AI answers 80% of common queries correctly | User testing sessions |
| **Phase 4** | API sync completes without manual intervention | 7-day monitoring period |
| **Phase 5** | Platform handles 1000+ daily active users | Load testing |

### Overall Platform KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Data Processing Time | < 5 minutes per report | Upload to dashboard update |
| AI Response Time | < 3 seconds | Query to response |
| Analysis Switch Time | < 2 seconds | Click to render |
| System Uptime | 99.9% | Monitoring dashboard |
| User Adoption | 80% active users | Weekly active users |
| Data Accuracy | 99.5% | Validation checks |
| Mobile Responsiveness | < 3 seconds load | Lighthouse score > 90 |

---

## MCP Server Architecture

```
┌─────────────────────────────────────────┐
│           MCP Server                    │
│  ┌─────────────────────────────────┐    │
│  │         Resources               │    │
│  │  • inventory://{location}/stock │    │
│  │  • sales://{date_range}/summary │    │
│  │  • reports://{type}/{date}      │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │          Tools                  │    │
│  │  • query_inventory(location)    │    │
│  │  • analyze_sales(period)        │    │
│  │  • generate_forecast(product)   │    │
│  │  • compare_locations()          │    │
│  │  • get_business_summary()       │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │        Prompts                  │    │
│  │  • business_summary_template    │    │
│  │  • inventory_alert_template     │    │
│  │  • sales_analysis_template      │    │
│  │  • location_comparison_template   │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Example AI Interactions

| User Query | MCP Tool Used | Response Type |
|------------|--------------|---------------|
| "What's my inventory turnover for Location A this month?" | `analyze_inventory_turnover` | Metric + trend chart |
| "Compare sales performance between snacks and beverages" | `compare_categories` | Comparison table + insights |
| "Which products are running low at the downtown location?" | `query_inventory` with filters | Alert list + reorder suggestions |
| "Generate a restocking recommendation for next week" | `generate_forecast` + `get_reorder_points` | Purchase order recommendations |
| "Show me the best performing location this quarter" | `compare_locations` | Ranking + performance metrics |

---

## Security Considerations

| Layer | Measures |
|-------|----------|
| Authentication | OAuth 2.0 / JWT tokens with refresh |
| Authorization | Role-based access control (RBAC) |
| Data Encryption | At-rest (AES-256) + In-transit (TLS 1.3) |
| API Security | Rate limiting, API key rotation, IP whitelist |
| File Upload | Virus scanning, file type validation, size limits |
| Audit Logging | All data access and modifications logged |
| Odoo Credentials | Encrypted storage, never logged |

---

## Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| Odoo 18.0 API changes | Abstract API layer, version pinning, adapter pattern |
| Large data volumes | Pagination, incremental sync, data archiving policy |
| AI hallucination | Grounding in actual data, confidence scores, citations |
| Data privacy | PII masking, GDPR/CCPA compliance, data retention policies |
| Performance degradation | Caching layers, CDN, database indexing, connection pooling |
| File upload failures | Row-level error reporting, partial import capability, retry logic |

---

## Next Steps

1. **Requirements Validation**: Review this plan with stakeholders
2. **Odoo 18.0 Access**: Obtain API documentation and sample reports
3. **Tech Stack Finalization**: Choose between Node.js and Python based on team expertise
4. **UI/UX Design**: Create Figma wireframes for analysis switcher
5. **Development Environment**: Setup Docker containers and CI/CD pipeline
6. **MVP Scope**: Define minimum viable features for initial launch

---

**Document Version**: 1.0  
**Last Updated**: Planning Phase  
**Status**: Ready for Development