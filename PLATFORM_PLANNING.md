```

# Micromarket Operator Platform - Complete Planning Documentation

## Executive Summary

This document outlines the complete planning for a **Micromarket Operator Platform** designed to help operators manage multiple micromarkets efficiently. The platform combines AI-powered analytics with an intelligent chatbot interface, leveraging data from Odoo 18.0 Inventory Management System.

**Scope:** Startup phase architecture for up to 100 users with simple deployment and minimal infrastructure complexity.

---

## Table of Contents

1. [Platform Overview](#1-platform-overview)
2. [Architecture Design](#2-architecture-design)
3. [Database Schema Design](#3-database-schema-design)
4. [Data Flow Diagrams](#4-data-flow-diagrams)
5. [Tech Stack](#5-tech-stack)
6. [Implementation Phases](#6-implementation-phases)
7. [API Endpoints Specification](#7-api-endpoints-specification)
8. [Analysis Capabilities](#8-analysis-capabilities)
9. [Platform KPIs](#9-platform-kpis)
10. [Testing Strategy & KPIs](#10-testing-strategy--kpis)
11. [Roadmap](#11-roadmap)
12. [Risk Assessment](#12-risk-assessment)

---

## 1. Platform Overview

### 1.1 Purpose
Enable micromarket operators to:
- Monitor multiple locations from a single interface
- Identify critical trends and actionable items automatically
- Query business data using natural language via AI chatbot
- Make data-driven decisions based on Odoo 18.0 inventory reports

### 1.2 Core Features

#### Feature 1: Smart Dashboard (Top 5 Insights)
- **Trend Analysis**: Sales patterns, seasonal variations
- **Problem Detection**: Stockouts, overstock, expiring products
- **Actionable Items**: Restock alerts, reorder suggestions, pricing recommendations
- **Performance Metrics**: Revenue trends, profit margins by location

#### Feature 2: AI Chatbot (MCP-Based)
- Natural language queries about inventory, sales, and operations
- Context-aware responses using database access
- Report generation on-demand
- Predictive insights and recommendations

### 1.3 User Personas

| Persona | Role | Primary Needs |
|---------|------|-------------|
| Operations Manager | Oversees 5-20 micromarkets | Quick status overview, exception alerts |
| Inventory Analyst | Manages stock levels | Detailed stock analysis, reorder optimization |
| Field Operator | On-ground management | Quick lookups, task lists |

---

## 2. Architecture Design

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
│  ┌─────────────────┐          ┌─────────────────┐           │
│  │   Web Dashboard │          │  Admin Portal   │           │
│  │   (React/Vue)   │          │  (React/Vue)    │           │
│  └────────┬────────┘          └────────┬────────┘           │
└───────────┼────────────────────────────┼─────────────────────┘
            │                            │
            └────────────┬───────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                    SIMPLE API GATEWAY                        │
│              (Nginx / Node Script / Traefik)                 │
│              - Static file serving                           │
│              - Simple proxy to backend                       │
│              - SSL termination                               │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                      BACKEND SERVICE                         │
│                    (Python/FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  - Analytics Service                                  │   │
│  │  - Chatbot Service (MCP Server)                       │   │
│  │  - Upload Service                                     │   │
│  │  - Background Tasks (Celery/AsyncIO)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                        DATA LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ PostgreSQL  │  │    Redis    │  │  Local File Storage │  │
│  │ (Single)    │  │   (Cache)   │  │  (Reports/Uploads)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────┐
│                   EXTERNAL SERVICES                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Odoo 18.0  │  │  LLM API    │  │  Email Service      │  │
│  │  (Reports)  │  │  (OpenAI/   │  │  (SMTP/SendGrid)    │  │
│  │             │  │   Claude)   │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Deployment Architecture (Docker Compose)

```
┌─────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE STACK                      │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Frontend  │  │   Backend   │  │    Nginx Gateway    │  │
│  │    (Nginx)  │  │   (FastAPI) │  │   (Port 80/443)     │  │
│  │   Port 3000 │  │   Port 8000 │  │                     │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         └────────────────┼─────────────────────┘             │
│                          │                                   │
│  ┌───────────────────────┼───────────────────────────────┐   │
│  │                       │                               │   │
│  ▼                       ▼                               ▼   │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│ │  PostgreSQL  │  │    Redis     │  │  Local Storage   │   │
│ │   (Single)   │  │   (Cache)    │  │  ./data/uploads  │   │
│ │   Port 5432  │  │   Port 6379  │  │  ./data/reports  │   │
│ └──────────────┘  └──────────────┘  └──────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Celery Worker (Background Tasks)         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Component Architecture

