OperatorDash/docs/database_schema.md
```

# Micromarket Operator Platform - Database Schema

## Overview

This document outlines the high-level database schema design for the Micromarket Operator Platform. The schema is optimized for inventory management, sales analytics, and AI-powered insights.

---

## Core Entities

### 1. Operators (Users)
Stores platform users and their access levels.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | String | Unique identifier |
| name | String | Display name |
| role | Enum | admin/manager/analyst/viewer |
| preferences | JSON | UI settings, timezone |
| last_login | Timestamp | Activity tracking |

**Relationships:**
- One operator → Many micromarkets
- One operator → Many chat sessions
- One operator → Many file uploads

---

### 2. Micromarkets
Represents individual store locations.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| operator_id | UUID | Owner reference |
| name | String | Display name |
| code | String | Unique location code |
| location | GeoPoint | Lat/long coordinates |
| address | Text | Full address |
| timezone | String | For local time calculations |
| status | Enum | active/inactive/maintenance |
| settings | JSON | Currency, tax rates, hours |

**Relationships:**
- One micromarket → Many inventory records
- One micromarket → Many sales transactions
- One micromarket → Many insights

---

### 3. Products
Master catalog of all sellable items.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sku | String | Unique stock keeping unit |
| barcode | String | Scannable identifier |
| name | String | Product name |
| category_id | UUID | Category reference |
| supplier_id | UUID | Supplier reference |
| unit_price | Decimal | Selling price |
| cost_price | Decimal | Acquisition cost |
| unit_of_measure | String | units/kg/liters/etc |
| is_perishable | Boolean | Expiration tracking |
| shelf_life_days | Integer | Days until expiration |
| odoo_product_id | String | External system mapping |

**Relationships:**
- One product → One category
- One product → One supplier
- One product → Many inventory records
- One product → Many sale line items

---

### 4. Categories
Hierarchical product classification.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | String | Category name |
| parent_id | UUID | Self-reference for hierarchy |
| odoo_category_id | String | External mapping |

**Relationships:**
- Self-referential (parent/child categories)
- One category → Many products

---

### 5. Suppliers
Vendor and manufacturer information.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | String | Company name |
| contact_person | String | Primary contact |
| email | String | Contact email |
| phone | String | Contact phone |
| lead_time_days | Integer | Average delivery time |
| odoo_partner_id | String | External mapping |

**Relationships:**
- One supplier → Many products

---

## Inventory Management

### 6. Inventory (Stock Levels)
Current stock snapshot per market-product combination.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| product_id | UUID | Product reference |
| market_id | UUID | Market reference |
| quantity_on_hand | Decimal | Physical count |
| quantity_reserved | Decimal | Committed to orders |
| quantity_available | Computed | On hand minus reserved |
| reorder_point | Decimal | Trigger level for reorder |
| min_stock_level | Decimal | Safety stock minimum |
| max_stock_level | Decimal | Storage capacity limit |
| location_code | String | Bin/shelf location |
| last_counted | Timestamp | Last physical count |

**Key Features:**
- Unique constraint on (product_id, market_id)
- Computed available quantity
- Supports multiple storage locations per market

---

### 7. Stock Moves
Historical inventory transactions (Time-series data).

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| product_id | UUID | Product reference |
| market_id | UUID | Market reference |
| move_type | Enum | in/out/transfer/adjustment |
| quantity | Decimal | Positive or negative |
| unit_cost | Decimal | Cost at time of move |
| reference | String | PO/SO number |
| source_location | String | Where from |
| destination_location | String | Where to |
| move_date | Timestamp | When occurred |
| odoo_move_id | String | External reference |

**Storage:** TimescaleDB hypertable for time-series optimization

---

## Sales & Transactions

### 8. Sales
Header records for transactions (Time-series data).

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sale_number | String | Human-readable reference |
| market_id | UUID | Where sold |
| sale_date | Timestamp | Transaction time |
| channel | Enum | pos/online/mobile/manual |
| status | Enum | draft/confirmed/completed/cancelled |
| subtotal | Decimal | Before tax/discounts |
| tax_amount | Decimal | Tax collected |
| discount_amount | Decimal | Discounts applied |
| total_amount | Decimal | Final amount |
| customer_name | String | Optional for B2B |
| odoo_order_id | String | External reference |

**Storage:** TimescaleDB hypertable for time-series optimization

---

### 9. Sale Items
Line items within sales.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sale_id | UUID | Parent sale |
| product_id | UUID | Product sold |
| quantity | Decimal | Units sold |
| unit_price | Decimal | Price at sale |
| cost_price | Decimal | Cost for margin calc |
| discount_percent | Decimal | Line discount |
| total_price | Decimal | Line total |

---

### 10. Payments
Payment records linked to sales.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sale_id | UUID | Parent sale |
| amount | Decimal | Payment amount |
| method | Enum | cash/card/mobile/bank |
| status | Enum | pending/completed/failed |
| transaction_ref | String | External reference |
| paid_at | Timestamp | Completion time |

---

## Analytics & AI

### 11. Analysis Results
AI-generated insights and recommendations.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| analysis_type | String | trend/anomaly/forecast/etc |
| market_id | UUID | Target market (optional) |
| title | String | Display title |
| description | Text | Detailed explanation |
| severity | Enum | info/low/medium/high/critical |
| category | String | inventory/sales/pricing/ops |
| metrics | JSON | Structured data |
| insights | JSON | AI-generated findings |
| recommendations | JSON | Suggested actions |
| status | Enum | active/resolved/dismissed |
| display_priority | Integer | Sort order |
| expires_at | Timestamp | Validity period |

---

### 12. Daily Metrics
Aggregated statistics for fast dashboard queries.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| market_id | UUID | Target market |
| metric_date | Date | Aggregation date |
| total_sales | Decimal | Daily revenue |
| total_transactions | Integer | Count of sales |
| avg_transaction_value | Decimal | Average ticket |
| stock_value | Decimal | Inventory valuation |
| stockout_count | Integer | Products out of stock |
| low_stock_count | Integer | Below reorder point |
| gross_profit | Decimal | Profit amount |
| gross_margin_percent | Decimal | Margin percentage |

**Storage:** TimescaleDB hypertable for historical analysis

---

## Data Import

### 13. Uploaded Files
Tracks Odoo report uploads and processing.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| operator_id | UUID | Who uploaded |
| market_id | UUID | Target market |
| original_filename | String | User-facing name |
| file_type | Enum | stock_report/sales_report/etc |
| file_size | Integer | Bytes |
| status | Enum | pending/processing/completed/failed |
| records_processed | Integer | Success count |
| records_failed | Integer | Error count |
| parsed_summary | JSON | Processing results |
| storage_path | String | S3/MinIO location |

---

### 14. File Processing Logs
Detailed processing history.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| file_id | UUID | Parent file |
| log_level | Enum | info/warning/error/debug |
| message | Text | Log entry |
| details | JSON | Additional context |

---

## Chatbot & MCP

### 15. Chat Sessions
Conversational sessions with AI.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| operator_id | UUID | User reference |
| market_id | UUID | Default context market |
| title | String | Session name |
| context | JSON | Active filters, settings |
| message_count | Integer | Total messages |
| total_tokens | Integer | LLM usage |
| started_at | Timestamp | Creation time |
| last_activity | Timestamp | Last message |
| rating | Integer | User feedback (1-5) |

---

### 16. Chat Messages
Individual messages within sessions.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| session_id | UUID | Parent session |
| role | Enum | user/assistant/system/tool |
| content | Text | Message content |
| tool_calls | JSON | MCP tool invocations |
| tool_results | JSON | Tool execution results |
| model | String | LLM model used |
| tokens_input | Integer | Input token count |
| tokens_output | Integer | Output token count |
| latency_ms | Integer | Response time |

---

### 17. MCP Tool Executions
Audit log of AI tool usage.

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| session_id | UUID | Chat session |
| tool_name | String | Which tool |
| tool_input | JSON | Parameters |
| tool_output | JSON | Results |
| execution_time_ms | Integer | Duration |
| success | Boolean | Success flag |
| error_message | Text | If failed |

---

## Entity Relationship Diagram

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│    operators    │◄──────┤  micromarkets    │       │   categories    │
└─────────────────┘       └────────┬─────────┘       └────────┬────────┘
                                   │                          │
                                   │                          │
                          ┌────────┴─────────┐                │
                          │                  │                │
                   ┌──────▼──────┐    ┌─────▼──────┐   ┌─────▼──────┐
                   │   products   │    │  inventory │   │  products   │
                   └──────┬──────┘    └────────────┘   └────────────┘
                          │
                   ┌──────┴──────────┐
                   │                   │
            ┌─────▼──────┐     ┌──────▼─────┐
            │  suppliers  │     │   sales    │
            └─────────────┘     └─────┬──────┘
                                      │
                               ┌──────┴──────────┐
                               │                  │
                        ┌──────▼──────┐    ┌─────▼──────┐
                        │  sale_items │    │  payments  │
                        └─────────────┘    └────────────┘

┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│  uploaded_files │       │  analysis_results│       │  chat_sessions  │
└─────────────────┘       └──────────────────┘       └────────┬────────┘
                                                              │
                                                              ▼
                                                        ┌─────────────┐
                                                        │chat_messages│
                                                        └─────────────┘
```

