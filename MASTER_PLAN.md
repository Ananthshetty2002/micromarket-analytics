requirement\MASTER_PLAN.md
```

# Micromarket Operator Platform - Master Plan

## Executive Summary

This document consolidates the complete planning documentation for the Micromarket Operator Platform - a lightweight, AI-powered inventory and sales management system designed for small-scale micromarket operators (<100 users).

**Platform Goals:**
- Simplify inventory management through automated Odoo report processing
- Provide actionable insights via AI-powered analytics
- Enable natural language queries through conversational AI
- Support data-driven decision making for micromarket operators

---

## 1. Tech Stack

### Overview
Simplified, startup-friendly stack optimized for rapid development and single-server deployment.

### Frontend Stack
| Technology | Purpose |
|------------|---------|
| React 18+ | UI framework |
| TypeScript | Type safety |
| Vite | Build tool |
| Tailwind CSS | Styling |
| shadcn/ui | Component library |
| Recharts | Data visualization |
| Zustand | State management |
| TanStack Query | Server state management |
| Socket.io-client | Real-time updates |

### Backend Stack
| Technology | Purpose |
|------------|---------|
| FastAPI | API framework |
| SQLAlchemy 2.0 | ORM |
| Pydantic | Data validation |
| Celery | Background tasks |
| Pandas | Data processing |
| OpenAI | LLM integration |
| Pytest | Testing |

### Database & Infrastructure
| Technology | Purpose |
|------------|---------|
| PostgreSQL 16 | Primary database |
| Redis 7 | Caching & message broker |
| Nginx | Reverse proxy |
| Docker Compose | Containerization |
| Local filesystem | File storage |

---

## 2. Database Schema

### Core Entities

#### Operators (Users)
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| email | String | Unique identifier |
| name | String | Display name |
| role | Enum | admin/manager/analyst/viewer |
| preferences | JSON | UI settings, timezone |
| last_login | Timestamp | Activity tracking |

#### Micromarkets
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| operator_id | UUID | Owner reference |
| name | String | Location name |
| code | String | Unique code |
| location | JSON | Lat/long coordinates |
| address | String | Street address |
| city | String | City |
| state | String | State/Province |
| country | String | Country |
| timezone | String | Timezone |
| status | Enum | active/inactive/maintenance |

#### Products
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sku | String | Stock keeping unit |
| barcode | String | EAN/UPC code |
| name | String | Product name |
| description | Text | Description |
| category_id | UUID | Category reference |
| unit_price | Decimal | Selling price |
| cost_price | Decimal | Cost price |
| currency | String | Currency code |
| is_active | Boolean | Active status |

#### Inventory
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| product_id | UUID | Product reference |
| market_id | UUID | Market reference |
| quantity_on_hand | Integer | Physical stock |
| quantity_reserved | Integer | Reserved quantity |
| quantity_available | Integer | Available for sale |
| reorder_point | Integer | Reorder threshold |
| max_stock_level | Integer | Maximum stock |
| status | Enum | in_stock/low_stock/out_of_stock |

#### Sales
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sale_number | String | Transaction ID |
| market_id | UUID | Market reference |
| sale_date | Timestamp | Transaction time |
| channel | Enum | pos/online/manual |
| total_amount | Decimal | Total value |
| item_count | Integer | Number of items |

#### Sale Items
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| sale_id | UUID | Sale reference |
| product_id | UUID | Product reference |
| quantity | Integer | Units sold |
| unit_price | Decimal | Price per unit |
| total_price | Decimal | Line total |
| cost_price | Decimal | Cost per unit |

#### Insights
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| market_id | UUID | Market reference |
| type | Enum | stockout_risk/low_stock/overstock/trend |
| severity | Enum | critical/warning/info |
| title | String | Short description |
| description | Text | Detailed explanation |
| metrics | JSON | Supporting data |
| recommendations | JSON | Suggested actions |
| is_dismissed | Boolean | User dismissed |
| generated_at | Timestamp | Creation time |

#### Chat Sessions
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| operator_id | UUID | User reference |
| market_id | UUID | Market context |
| title | String | Session title |
| message_count | Integer | Number of messages |
| started_at | Timestamp | Creation time |
| last_activity_at | Timestamp | Last update |

### Entity Relationships
```
Operator ──< Micromarket ──< Inventory >── Product
   │              │              │
   │              └──< Sales ──< Sale Items
   │                     │
   └──< Chat Session    └──< Insights