#### Backend Service (Single FastAPI Application)
```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────┐  │
│  │  Analytics  │  │  Chatbot (MCP)  │  │
│  │  Router     │  │  Router         │  │
│  └─────────────┘  └─────────────────┘  │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │   Upload    │  │  Auth/Users     │  │
│  │  Router     │  │  Router         │  │
│  └─────────────┘  └─────────────────┘  │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────┐  │
│  │  Database   │  │  File Storage   │  │
│  │  Layer      │  │  Service        │  │
│  │  (SQLAlchemy)│  │  (Local FS)     │  │
│  └─────────────┘  └─────────────────┘  │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────┐  │
│  │  Background │  │  LLM Client     │  │
│  │  Tasks      │  │  (OpenAI)       │  │
│  │  (Celery)   │  │                 │  │
│  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
```

---

## 3. Database Schema Design

### 3.1 Entity Relationship Diagram

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│    operators    │◄──────┤  micromarkets    │       │   categories    │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)          │       │ id (PK)         │
│ email           │       │ operator_id (FK) │       │ name            │
│ name            │       │ name             │       │ description     │
│ role            │       │ location         │       │ parent_id (FK)  │
│ created_at      │       │ address          │       │ created_at      │
└─────────────────┘       │ timezone         │       └─────────────────┘
                          │ status           │                │
                          │ created_at       │                │
                          └──────────────────┘                │
                                   │                          │
                                   │                          │
                          ┌────────┴─────────┐                │
                          │                  │                │
                   ┌──────▼──────┐    ┌─────▼──────┐   ┌─────▼──────┐
                   │   products   │    │  inventory │   │  products   │
                   ├─────────────┤    ├────────────┤   │  categories │
                   │ id (PK)     │◄───┤ id (PK)    │   ├────────────┤
                   │ sku (UQ)    │    │ product_id │   │ product_id  │
                   │ name        │    │ market_id  │   │ category_id │
                   │ description │    │ quantity   │   └────────────┘
                   │ unit_price  │    │ min_stock  │
                   │ cost_price  │    │ max_stock  │
                   │ category_id │    │ reorder_pt │
                   │ supplier_id │    │ location   │
                   │ is_active   │    │ updated_at │
                   └─────────────┘    └────────────┘
                          │
                   ┌──────┴──────────┐
                   │                   │
            ┌─────▼──────┐     ┌──────▼─────┐
            │  suppliers  │     │   sales    │
            ├────────────┤     ├────────────┤
            │ id (PK)    │     │ id (PK)    │
            │ name       │     │ product_id │
            │ contact    │     │ market_id  │
            │ email      │     │ quantity   │
            │ phone      │     │ unit_price │
            │ address    │     │ total      │
            └────────────┘     │ sale_date  │
                               │ channel    │
                               └────────────┘
                                        │
                               ┌────────┴─────────┐
                               │                  │
                        ┌──────▼──────┐    ┌─────▼──────┐
                        │  stock_moves│    │  payments  │
                        ├─────────────┤    ├────────────┤
                        │ id (PK)     │    │ id (PK)    │
                        │ product_id  │    │ sale_id    │
                        │ market_id   │    │ amount     │
                        │ type        │    │ method     │
                        │ quantity    │    │ status     │
                        │ reference   │    │ paid_at    │
                        │ move_date   │    └────────────┘
                        │ source      │
                        │ destination │
                        └─────────────┘

┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│  uploaded_files │       │  analysis_results│       │  chat_sessions  │
├─────────────────┤       ├──────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)          │       │ id (PK)         │
│ filename        │       │ type             │       │ operator_id     │
│ file_type       │       │ market_id        │       │ started_at      │
│ file_size       │       │ generated_at     │       │ ended_at        │
│ upload_date     │       │ data (JSONB)     │       │ context_json    │
│ status          │       │ insights (JSONB) │       └─────────────────┘
│ parsed_data     │       │ priority         │                │
│ (JSONB)         │       │ status           │                │
│ operator_id     │       └──────────────────┘                │
│ market_id       │                                            │
└─────────────────┘                                   ┌──────▼──────┐
                                                        │chat_messages│
                                                        ├─────────────┤
                                                        │ id (PK)     │
                                                        │ session_id  │
                                                        │ role        │
                                                        │ content     │
                                                        │ timestamp   │
                                                        │ tokens_used │
                                                        └─────────────┘
```

### 3.2 Core Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| **operators** | Platform users | id, email, name, role, preferences |
| **micromarkets** | Store locations | id, operator_id, name, location, address, status |
| **categories** | Product hierarchy | id, name, parent_id |
| **suppliers** | Vendor information | id, name, contact, lead_time_days |
| **products** | Product catalog | id, sku, name, category_id, unit_price, cost_price, odoo_product_id |
| **inventory** | Current stock levels | id, product_id, market_id, quantity_on_hand, reorder_point |
| **stock_moves** | Inventory history | id, product_id, market_id, move_type, quantity, move_date |
| **sales** | Transaction headers | id, market_id, sale_date, total_amount, channel |
| **sale_items** | Transaction lines | id, sale_id, product_id, quantity, unit_price |
| **uploaded_files** | File upload tracking | id, filename, file_type, status, storage_path |
| **analysis_results** | AI insights | id, type, title, severity, metrics, recommendations |
| **chat_sessions** | Chat conversations | id, operator_id, context, message_count |
| **chat_messages** | Individual messages | id, session_id, role, content, tool_calls |

### 3.3 Odoo 18.0 Report Mapping

| Odoo Report | Target Tables | Key Mapping |
|-------------|---------------|-------------|
| **Stock Report** | products, inventory | SKU → products.sku, Quantity → inventory.quantity_on_hand |
| **Inventory Valuation** | products | Cost → products.cost_price |
| **Product Moves** | stock_moves | Direct field mapping |
| **Sales Analysis** | sales, sale_items | Order → sales, Lines → sale_items |
| **Partner List** | suppliers | Partner → suppliers |

---

## 4. Data Flow Diagrams

### 4.1 Report Upload Flow

```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  User    │────►│  Upload API │────►│  Validation  │────►│ Local Storage│
│          │     │             │     │              │     │ ./uploads/  │
└──────────┘     └─────────────┘     └──────────────┘     └──────┬──────┘
                                                                  │
                              ┌───────────────────────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │ Background   │
                       │ Task Queue   │
                       │ (Celery)     │
                       └───────┬──────┘
                               │
                               ▼
                       ┌──────────────┐
                       │   Parser     │
                       │   Engine     │
                       └───────┬──────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │ Products │    │ Inventory│    │  Sales   │
        │  Table   │    │  Table   │    │  Table   │
        └──────────┘    └──────────┘    └──────────┘
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                       ┌──────────────┐
                       │  Analytics   │
                       │   Trigger    │
                       └──────────────┘
```

### 4.2 Dashboard Data Flow

```
┌──────────┐     ┌─────────────┐     ┌─────────────────────────────┐
│  User    │────►│  Dashboard  │────►│      Analytics Engine         │
│ Request  │     │    API      │     │                               │
└──────────┘     └─────────────┘     │  ┌─────────┐  ┌──────────┐ │
                                      │  │  Trend  │  │ Anomaly  │ │
                                      │  │Analyzer │  │ Detector │ │
                                      │  └────┬────┘  └─────┬────┘ │
                                      │       │             │      │
                                      │       └──────┬──────┘      │
                                      │              │              │
                                      └──────────────┼──────────────┘
                                                     │
                              ┌──────────────────────┼──────────────┐
                              │                      │              │
                              ▼                      ▼              ▼
                        ┌──────────┐          ┌──────────┐   ┌──────────┐
                        │PostgreSQL│          │  Redis   │   │  Simple  │
                        │          │          │  (Cache) │   │  File    │
                        │          │          │          │   │  Cache   │
                        └──────────┘          └──────────┘   └──────────┘
                              │                      │              │
                              └──────────────────────┼──────────────┘
                                                     │
                                                     ▼
                                              ┌──────────────┐
                                              │  Top 5       │
                                              │  Insights    │
                                              │  Response    │
                                              └──────────────┘
