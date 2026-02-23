OperatorDash/docs/api_endpoints.md
```

# API Endpoints Specification

## Base URL
```
Production: https://api.yourdomain.com/v1
Development: http://localhost:8000/v1
```

## Authentication
All endpoints require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

---

## 1. Authentication Endpoints

### POST /auth/register
Register a new operator account.

**Request:**
```json
{
  "email": "operator@example.com",
  "password": "SecurePass123!",
  "name": "John Doe",
  "phone": "+1234567890",
  "timezone": "America/New_York"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "operator@example.com",
  "name": "John Doe",
  "role": "manager",
  "created_at": "2025-01-15T10:30:00Z"
}
```

### POST /auth/login
Authenticate and receive JWT tokens.

**Request:**
```json
{
  "email": "operator@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "operator": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "operator@example.com",
    "name": "John Doe",
    "role": "manager"
  }
}
```

### POST /auth/refresh
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_in": 3600
}
```

### POST /auth/logout
Invalidate current tokens.

**Response (204):** No content

### GET /auth/me
Get current operator profile.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "operator@example.com",
  "name": "John Doe",
  "role": "manager",
  "phone": "+1234567890",
  "timezone": "America/New_York",
  "preferences": {
    "dashboard_layout": "compact",
    "notifications_enabled": true
  },
  "last_login_at": "2025-01-15T10:30:00Z",
  "created_at": "2025-01-01T00:00:00Z"
}
```

### PUT /auth/me
Update operator profile.

**Request:**
```json
{
  "name": "John Doe Updated",
  "phone": "+1987654321",
  "timezone": "Europe/London",
  "preferences": {
    "notifications_enabled": false
  }
}
```

**Response (200):** Updated operator object

---

## 2. Micromarket Endpoints

### GET /markets
List all micromarkets for the operator.

**Query Parameters:**
- `status` (optional): Filter by status (`active`, `inactive`, `maintenance`)
- `search` (optional): Search by name or code
- `limit` (optional): Number of results (default: 20, max: 100)
- `offset` (optional): Pagination offset

**Response (200):**
```json
{
  "total": 15,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Downtown Market",
      "code": "DTM001",
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060
      },
      "address": "123 Main St",
      "city": "New York",
      "state": "NY",
      "country": "USA",
      "status": "active",
      "timezone": "America/New_York",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### POST /markets
Create a new micromarket.

**Request:**
```json
{
  "name": "Uptown Market",
  "code": "UTM001",
  "location": {
    "latitude": 40.7589,
    "longitude": -73.9851
  },
  "address": "456 Broadway",
  "city": "New York",
  "state": "NY",
  "country": "USA",
  "timezone": "America/New_York"
}
```

**Response (201):** Created market object

### GET /markets/{id}
Get detailed information about a specific market.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Downtown Market",
  "code": "DTM001",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "country": "USA",
  "status": "active",
  "timezone": "America/New_York",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### PUT /markets/{id}
Update market information.

**Request:**
```json
{
  "name": "Downtown Market Updated",
  "status": "maintenance"
}
```

**Response (200):** Updated market object

### DELETE /markets/{id}
Delete a micromarket (soft delete).

**Response (204):** No content

### GET /markets/{id}/stats
Get real-time statistics for a market.

**Response (200):**
```json
{
  "market_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2025-01-15T14:30:00Z",
  "inventory": {
    "total_products": 450,
    "total_value": 45000.00,
    "low_stock_items": 12,
    "out_of_stock_items": 3
  },
  "sales": {
    "today": {
      "revenue": 1250.50,
      "transactions": 45,
      "average_ticket": 27.79
    },
    "this_week": {
      "revenue": 8750.00,
      "transactions": 315,
      "growth_percent": 12.5
    }
  }
}
```

### GET /markets/{id}/inventory
Get inventory details for a market.