```

---

## 3. API Endpoints

### Authentication (`/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Authenticate |
| POST | `/auth/refresh` | Refresh token |
| POST | `/auth/logout` | End session |
| GET | `/auth/me` | Get current user |
| PUT | `/auth/me` | Update profile |

### Micromarkets (`/markets`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/markets` | List markets |
| POST | `/markets` | Create market |
| GET | `/markets/{id}` | Get market details |
| PUT | `/markets/{id}` | Update market |
| DELETE | `/markets/{id}` | Delete market |
| GET | `/markets/{id}/stats` | Market statistics |
| GET | `/markets/{id}/inventory` | Market inventory |

### Products (`/products`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List products |
| POST | `/products` | Create product |
| GET | `/products/{id}` | Get product details |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |
| GET | `/products/{id}/inventory` | Product inventory across markets |
| GET | `/products/search` | Search products |

### Inventory (`/inventory`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory` | List inventory |
| GET | `/inventory/low-stock` | Low stock alerts |
| GET | `/inventory/overstock` | Overstock items |
| GET | `/inventory/stockouts` | Out of stock items |
| POST | `/inventory/adjust` | Adjust stock levels |
| GET | `/inventory/movements` | Stock movement history |

### Sales (`/sales`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sales` | List sales |
| GET | `/sales/{id}` | Get sale details |
| GET | `/sales/summary` | Sales summary/report |

### Uploads (`/uploads`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/uploads` | Upload file |
| GET | `/uploads` | List uploads |
| GET | `/uploads/{id}` | Get upload details |
| GET | `/uploads/{id}/status` | Check processing status |
| DELETE | `/uploads/{id}` | Delete upload |

### Analytics (`/analytics`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/insights` | Get AI insights |
| GET | `/analytics/trends` | Trend analysis |
| GET | `/analytics/forecast` | Demand forecasting |
| GET | `/analytics/dashboard` | Dashboard data |

### Chatbot (`/chat`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/sessions` | Create chat session |
| GET | `/chat/sessions` | List sessions |
| DELETE | `/chat/sessions/{id}` | Delete session |
| POST | `/chat/sessions/{id}/messages` | Send message |
| GET | `/chat/sessions/{id}/messages` | Get messages |
| POST | `/chat/sessions/{id}/feedback` | Rate response |

### MCP Server (`/mcp`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mcp/tools` | List available tools |
| POST | `/mcp/tools/{tool_name}/execute` | Execute tool |

---

## 4. Data Flows

### Report Upload Flow
```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  User    │────►│  Upload API │────►│  Validation  │────►│  Local       │
│  (Web)   │     │  (FastAPI)  │     │  (Schema)    │     │  Storage     │
└──────────┘     └─────────────┘     └──────────────┘     └─────┬────────┘
                                                                │
┌──────────┐     ┌─────────────┐     ┌──────────────┐         │
│ Database │◄────│  Processor  │◄────│  Background  │◄────────┘
│(PostgreSQL)   │  (Celery)   │     │  Queue       │
└──────────┘     └─────────────┘     └──────────────┘
```

### Dashboard Data Flow
```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  User    │────►│  Dashboard  │────►│  Analytics   │────►│  PostgreSQL  │
│ Request  │     │  API        │     │  Engine      │     │  Database    │
└──────────┘     └─────────────┘     └──────┬───────┘     └─────────────┘
                                            │
                                     ┌──────┴───────┐
                                     │  Redis Cache │
                                     └──────────────┘
```

### Chatbot MCP Flow
```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  User    │────►│  Chat API   │────►│  MCP Server  │────►│  LLM        │
│  Query   │     │             │     │  (Context)   │     │  (OpenAI)   │
└──────────┘     └─────────────┘     └──────┬───────┘     └──────┬──────┘
                                            │                    │
                                     ┌──────┴───────┐     ┌──────┴───────┐
                                     │  Database    │◄────│  Tool Exec   │
                                     │  (PostgreSQL)│     │  (SQL/Python)│
                                     └──────────────┘     └──────────────┘
```