---

## Data Flow from Odoo

### Odoo Report → Platform Mapping

| Odoo Report | Target Tables | Key Mappings |
|-------------|---------------|--------------|
| **Stock Report** | products, inventory | SKU → products.sku, Quantity → inventory.quantity_on_hand |
| **Inventory Valuation** | products, inventory | Cost → products.cost_price, Value → calculated |
| **Product Moves** | stock_moves | All fields direct mapping |
| **Sales Analysis** | sales, sale_items | Order → sales, Lines → sale_items |
| **Partner List** | suppliers | Partner → suppliers |

### Processing Flow

```
Odoo Export (CSV/Excel)
        │
        ▼
   [Upload API]
        │
        ▼
   [Validation Layer]
   - Schema check
   - Data type validation
   - Referential integrity
        │
        ┌──────────┬──────────┐
        ▼          ▼          ▼
   [Products] [Inventory] [Sales]
        │          │          │
        └──────────┼──────────┘
                   │
                   ▼
           [Analytics Trigger]
           - Refresh materialized views
           - Invalidate caches
           - Queue insight generation
```

---

## Key Design Decisions

### 1. Time-Series Optimization
- **Stock moves** and **sales** use TimescaleDB hypertables
- Automatic partitioning by date
- Efficient time-range queries for analytics