**Query Parameters:**
- `status` (optional): `all`, `low_stock`, `out_of_stock`, `overstock`
- `category_id` (optional): Filter by category
- `search` (optional): Search by product name or SKU
- `limit` (optional): Default 50, max 500
- `offset` (optional): Pagination offset

**Response (200):**
```json
{
  "total": 450,
  "limit": 50,
  "offset": 0,
  "items": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440100",
      "sku": "BEV001",
      "name": "Organic Coffee",
      "category": "Beverages",
      "quantity_on_hand": 45,
      "quantity_reserved": 5,
      "quantity_available": 40,
      "reorder_point": 20,
      "status": "normal"
    }
  ]
}
```

---

## 3. Product Endpoints

### GET /products
List all products.

**Query Parameters:**
- `category_id` (optional): Filter by category
- `status` (optional): `active`, `inactive`, `all`
- `search` (optional): Search by name, SKU, or barcode
- `limit` (optional): Default 20, max 100
- `offset` (optional): Pagination offset

**Response (200):**
```json
{
  "total": 1250,
  "limit": 20,
  "offset": 0,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "sku": "BEV001",
      "barcode": "123456789012",
      "name": "Organic Coffee",
      "category": {
        "id": "550e8400-e29b-41d4-a716-446655440010",
        "name": "Beverages"
      },
      "unit_price": 5.99,
      "cost_price": 4.50,
      "currency": "USD",
      "is_active": true
    }
  ]
}
```

### POST /products
Create a new product.

**Request:**
```json
{
  "sku": "BEV002",
  "barcode": "123456789013",
  "name": "Green Tea",
  "description": "Organic green tea",
  "category_id": "550e8400-e29b-41d4-a716-446655440010",
  "unit_price": 4.99,
  "cost_price": 3.50,
  "currency": "USD"
}
```

**Response (201):** Created product object

### GET /products/{id}
Get product details.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440100",
  "sku": "BEV001",
  "barcode": "123456789012",
  "name": "Organic Coffee",
  "description": "Premium organic coffee beans",
  "category": {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "name": "Beverages"
  },
  "unit_price": 5.99,
  "cost_price": 4.50,
  "currency": "USD",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z"
}
```

### PUT /products/{id}
Update product.

**Request:**
```json
{
  "unit_price": 6.49,
  "cost_price": 4.75,
  "is_active": true
}
```

**Response (200):** Updated product object

### DELETE /products/{id}
Delete product (soft delete).

**Response (204):** No content

### GET /products/{id}/inventory
Get inventory levels across all markets for a product.

**Response (200):**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440100",
  "total_quantity_on_hand": 450,
  "total_quantity_available": 420,
  "markets": [
    {
      "market_id": "550e8400-e29b-41d4-a716-446655440001",
      "market_name": "Downtown Market",
      "quantity_on_hand": 45,
      "quantity_available": 40,
      "reorder_point": 20,
      "status": "normal"
    }
  ]
}
```

### GET /products/search
Advanced product search.

**Query Parameters:**
- `q` (required): Search query
- `limit` (optional): Default 10, max 50

**Response (200):**
```json
{
  "query": "coffee",
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "sku": "BEV001",
      "name": "Organic Coffee",
      "score": 0.95
    }
  ]
}
```

---

## 4. Inventory Endpoints

### GET /inventory
Get inventory across all markets.

**Query Parameters:**
- `market_id` (optional): Filter by market
- `product_id` (optional): Filter by product
- `status` (optional): `all`, `low_stock`, `out_of_stock`, `overstock`
- `limit` (optional): Default 50, max 500

**Response (200):**
```json
{
  "total": 4500,
  "limit": 50,
  "offset": 0,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440500",
      "product": {
        "id": "550e8400-e29b-41d4-a716-446655440100",
        "sku": "BEV001",
        "name": "Organic Coffee"
      },
      "market": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Downtown Market"
      },
      "quantity_on_hand": 45,
      "quantity_available": 40,
      "status": "normal"
    }
  ]
}
```