```

### 4.3 Chatbot MCP Flow

```
┌──────────┐     ┌─────────────┐     ┌─────────────────────────────────┐
│  User    │────►│  Chat API   │────►│         MCP Server              │
│  Query   │     │             │     │                                 │
└──────────┘     └─────────────┘     │  ┌─────────────────────────┐   │
                                      │  │    Context Manager      │   │
                                      │  │  - Session state        │   │
                                      │  │  - Active markets       │   │
                                      │  │  - User permissions     │   │
                                      │  └─────────────────────────┘   │
                                      │              │                  │
                                      │              ▼                  │
                                      │  ┌─────────────────────────┐   │
                                      │  │    Intent Router        │   │
                                      │  │  - Query classification │   │
                                      │  │  - Tool selection       │   │
                                      │  └─────────────────────────┘   │
                                      │              │                  │
                                      └──────────────┼──────────────────┘
                                                     │
                              ┌──────────────────────┼──────────────────────┐
                              │                      │                      │
                              ▼                      ▼                      ▼
                        ┌──────────┐          ┌──────────┐          ┌──────────┐
                        │  DB Tool │          │ Calc Tool│          │ API Tool │
                        │          │          │          │          │          │
                        │ • Query  │          │ • Aggreg │          │ • Fetch  │
                        │ • Join   │          │ • Compute│          │ • Update │
                        │ • Filter │          │ • Stats  │          │ • Create │
                        └────┬─────┘          └────┬─────┘          └────┬─────┘
                             │                     │                     │
                             └─────────────────────┼─────────────────────┘
                                                   │
                                                   ▼
                                           ┌──────────────┐
                                           │  LLM Prompt  │
                                           │  Builder     │
                                           └──────┬───────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │   LLM API    │
                                           │(OpenAI/Claude)│
                                           └──────┬───────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │   Response   │
                                           │   Formatter  │
                                           └──────┬───────┘
                                                  │
                                                  ▼
                                           ┌──────────────┐
                                           │    User      │
                                           │   Response   │
                                           └──────────────┘
```

### 4.4 File Storage Structure

```
./data/
├── uploads/
│   ├── 2025/
│   │   ├── 01/
│   │   │   ├── 550e8400-e29b-41d4-a716-446655440900.xlsx
│   │   │   └── 550e8400-e29b-41d4-a716-446655440901.csv
│   │   └── 02/
│   └── raw/
│       └── {upload_id}/
│           └── original_filename.xlsx
├── reports/
│   ├── generated/
│   │   └── 550e8400-e29b-41d4-a716-446655441004.pdf
│   └── exports/
└── cache/
    └── analytics/
        └── dashboard_{market_id}_{date}.json
```

---

## 5. Tech Stack

### 5.1 Core Technologies

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend** | React | 18.x | UI Framework |
| | TypeScript | 5.x | Type Safety |
| | TanStack Query | 5.x | Data Fetching |
| | Recharts | 2.x | Data Visualization |
| | Tailwind CSS | 3.x | Styling |
| | shadcn/ui | Latest | Component Library |
| **Backend** | Python | 3.11+ | Primary Language |
| | FastAPI | 0.110+ | API Framework |
| | SQLAlchemy | 2.x | ORM |
| | Alembic | Latest | Migrations |
| | Celery | 5.x | Background Tasks |
| | Pandas | 2.x | Data Processing |
| **AI/ML** | LangChain | Latest | LLM Orchestration |
| | MCP SDK | Latest | Model Context Protocol |
| | OpenAI API | Latest | LLM Provider |
| | Prophet | Latest | Time Series Forecasting |
| **Database** | PostgreSQL | 16.x | Primary Database |
| | PostGIS | 3.x | Geospatial Data |
| | Redis | 7.x | Cache & Queue |
| **Infrastructure** | Docker | 24.x | Containerization |
| | Docker Compose | 2.x | Local Deployment |
| | Nginx | Latest | Gateway & Static Files |
| **Monitoring** | Prometheus | Latest | Metrics (optional) |
| | Grafana | Latest | Dashboards (optional) |

### 5.2 MCP (Model Context Protocol) Stack

```
┌─────────────────────────────────────────┐
│           MCP Client Layer              │
│      (React + MCP Client SDK)           │
│  - Session Management                   │
│  - Tool Discovery                       │
│  - Resource Access                      │
└─────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│           MCP Server Layer              │
│      (Python FastAPI Integration)       │
│  ┌─────────────────────────────────┐   │
│  │  Tools:                         │   │
│  │  • query_inventory              │   │
│  │  • analyze_sales                │   │
│  │  • get_forecast                 │   │
│  │  • calculate_metrics            │   │
│  ├─────────────────────────────────┤   │
│  │  Resources:                     │   │
│  │  • inventory://current          │   │
│  │  • sales://summary              │   │
│  │  • analytics://insights         │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 5.3 Development Tools