### 2. Flexible Metadata
- JSONB columns for extensible attributes
- Product metadata, operator preferences, market settings
- Schema evolution without migrations

### 3. Computed Fields
- inventory.quantity_available (on_hand - reserved)
- Daily metrics aggregated from source tables
- Real-time views for current status

### 4. External System Mapping
- odoo_*_id fields for cross-reference
- Enables bidirectional sync if needed
- Preserves source system identity

### 5. Soft Deletes
- is_active flags instead of hard deletes
- Maintains referential integrity
- Audit trail preservation

---

## Indexing Strategy

### High-Frequency Queries
- inventory: (product_id, market_id) - unique constraint
- sales: (market_id, sale_date) - time-series queries
- stock_moves: (product_id, move_date) - movement history
- analysis_results: (market_id, status, created_at) - dashboard

### Search Optimization
- products: Full-text search on name + SKU
- categories: Recursive query support for hierarchy
- uploaded_files: Status + type filtering

---

## Data Retention

| Data Type | Retention | Archive Strategy |
|-----------|-----------|------------------|
| Raw uploads | 90 days | Move to cold storage |
| Stock moves | 2 years | Aggregate to monthly |
| Sales details | 5 years | Anonymize after 2 years |
| Chat history | 1 year | Archive to object storage |
| Analysis results | 6 months | Keep summaries only |
| Audit logs | 7 years | Immutable compliance store |

---

## Scaling Considerations

### Read Replicas
- Analytics queries → Read replica
- Dashboard data → Cached + read replica
- Chat history → Read replica

### Partitioning
- Time-series tables by date
- Large markets by geography
- Archival of old data

### Caching Layers
- Redis: Session data, real-time metrics
- Application cache: Product catalog, categories
- CDN: Static reports, exports

---

*Last Updated: January 2025*
*Version: 1.0*