### GET /inventory/low-stock
Get all low stock items across markets.

**Response (200):**
```json
{
  "total": 23,
  "items": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440100",
      "sku": "BEV001",
      "name": "Organic Coffee",
      "market_id": "550e8400-e29b-41d4-a716-446655440001",
      "market_name": "Downtown Market",
      "quantity_available": 15,
      "reorder_point": 20,
      "days_until_stockout": 3,
      "suggested_order_quantity": 50
    }
  ]
}
```

### GET /inventory/overstock
Get overstock items.

**Response (200):**
```json
{
  "total": 8,
  "items": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440101",
      "sku": "SNK001",
      "name": "Potato Chips",
      "market_id": "550e8400-e29b-41d4-a716-446655440001",
      "quantity_on_hand": 150,
      "max_stock_level": 100,
      "excess_quantity": 50
    }
  ]
}
```

### GET /inventory/stockouts
Get stockout items.

**Response (200):**
```json
{
  "total": 3,
  "items": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440102",
      "sku": "BEV002",
      "name": "Green Tea",
      "market_id": "550e8400-e29b-41d4-a716-446655440001",
      "days_out_of_stock": 2,
      "lost_sales_estimate": 45.00,
      "suggested_order_quantity": 100
    }
  ]
}
```

### POST /inventory/adjust
Create inventory adjustment.

**Request:**
```json
{
  "market_id": "550e8400-e29b-41d4-a716-446655440001",
  "product_id": "550e8400-e29b-41d4-a716-446655440100",
  "adjustment_type": "count",
  "quantity": 42,
  "reason": "Physical count correction",
  "notes": "Found 3 extra units during monthly count"
}
```

**Response (201):** Adjustment record

### GET /inventory/movements
Get stock movement history.

**Query Parameters:**
- `market_id` (optional): Filter by market
- `product_id` (optional): Filter by product
- `start_date` (optional)
- `end_date` (optional)
- `limit` (optional): Default 50, max 500

**Response (200):**
```json
{
  "total": 1250,
  "limit": 50,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440700",
      "product": {
        "sku": "BEV001",
        "name": "Organic Coffee"
      },
      "market": {
        "name": "Downtown Market"
      },
      "move_type": "out",
      "quantity": -5,
      "move_date": "2025-01-15T14:25:00Z"
    }
  ]
}
```

---

## 5. Sales Endpoints

### GET /sales
List sales transactions.

**Query Parameters:**
- `market_id` (optional): Filter by market
- `start_date` (optional)
- `end_date` (optional)
- `channel` (optional): `pos`, `online`, `mobile`, `manual`
- `limit` (optional): Default 20, max 100

**Response (200):**
```json
{
  "total": 1250,
  "limit": 20,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440800",
      "sale_number": "SO-2025-001",
      "market_id": "550e8400-e29b-41d4-a716-446655440001",
      "sale_date": "2025-01-15T14:25:00Z",
      "channel": "pos",
      "total_amount": 30.01,
      "item_count": 3
    }
  ]
}
```