| Category | Tool | Purpose |
|----------|------|---------|
| IDE | VS Code | Development |
| API Testing | Postman / Hoppscotch | API Development |
| Database | pgAdmin / DBeaver | DB Management |
| Documentation | MkDocs | Docs Site |
| API Docs | OpenAPI/Swagger | API Documentation |

---

## 6. Implementation Phases

### Phase 1: Foundation (Weeks 1-4)

#### Sprint 1: Project Setup & Infrastructure (Week 1)
- [ ] Repository structure setup
- [ ] Docker Compose development environment
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] PostgreSQL database setup with migrations
- [ ] Basic FastAPI project structure
- [ ] JWT authentication system

**Deliverables:**
- Running development environment (`docker-compose up`)
- Authentication API endpoints
- Database schema v1 deployed

#### Sprint 2: Core Data Models & Upload
- [ ] Implement all database models
- [ ] File upload service (local storage)
- [ ] Basic Odoo report parsers (CSV/Excel)
- [ ] Data validation and transformation layer
- [ ] Background job processing (Celery)

**Deliverables:**
- File upload API
- Parser for 3 core Odoo reports
- Data ingestion pipeline

#### Sprint 3: Basic Dashboard
- [ ] React frontend setup
- [ ] Authentication UI
- [ ] Basic dashboard layout
- [ ] Data visualization components
- [ ] API integration with TanStack Query

**Deliverables:**
- Login/dashboard UI
- File upload interface
- Basic data display

### Phase 2: Analytics Engine (Weeks 5-8)

#### Sprint 4: Analytics Core
- [ ] Trend analysis algorithms
- [ ] Anomaly detection (statistical)
- [ ] Stock level analysis
- [ ] Sales pattern recognition
- [ ] Analysis results storage

**Deliverables:**
- Analytics service API
- 5 core analysis types
- Automated analysis triggers

#### Sprint 5: Smart Insights
- [ ] Top 5 insights generation
- [ ] Priority scoring algorithm
- [ ] Insight categorization
- [ ] Recommendation engine v1
- [ ] Dashboard insight cards

**Deliverables:**
- Insights API
- Dashboard with top 5 display
- Filtering and sorting

#### Sprint 6: Advanced Analytics
- [ ] Forecasting models (Prophet)
- [ ] Seasonal decomposition
- [ ] Market comparison tools
- [ ] Export capabilities

**Deliverables:**
- Forecasting API
- Comparison tools
- Report exports (PDF/Excel)

### Phase 3: AI Chatbot (Weeks 9-12)

#### Sprint 7: MCP Server Setup
- [ ] MCP server implementation
- [ ] Database tool definitions
- [ ] Query builder tools
- [ ] Context management

**Deliverables:**
- MCP server running
- 5+ database tools
- Tool documentation

#### Sprint 8: LLM Integration
- [ ] OpenAI/Anthropic API integration
- [ ] Prompt engineering
- [ ] Response formatting
- [ ] Token usage optimization

**Deliverables:**
- Chat completion API
- Basic chat interface
- Context-aware responses

#### Sprint 9: Chat UI & Features
- [ ] Chat interface design
- [ ] Message history
- [ ] Suggested queries
- [ ] Chat session management

**Deliverables:**
- Full chatbot UI
- Session persistence
- Mobile-responsive chat

