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