### GET /sales/{id}
Get sale details.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440800",
  "sale_number": "SO-2025-001",
  "market_id": "550e8400-e29b-41d4-a716-446655440001",
  "sale_date": "2025-01-15T14:25:00Z",
  "channel": "pos",
  "total_amount": 30.01,
  "items": [
    {
      "product_id": "550e8400-e29b-41d4-a716-446655440100",
      "product_name": "Organic Coffee",
      "quantity": 2,
      "unit_price": 5.99,
      "total_price": 11.98
    }
  ]
}
```

### GET /sales/summary
Get sales summary statistics.

**Query Parameters:**
- `market_id` (optional): Filter by market
- `period` (required): `today`, `this_week`, `this_month`

**Response (200):**
```json
{
  "period": "this_week",
  "summary": {
    "total_revenue": 8750.00,
    "total_transactions": 315,
    "average_ticket": 27.78,
    "gross_profit": 2625.00
  },
  "by_day": [
    {
      "date": "2025-01-15",
      "revenue": 1250.50,
      "transactions": 45
    }
  ]
}
```

---

## 6. Upload Endpoints

### POST /uploads
Upload Odoo report file.

**Request (multipart/form-data):**
```
file: <binary>
market_id: "550e8400-e29b-41d4-a716-446655440001"
file_type: "odoo_stock_report"
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440900",
  "original_filename": "stock_report_2025-01-15.xlsx",
  "file_type": "odoo_stock_report",
  "file_size_bytes": 45678,
  "status": "pending",
  "created_at": "2025-01-15T14:30:00Z"
}
```

### GET /uploads
List uploaded files.

**Response (200):**
```json
{
  "total": 45,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440900",
      "original_filename": "stock_report_2025-01-15.xlsx",
      "file_type": "odoo_stock_report",
      "status": "completed",
      "records_processed": 450,
      "records_failed": 0,
      "created_at": "2025-01-15T14:30:00Z"
    }
  ]
}
```

### GET /uploads/{id}
Get upload details.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440900",
  "original_filename": "stock_report_2025-01-15.xlsx",
  "status": "completed",
  "records_processed": 450,
  "records_failed": 0,
  "processing_error": null,
  "created_at": "2025-01-15T14:30:00Z"
}
```