#### Sprint 10: Advanced Chat Features
- [ ] Multi-turn conversations
- [ ] Context switching
- [ ] Visualization generation
- [ ] Report generation from chat

**Deliverables:**
- Advanced chat features
- Visualization in chat
- User feedback system

### Phase 4: Polish & Launch (Weeks 13-16)

#### Sprint 11: Performance & Security
- [ ] Database query optimization
- [ ] Caching strategy implementation
- [ ] Security audit
- [ ] API rate limiting

**Deliverables:**
- Optimized queries
- Redis caching layer
- Security hardening

#### Sprint 12: Documentation & Deployment
- [ ] User documentation
- [ ] API documentation
- [ ] Deployment scripts
- [ ] Production Docker Compose

**Deliverables:**
- Complete documentation
- Production-ready deployment
- Go-live support

---

## 7. API Endpoints Specification

### 7.1 Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new operator |
| POST | `/auth/login` | Authenticate user |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Invalidate tokens |
| GET | `/auth/me` | Get current user profile |
| PUT | `/auth/me` | Update user profile |

### 7.2 Micromarket Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/markets` | List all markets |
| POST | `/markets` | Create new market |
| GET | `/markets/{id}` | Get market details |
| PUT | `/markets/{id}` | Update market |
| DELETE | `/markets/{id}` | Delete market |
| GET | `/markets/{id}/stats` | Get market statistics |
| GET | `/markets/{id}/inventory` | Get market inventory |

### 7.3 Product Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all products |
| POST | `/products` | Create product |
| GET | `/products/{id}` | Get product details |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |
| GET | `/products/search` | Search products |

### 7.4 Inventory Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory` | Get inventory levels |
| GET | `/inventory/low-stock` | Get low stock items |
| GET | `/inventory/overstock` | Get overstock items |
| GET | `/inventory/stockouts` | Get stockout items |
| POST | `/inventory/adjust` | Create adjustment |

### 7.5 Sales Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sales` | List sales |
| GET | `/sales/{id}` | Get sale details |
| GET | `/sales/summary` | Get sales summary |
| GET | `/sales/trends` | Get sales trends |

### 7.6 Upload Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/uploads` | Upload file |
| GET | `/uploads` | List uploads |
| GET | `/uploads/{id}` | Get upload status |
| DELETE | `/uploads/{id}` | Delete upload |
| POST | `/uploads/odoo/stock-report` | Upload stock report |
| POST | `/uploads/odoo/sales-report` | Upload sales report |

### 7.7 Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/insights` | Get AI insights |
| GET | `/analytics/trends` | Get trends |
| GET | `/analytics/forecast` | Get forecasts |
| GET | `/analytics/dashboard` | Get dashboard data |
| POST | `/analytics/generate` | Trigger analysis |

### 7.8 Chatbot Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat/sessions` | Create session |
| GET | `/chat/sessions` | List sessions |
| GET | `/chat/sessions/{id}` | Get session |
| DELETE | `/chat/sessions/{id}` | Delete session |
| POST | `/chat/sessions/{id}/messages` | Send message |
| GET | `/chat/sessions/{id}/messages` | Get messages |
| POST | `/chat/sessions/{id}/feedback` | Submit feedback |

### 7.9 MCP Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mcp/tools` | List MCP tools |
| POST | `/mcp/tools/{name}/execute` | Execute tool |
| GET | `/mcp/resources` | List resources |
| GET | `/mcp/resources/{uri}` | Get resource |

---

## 8. Analysis Capabilities

### 8.1 Inventory Analysis

| Analysis Type | Description | Output |
|--------------|-------------|--------|
| **Stockout Prediction** | Predict products likely to stockout | Risk score, days until stockout |
| **Overstock Detection** | Identify slow-moving excess inventory | Excess quantity, holding cost |
| **Reorder Optimization** | Calculate optimal reorder points | Reorder point, suggested quantity |
| **ABC Analysis** | Classify products by value | A/B/C classification |
| **Shelf Life Analysis** | Track expiration dates | Expiry alerts |

### 8.2 Sales Analysis