### Real-time Updates Flow
```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────┐
│  Background  │────►│  Redis      │────►│  WebSocket   │────►│  Frontend│
│  Worker      │     │  Pub/Sub    │     │  Server      │     │  (React) │
└──────────────┘     └─────────────┘     └──────────────┘     └──────────┘
```

---

## 5. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-3)
**Goal:** Get basic platform running with Docker

#### Week 1: Project Setup & Core Infrastructure
- [ ] Repository setup with monorepo structure
- [ ] Docker Compose development environment
- [ ] PostgreSQL database with basic migrations
- [ ] FastAPI project scaffolding
- [ ] JWT authentication (simple, no OAuth)
- [ ] React frontend with Vite
- [ ] Tailwind CSS + shadcn/ui setup

**Deliverables:**
- `docker-compose up` starts full stack
- Login/register working
- Database tables created

#### Week 2: Data Models & File Upload
- [ ] Core SQLAlchemy models (operators, markets, products, inventory, sales)
- [ ] File upload endpoint (local storage)
- [ ] CSV/Excel parser for Odoo Stock Report
- [ ] Basic data validation
- [ ] Simple background processing (threading for start)

**Deliverables:**
- Upload Odoo reports via UI
- Data imports to database
- View imported products and inventory

#### Week 3: Basic Dashboard
- [ ] Dashboard layout with sidebar
- [ ] Key metric cards (total products, stock value, low stock)
- [ ] Inventory list with filtering
- [ ] Market switcher
- [ ] Mobile-responsive design

**Deliverables:**
- Working dashboard showing imported data
- Can switch between markets
- Basic visualizations

---

### Phase 2: Analytics & Insights (Weeks 4-6)
**Goal:** Add smart insights and trend detection

#### Week 4: Analytics Engine
- [ ] Simple trend analysis (SQL queries + pandas)
- [ ] Stockout risk detection
- [ ] Low stock alerts
- [ ] Basic sales summaries

**Deliverables:**
- Automated insights generated after upload
- API endpoints for analytics

#### Week 5: Top 5 Insights Dashboard
- [ ] Priority scoring for insights
- [ ] Dashboard "Top 5" component
- [ ] Insight detail views
- [ ] Dismiss/snooze functionality

**Deliverables:**
- Users see top 5 actionable items on dashboard
- Can interact with insights

#### Week 6: Forecasting & Alerts
- [ ] Simple forecasting (moving averages)
- [ ] Email alerts for critical issues
- [ ] Report exports (CSV/Excel)

**Deliverables:**
- Basic demand forecasting
- Email notifications setup

---

### Phase 3: AI Chatbot (Weeks 7-9)
**Goal:** Add conversational interface

#### Week 7: MCP Server Setup
- [ ] MCP server implementation (Python)
- [ ] Database query tools (3-4 basic tools)
- [ ] Context management

**Deliverables:**
- MCP server running
- Tools can query inventory and sales

#### Week 8: LLM Integration
- [ ] OpenAI API integration
- [ ] Prompt templates
- [ ] Response streaming
- [ ] Chat API endpoints

**Deliverables:**
- Chat completions working
- Context-aware responses

#### Week 9: Chat UI
- [ ] Chat interface component
- [ ] Message history
- [ ] Suggested queries
- [ ] Session management

**Deliverables:**
- Full chatbot UI
- Can ask about inventory, sales, trends

---

### Phase 4: Polish & Production (Weeks 10-12)
**Goal:** Production-ready deployment

#### Week 10: Performance & Security
- [ ] Database query optimization
- [ ] Basic caching (Redis)
- [ ] Input validation hardening
- [ ] API rate limiting

**Deliverables:**
- <200ms API response times
- Security basics in place

#### Week 11: Monitoring & Logging
- [ ] Application logging
- [ ] Error tracking (Sentry)
- [ ] Health check endpoints
- [ ] Simple metrics dashboard

**Deliverables:**
- Can monitor application health
- Errors tracked and alerted