### GET /uploads/{id}/status
Get processing status.

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440900",
  "status": "processing",
  "progress_percent": 65,
  "records_processed": 292,
  "records_total": 450
}
```

### DELETE /uploads/{id}
Delete uploaded file.

**Response (204):** No content

---

## 7. Analytics Endpoints

### GET /analytics/insights
Get AI-generated insights.

**Query Parameters:**
- `market_id` (optional): Filter by market
- `severity` (optional): `info`, `low`, `medium`, `high`, `critical`
- `limit` (optional): Default 5, max 20

**Response (200):**
```json
{
  "generated_at": "2025-01-15T14:30:00Z",
  "total_insights": 12,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655441000",
      "rank": 1,
      "title": "Stockout Risk: Green Tea",
      "description": "Green Tea is projected to stockout in 2 days based on current sales velocity",
      "severity": "high",
      "category": "inventory",
      "metrics": {
        "product_id": "550e8400-e29b-41d4-a716-446655440102",
        "current_stock": 8,
        "days_remaining": 1.8
      },
      "recommendations": [
        {
          "action": "urgent_reorder",
          "suggested_quantity": 100
        }
      ],
      "created_at": "2025-01-15T14:00:00Z"
    }
  ]
}
```

### GET /analytics/trends
Get trend analysis.

**Query Parameters:**
- `market_id` (optional)
- `metric` (required): `revenue`, `transactions`
- `period` (required): `7d`, `30d`, `90d`

**Response (200):**
```json
{
  "metric": "revenue",
  "period": "30d",
  "trend": {
    "direction": "up",
    "change_percent": 9.4
  },
  "data_points": [
    {
      "date": "2025-01-15",
      "value": 1250.50
    }
  ]
}
```

### GET /analytics/forecast
Get demand forecast.

**Query Parameters:**
- `product_id` (required)
- `market_id` (optional)
- `days` (optional): Default 30

**Response (200):**
```json
{
  "product_id": "550e8400-e29b-41d4-a716-446655440100",
  "forecast_generated_at": "2025-01-15T14:30:00Z",
  "forecast": [
    {
      "date": "2025-01-16",
      "predicted_demand": 5.2,
      "confidence_interval_lower": 3.8,
      "confidence_interval_upper": 6.6
    }
  ]
}
```

### GET /analytics/dashboard
Get dashboard summary data.

**Query Parameters:**
- `market_id` (optional)

**Response (200):**
```json
{
  "generated_at": "2025-01-15T14:30:00Z",
  "summary": {
    "active_insights": 12,
    "critical_issues": 2,
    "warnings": 5
  },
  "top_insights": [
    {
      "id": "550e8400-e29b-41d4-a716-446655441000",
      "title": "Stockout Risk: Green Tea",
      "severity": "high"
    }
  ],
  "key_metrics": {
    "revenue_today": 1250.50,
    "inventory_value": 45000.00,
    "low_stock_count": 12,
    "stockout_count": 3
  }
}
```

---

## 8. Chatbot Endpoints

### POST /chat/sessions
Create a new chat session.

**Request:**
```json
{
  "title": "Inventory Analysis",
  "market_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655442000",
  "title": "Inventory Analysis",
  "operator_id": "550e8400-e29b-41d4-a716-446655440000",
  "market_id": "550e8400-e29b-41d4-a716-446655440001",
  "message_count": 0,
  "started_at": "2025-01-15T14:30:00Z"
}
```

### GET /chat/sessions
List chat sessions.

**Response (200):**
```json
{
  "total": 15,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655442000",
      "title": "Inventory Analysis",
      "message_count": 12,
      "last_activity_at": "2025-01-15T14:45:00Z"
    }
  ]
}
```

### DELETE /chat/sessions/{id}
Delete chat session.

**Response (204):** No content

### POST /chat/sessions/{id}/messages
Send a message to the chatbot.

**Request:**
```json
{
  "content": "What are my top 5 selling products this week?"
}
```

**Response (200):**
```json
{
  "message": {
    "id": "550e8400-e29b-41d4-a716-446655442001",
    "role": "user",
    "content": "What are my top 5 selling products this week?",
    "created_at": "2025-01-15T14:46:00Z"
  },
  "response": {
    "id": "550e8400-e29b-41d4-a716-446655442002",
    "role": "assistant",
    "content": "Based on your sales data, here are your top 5 selling products:\n\n1. Organic Coffee - 45 units sold\n2. Green Tea - 38 units sold\n...",
    "model": "gpt-4",
    "created_at": "2025-01-15T14:46:02Z"
  }
}
```

### GET /chat/sessions/{id}/messages
Get message history.

**Response (200):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655442000",
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655442001",
      "role": "user",
      "content": "What are my top 5 selling products?",
      "created_at": "2025-01-15T14:46:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655442002",
      "role": "assistant",
      "content": "Based on your sales data...",
      "created_at": "2025-01-15T14:46:02Z"
    }
  ]
}
```

### POST /chat/sessions/{id}/feedback
Submit feedback on the session.

**Request:**
```json
{
  "rating": 5,
  "feedback": "Very helpful!"
}
```

---

## 9. MCP Server Endpoints

### GET /mcp/tools
List available MCP tools.

**Response (200):**
```json
{
  "tools": [
    {
      "name": "query_inventory",
      "description": "Query current inventory levels",
      "input_schema": {
        "market_id": {"type": "string"},
        "status": {"type": "string"}
      }
    },
    {
      "name": "analyze_sales",
      "description": "Analyze sales trends",
      "input_schema": {
        "date_range": {"type": "object"},
        "group_by": {"type": "string"}
      }
    }
  ]
}
```

### POST /mcp/tools/{tool_name}/execute
Execute a specific MCP tool.

**Request:**
```json
{
  "input": {
    "market_id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "low_stock"
  }
}
```

**Response (200):**
```json
{
  "tool": "query_inventory",
  "success": true,
  "output": {
    "total": 12,
    "items": []
  }
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limits

| Endpoint Group | Limit | Window |
|----------------|-------|--------|
| Authentication | 10 | per minute |
| General API | 100 | per minute |
| Uploads | 5 | per minute |
| Chat/MCP | 30 | per minute |
| Analytics | 20 | per minute |

---

*Last Updated: January 2025*
*Version: 1.1 (WebSocket Removed)*