| Analysis Type | Description | Output |
|--------------|-------------|--------|
| **Trend Analysis** | Identify sales patterns | Trend direction, growth rate |
| **Seasonal Analysis** | Detect seasonal patterns | Peak days/hours, seasonality index |
| **Product Performance** | Rank products by metrics | Top sellers, slow movers |
| **Market Comparison** | Compare across markets | Benchmarking, variance analysis |

### 8.3 AI-Powered Insights

| Insight Category | Capabilities |
|-----------------|--------------|
| **Natural Language Summaries** | Convert metrics to narrative |
| **Anomaly Explanation** | Explain why anomalies occurred |
| **Recommendation Generation** | Suggest specific actions |
| **What-If Analysis** | Simulate scenarios |

---

## 9. Platform KPIs

### 9.1 Business KPIs

| KPI | Target |
|-----|--------|
| Time to Insight | < 5 minutes |
| Forecast Accuracy | > 75% |
| User Adoption | > 80% DAU/MAU |

### 9.2 Technical KPIs

| KPI | Target |
|-----|--------|
| API Response Time (p95) | < 500ms |
| Dashboard Load Time | < 3 seconds |
| Chat Response Time | < 5 seconds |
| System Availability | 99.5% |

### 9.3 AI/ML KPIs

| KPI | Target |
|-----|--------|
| Chat Satisfaction | > 4.0/5 |
| Tool Selection Accuracy | > 90% |
| Token Efficiency | < 2000 tokens/query |

---

## 10. Testing Strategy & KPIs

### 10.1 Testing Pyramid

- **Unit Tests**: 70% coverage
- **Integration Tests**: API and DB testing
- **E2E Tests**: Critical user journeys

### 10.2 Testing Tools

| Category | Tool |
|----------|------|
| Unit Testing | pytest |
| E2E Testing | Playwright |
| Load Testing | Locust |
| API Testing | Postman |

### 10.3 Testing KPIs

| Metric | Target |
|--------|--------|
| Code Coverage | > 70% |
| Test Execution Time | < 10 min |
| Bug Escape Rate | < 10% |

---

## 11. Roadmap

### Q1 2025 (Months 1-3)
- Foundation architecture
- Database implementation
- File upload and parsing
- Basic dashboard
- User authentication

### Q2 2025 (Months 4-6)
- Analytics engine
- Top 5 insights
- MCP server
- Basic chatbot
- Beta launch

### Post-Launch
- Mobile responsiveness improvements
- Advanced forecasting
- Additional ERP integrations
- Performance optimizations

---

## 12. Risk Assessment

### 12.1 Technical Risks

| Risk | Probability | Mitigation |
|------|-------------|------------|
| LLM API changes | Medium | Abstract LLM layer |
| Data quality issues | High | Validation pipeline |
| Performance at scale | Low | Simple architecture, easy to scale |

### 12.2 Business Risks

| Risk | Probability | Mitigation |
|------|-------------|------------|
| User adoption | Medium | UX focus, training |
| Integration complexity | Medium | Flexible parser |

---

## Appendix A: Docker Compose Configuration

```yaml
version: '3.8'

services:
  # API Gateway / Static File Server
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
      - ./data/uploads:/var/www/uploads
    depends_on:
      - backend

  # Backend API
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/operatordash
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    depends_on:
      - postgres
      - redis

  # Background Task Worker
  celery:
    build: ./backend
    command: celery -A app.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/operatordash
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data:/app/data
    depends_on:
      - postgres
      - redis

  # Database
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=operatordash
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  # Cache & Queue
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## Appendix B: Simple Nginx Configuration

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    
    # Frontend static files
    server {
        listen 80;
        server_name localhost;
        
        # API proxy
        location /api/ {
            proxy_pass http://backend:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # WebSocket support
        location /ws/ {
            proxy_pass http://backend:8000/ws/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        # Static frontend
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }
        
        # Uploaded files
        location /uploads/ {
            alias /var/www/uploads/;
            autoindex off;
        }
    }
}
```

---

## Document Information

| Property | Value |
|----------|-------|
| **Version** | 1.0 (Simplified) |
| **Last Updated** | January 2025 |
| **Target Users** | < 100 operators |
| **Deployment** | Docker Compose |
| **Status** | Draft |

---

*This is a simplified architecture for startup phase. Scale to Kubernetes/cloud when user base grows beyond 100 active users.*