#### Week 12: Deployment & Documentation
- [ ] Production Docker Compose setup
- [ ] Environment configuration
- [ ] User documentation
- [ ] API documentation (OpenAPI)

**Deliverables:**
- Production deployment guide
- Complete documentation
- Ready for users

---

## 6. Deployment Architecture

### Simple Docker Compose Setup
```
┌─────────────────────────────────────┐
│           Docker Compose             │
│  ┌─────────────┐  ┌─────────────┐  │
│  │   Nginx     │  │   React     │  │
│  │   (Proxy)   │  │   Frontend  │  │
│  └──────┬──────┘  └─────────────┘  │
│         │                           │
│  ┌──────┴───────────────────────┐  │
│  │      FastAPI Backend         │  │
│  │  - API endpoints             │  │
│  │  - MCP Server                │  │
│  │  - File processing           │  │
│  └──────┬───────────────────────┘  │
│         │                           │
│  ┌──────┴──────┐  ┌─────────────┐  │
│  │ PostgreSQL  │  │    Redis    │  │
│  │  (Data)     │  │  (Cache)    │  │
│  └─────────────┘  └─────────────┘  │
│                                     │
│  ┌─────────────┐                    │
│  │ Local       │                    │
│  │ Storage     │                    │
│  │ (Uploads)   │                    │
│  └─────────────┘                    │
└─────────────────────────────────────┘
```

### Infrastructure Requirements

#### Single Server (Recommended for <100 users)
- **CPU:** 4 cores
- **RAM:** 8GB
- **Storage:** 100GB SSD
- **OS:** Ubuntu 22.04 LTS

#### Services
| Service | Resource Allocation |
|---------|-------------------|
| Nginx | Minimal (proxy only) |
| React Frontend | Static files (Nginx) |
| FastAPI Backend | 2 CPU, 4GB RAM |
| Celery Worker | 1 CPU, 2GB RAM |
| PostgreSQL | 1 CPU, 2GB RAM, 50GB storage |
| Redis | 512MB RAM |

---

## 7. Success Metrics

| Phase | Metric | Target |
|-------|--------|--------|
| Phase 1 | Upload to dashboard | < 5 minutes |
| Phase 2 | Insight generation | Automatic on upload |
| Phase 3 | Chat response time | < 3 seconds |
| Phase 4 | System uptime | 99% |

### Performance Targets
- API Response Time: < 200ms (p95)
- Page Load Time: < 2 seconds
- File Processing: < 1 minute per 10,000 records
- Concurrent Users: 100

---

## 8. Resource Requirements

### Team
| Role | Count | Time |
|------|-------|------|
| Full-Stack Developer | 1-2 | Full-time |
| DevOps/Backend | 1 | Part-time |

### External Services
| Service | Purpose | Cost Level |
|---------|---------|------------|
| OpenAI API | LLM for chatbot | Usage-based |
| SendGrid/AWS SES | Email notifications | Free tier |
| Sentry | Error tracking | Free tier |

---

## 9. File Structure

```
micromarket-platform/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── store/
│   ├── Dockerfile
│   └── package.json
├── nginx/
│   └── nginx.conf
└── uploads/
    └── (local file storage)
```

---

## 10. Future Considerations

### Post-Launch Enhancements
- [ ] Additional Odoo report type support
- [ ] Advanced forecasting models (ML-based)
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Integration with payment systems
- [ ] Advanced role-based access control
- [ ] Kubernetes deployment for scaling

### Scaling Path
1. **Current:** Single server, Docker Compose
2. **Growth:** Separate application and database servers
3. **Scale:** Load balancer + multiple API instances
4. **Enterprise:** Kubernetes cluster with auto-scaling

---

## Document Information

| Property | Value |
|----------|-------|
| **Version** | 1.0 |
| **Last Updated** | February 2025 |
| **Status** | Planning Complete |
| **Author** | Platform Team |

---

*This master plan consolidates all planning documentation for the Micromarket Operator Platform. For detailed specifications, refer to individual documents: `tech_stack.md`, `database_schema.md`, `api_endpoints.md`, `data_flows.md`, `roadmap.md`.*