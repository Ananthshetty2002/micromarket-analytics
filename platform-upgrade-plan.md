# Platform Upgrade & Comparison Plan
## Stockout Analysis Platform → Micromarket Business Intelligence Platform

---

## Executive Summary

This document provides a comprehensive comparison between the **existing Stockout Analysis Platform** and the **new Micromarket Business Intelligence Platform** requirements, along with a detailed migration and upgrade plan.

**Current State:** Stockout-focused platform with 3-pillar analytics (Detection, Root Cause, Impact)
**Target State:** Comprehensive business intelligence platform with 4 analysis sections, enhanced AI, and operator-friendly interface

---

## 1. Platform Comparison Matrix

| Feature | Existing Platform | New Requirements | Gap Analysis |
|---------|------------------|------------------|--------------|
| **Primary Focus** | Stockout detection & analysis | Comprehensive business intelligence | Expand scope beyond stockouts |
| **Analysis Sections** | 3 Pillars (Detection, Root Cause, Impact) | 4 Sections (Sales, Inventory, Location, Business Type) | Add Sales & Business Type sections |
| **Report Types** | 5 reports (Stock Analysis, Where Sold, Product Rank, Product Transaction, Sales By Product) | 7+ reports (expanded Sales, Inventory, POS, Accounting) | Add POS & Accounting reports |
| **Database** | SQLite | PostgreSQL | Migration required |
| **Frontend** | Streamlit | Next.js + React | Complete rewrite |
| **AI Integration** | OpenRouter (Kimi K2.5) | MCP Server + LLM | Architecture change |
| **Interface Design** | Basic Streamlit UI | Operator-friendly with section switchers | Major UI/UX overhaul |
| **API Integration** | File upload only | File upload + Scheduled API sync | Add automated sync |
| **Mobile Support** | Limited | PWA with offline support | Build mobile experience |
| **Reporting** | Basic export | Scheduled reports, email delivery | Enhance reporting engine |

---

## 2. Detailed Gap Analysis

### 2.1 Architecture Changes

```
CURRENT ARCHITECTURE (Streamlit + FastAPI + SQLite)
┌─────────────────────────────────────────┐
│  Streamlit Frontend                     │
│  - Basic widgets                        │
│  - Limited interactivity                │
│  - No URL routing                       │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  FastAPI Backend                        │
│  - REST endpoints                       │
│  - File upload handlers                 │
│  - Basic LLM integration                │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  SQLite Database                        │
│  - 6 core tables                        │
│  - Single file limitation               │
└─────────────────────────────────────────┘

TARGET ARCHITECTURE (Next.js + FastAPI/Fastify + PostgreSQL)
┌─────────────────────────────────────────┐
│  Next.js 14 Frontend                    │
│  - App Router with SSR                  │
│  - Analysis switcher component          │
│  - URL-based routing                    │
│  - PWA capabilities                     │
│  - Tailwind + Headless UI               │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  API Gateway + BFF Layer                │
│  - Authentication (JWT)                 │
│  - Rate limiting                        │
│  - Request routing                      │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Business Logic Layer                   │
│  - 4 analysis engines                   │
│  - MCP Server integration               │
│  - Report scheduler                     │
│  - Data transformation                  │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  Data Layer                             │
│  - PostgreSQL (primary)                 │
│  - Redis (cache/queue)                  │
│  - Vector DB (AI context)               │
└─────────────────────────────────────────┘
```

### 2.2 Database Migration Requirements

| Current Table | Action | New Structure |
|---------------|--------|---------------|
| `stock_analysis_records` | Extend | Add `inventory_snapshots` with more fields |
| `where_sold_records` | Merge into | `sales_transactions` + location analytics |
| `product_rank_records` | Extend | Part of analytics engine, not standalone table |
| `product_sales_reports` | Rename/Extend | `sales_daily_summary` + detailed transactions |
| `product_transactions` | Extend | Add movement tracking, transfer types |
| `daily_inventory_metrics` | Extend | Add velocity, alerts, predictions |
| **New Tables Needed** | Create | `users`, `locations`, `business_types`, `businesses`, `categories`, `api_connections`, `sync_jobs`, `saved_analyses`, `generated_reports`, `chat_conversations`, `chat_messages`, `ai_context_cache` |

### 2.3 Analysis Section Transformation

#### Current: 3-Pillar Framework
1. **Pillar 1: Detection** (Where Sold) → Network vs Local detection
2. **Pillar 2: Root Cause** (Ghost Inventory) → Warehouse vs Market comparison
3. **Pillar 3: Impact** (Rank Priority) → Prioritization based on sales velocity

#### Target: 4-Section Framework
1. **Sales Analysis** ← *NEW SECTION*
   - Overview, Trends, Product Performance, Comparison
   - Requires: Sales transaction data, revenue metrics
   
2. **Inventory Analysis** ← *EVOLVED FROM Pillars 1 & 2*
   - Stock Levels ← *From Pillar 1*
   - Movement Analysis ← *From transactions*
   - Alerts ← *Enhanced from current*
   - Valuation ← *NEW*
   - Reorder Points ← *NEW*
   
3. **Location Analysis** ← *EXPANDED FROM Where Sold*
   - Compare Locations ← *Enhanced Pillar 1*
   - Heatmap Visualization ← *NEW*
   - Top Performers ← *NEW*
   - Location Details ← *NEW*
   - Trends ← *NEW*
   
4. **Business Type Analysis** ← *NEW SECTION*
   - Category Mix ← *NEW*
   - Margin Analysis ← *NEW*
   - Cross-sell Analysis ← *NEW*
   - Seasonal Trends ← *NEW*
   - Mix Optimization ← *NEW*

### 2.4 AI/MCP Integration Changes

| Current Implementation | Target Implementation | Changes Required |
|----------------------|---------------------|------------------|
| Direct OpenRouter API calls | MCP Server architecture | Build MCP server |
| Text-based chat only | MCP tools + chat interface | Add tool registry |
| No context management | Context cache with vector DB | Add Pinecone/Weaviate |
| Basic query handling | Natural language to SQL | Enhance LLM prompts |
| Single model (Kimi K2.5) | Multi-model with routing | Add model selection |

---

## 3. Upgrade Implementation Plan

### Phase 1: Database Migration & Foundation (Weeks 1-3)

**Week 1: PostgreSQL Setup & Schema Design**
```sql
-- Migration Tasks:
1. Create PostgreSQL database with new schema
2. Build migration scripts from SQLite to PostgreSQL
3. Set up Redis for caching
4. Configure connection pooling
5. Implement database migrations (Alembic/Prisma)

-- New Tables to Create:
- users (authentication & RBAC)
- locations (market management)
- business_types (category classification)
- businesses (market grouping)
- api_connections (Odoo API config)
- sync_jobs (scheduled tasks)
```

**Week 2: Data Migration**
```python
# Migration Script Structure:
1. Export SQLite data to intermediate format (JSON/CSV)
2. Transform data to match new schema
3. Import to PostgreSQL with validation
4. Verify data integrity
5. Create materialized views for performance

# Critical Mappings:
- stock_analysis_records → inventory_snapshots
- where_sold_records → sales_transactions (location aggregation)
- product_rank_records → analytics views (derived, not stored)
- product_sales_reports → sales_daily_summary
```

**Week 3: Backend API Refactoring**
```python
# Current FastAPI Structure:
stockout_platform/
├── backend/
│   ├── api/           # Keep and extend
│   ├── ingestion/     # Refactor for new reports
│   ├── repository/    # Add PostgreSQL support
│   └── services/      # Add new analysis services

# Tasks:
1. Add async PostgreSQL support (asyncpg/SQLAlchemy 2.0)
2. Implement repository pattern for data access
3. Create new analysis service classes
4. Add authentication middleware
5. Implement API versioning (/api/v2/)
```

**Deliverables:**
- ✅ PostgreSQL database with migrated data
- ✅ Redis cache layer operational
- ✅ Backend API with v2 endpoints
- ✅ Data validation and integrity checks

---

### Phase 2: Analysis Engine Expansion (Weeks 4-6)

**Week 4: Sales Analysis Module**
```python
# New Service: sales_analysis_service.py

class SalesAnalysisService:
    """New module for comprehensive sales analytics"""
    
    async def get_sales_overview(self, filters: SalesFilters):
        # Aggregate sales metrics
        # Compare periods
        # Calculate growth rates
        
    async def get_sales_trends(self, date_range, granularity):
        # Time-series analysis
        # Moving averages
        # Seasonality detection
        
    async def get_product_performance(self, ranking_metric):
        # Top/bottom performers
        # ABC analysis
        # Velocity calculations
        
    async def compare_periods(self, period1, period2):
        # Period-over-period analysis
        # Variance calculation
        # Trend indicators
```

**Week 5: Enhanced Inventory Analysis**
```python
# Extend existing inventory analysis

class InventoryAnalysisService:
    """Enhanced from current stockout detection"""
    
    # Existing methods (keep):
    - detect_stockouts()
    - analyze_where_sold()
    - calculate_velocity()
    
    # New methods (add):
    - get_stock_valuation()
    - calculate_reorder_points()
    - analyze_movement_patterns()
    - predict_expiry_risks()
    - generate_replenishment_recommendations()
```

**Week 6: Location & Business Type Analysis**
```python
# New Service: location_analysis_service.py

class LocationAnalysisService:
    """Comprehensive location comparison"""
    
    async def compare_locations(self, metric, date_range):
        # Side-by-side metrics
        # Performance rankings
        # Benchmarking
        
    async def generate_heatmap_data(self, metric):
        # Geographic visualization data
        # Intensity mappings
        
    async def identify_top_performers(self, criteria):
        # Best performing locations
        # Success factor analysis
        
    async def analyze_location_trends(self, location_id):
        # Historical performance
        # Growth trajectories

# New Service: business_type_service.py

class BusinessTypeService:
    """Category and margin analysis"""
    
    async def get_category_mix(self, location_id):
        # Product mix breakdown
        # Category performance
        
    async def analyze_margins(self, category_filter):
        # Profitability by category
        # Margin trends
        
    async def identify_cross_sell_opportunities(self):
        # Product affinity analysis
        # Bundle recommendations
```

**Deliverables:**
- ✅ 4 analysis engines operational
- ✅ Enhanced inventory analysis (beyond stockouts)
- ✅ Location comparison capabilities
- ✅ Business type/category analytics

---

### Phase 3: MCP Server & AI Enhancement (Weeks 7-9)

**Week 7: MCP Server Architecture**
```typescript
// New: MCP Server Implementation (TypeScript/Node.js)

// mcp-server/src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

// Tools Registry
const tools = {
  // Inventory Tools
  query_inventory: {
    description: "Query current inventory levels",
    parameters: z.object({
      location_id: z.string(),
      product_id: z.string().optional(),
      alert_type: z.enum(["low_stock", "overstock", "expiring"]).optional()
    })
  },
  
  // Sales Tools  
  analyze_sales: {
    description: "Analyze sales performance",
    parameters: z.object({
      period: z.enum(["today", "week", "month", "quarter", "year"]),
      location_id: z.string().optional(),
      category: z.string().optional()
    })
  },
  
  // Location Tools
  compare_locations: {
    description: "Compare performance across locations",
    parameters: z.object({
      metric: z.enum(["sales", "profit", "turnover"]),
      date_range: z.object({ start: z.date(), end: z.date() })
    })
  },
  
  // Business Type Tools
  analyze_categories: {
    description: "Analyze category performance",
    parameters: z.object({
      business_type_id: z.string(),
      analysis_type: z.enum(["mix", "margin", "trends"])
    })
  }
};

// Resources
const resources = {
  "inventory://{location_id}/stock": getLocationStock,
  "sales://{date_range}/summary": getSalesSummary,
  "locations://list": getAllLocations,
  "analytics://{section}/{sub_section}": getAnalyticsData
};
```

**Week 8: Context Management & Vector DB**
```python
# New: Context cache service

class AIContextManager:
    """Manage AI context with vector embeddings"""
    
    async def build_context(self, business_id: str, context_type: str):
        # Aggregate relevant data
        # Create embeddings
        # Store in vector DB
        
    async def query_context(self, query: str, business_id: str):
        # Semantic search on context
        # Return relevant information
        
    async def refresh_context(self, business_id: str):
        # Update cached context
        # Invalidate old embeddings
```

**Week 9: Enhanced Chat Interface**
```python
# Extend current chat with MCP integration

class EnhancedChatService:
    """Upgraded from current LLM service"""
    
    async def process_query(self, query: str, conversation_id: str):
        # 1. Intent classification
        # 2. Tool selection via MCP
        # 3. Context retrieval
        # 4. LLM processing with tools
        # 5. Response formatting
        
    async def suggest_queries(self, user_id: str):
        # Personalized suggestions
        # Based on user role and history
        
    async def generate_insights(self, business_id: str):
        # Proactive insight generation
        # Daily/weekly summaries
```

**Deliverables:**
- ✅ MCP server with 10+ tools
- ✅ Vector DB integration
- ✅ Enhanced chat with context awareness
- ✅ Natural language to analytics translation

---

### Phase 4: Frontend Rewrite (Weeks 10-14)

**Week 10-11: Next.js Foundation**
```typescript
// New frontend structure (Next.js 14 App Router)

app/
├── layout.tsx              # Root layout with providers
├── page.tsx                # Dashboard (default view)
├── globals.css             # Tailwind configuration
│
├── (auth)/
│   ├── login/
│   └── register/
│
├── analytics/
│   ├── layout.tsx          # Analysis switcher wrapper
│   ├── page.tsx            # Redirect to default section
│   ├── sales/
│   │   ├── page.tsx        # Sales overview (default)
│   │   ├── trends/
│   │   ├── products/
│   │   └── compare/
│   ├── inventory/
│   │   ├── page.tsx        # Stock levels (default)
│   │   ├── movements/
│   │   ├── alerts/
│   │   ├── valuation/
│   │   └── reorder/
│   ├── locations/
│   │   ├── page.tsx        # Compare (default)
│   │   ├── heatmap/
│   │   ├── top-performers/
│   │   ├── details/
│   │   └── trends/
│   └── business-type/
│       ├── page.tsx        # Category mix (default)
│       ├── margins/
│       ├── cross-sell/
│       ├── seasonal/
│       └── optimization/
│
├── ai-chat/
│   └── page.tsx            # AI chat interface
│
├── reports/
│   └── page.tsx            # Report generation & history
│
└── settings/
    ├── profile/
    ├── api-connections/
    └── preferences/

components/
├── analysis-switcher/      # Reusable section switcher
├── charts/                 # Recharts wrappers
├── data-table/             # TanStack table
├── upload/                 # File upload components
└── chat/                   # Chat interface
```

**Week 12: Analysis Switcher Implementation**
```typescript
// components/analysis-switcher/SectionTabs.tsx

interface SectionConfig {
  id: string;
  label: string;
  icon: string;
  color: string;
  subSections: SubSection[];
}

const sections: SectionConfig[] = [
  {
    id: 'sales',
    label: 'Sales',
    icon: 'TrendingUp',
    color: '#10B981', // Green
    subSections: [
      { id: 'overview', label: 'Overview', default: true },
      { id: 'trends', label: 'Trends' },
      { id: 'products', label: 'Products' },
      { id: 'compare', label: 'Compare' }
    ]
  },
  {
    id: 'inventory',
    label: 'Inventory',
    icon: 'Package',
    color: '#3B82F6', // Blue
    subSections: [
      { id: 'stock-levels', label: 'Stock Levels', default: true },
      { id: 'movements', label: 'Movements' },
      { id: 'alerts', label: 'Alerts' },
      { id: 'valuation', label: 'Valuation' },
      { id: 'reorder', label: 'Reorder Points' }
    ]
  },
  // ... Location and Business Type sections
];

// Features:
- URL-based state: /analytics/{section}/{subsection}
- Keyboard shortcuts: Alt+1, Alt+2, etc.
- Persistent filters across switches
- Mobile-responsive design
```

**Week 13: Dashboard & Visualization**
```typescript
// Implementation priorities:

1. Dashboard Grid Layout
   - Drag-and-drop widgets
   - Customizable KPI cards
   - Real-time updates (WebSocket)

2. Chart Components
   - Time-series (Recharts)
   - Heatmaps (D3.js)
   - Geographic maps (Mapbox)
   - Comparison charts

3. Data Tables
   - Sortable, filterable
   - Pagination
   - Export to CSV/Excel

4. Mobile Optimization
   - Responsive breakpoints
   - Touch-friendly controls
   - PWA manifest
```

**Week 14: Integration & Testing**
```typescript
// Integration tasks:

1. API Client Setup
   - React Query for server state
   - Axios with interceptors
   - Error handling

2. State Management
   - Zustand for global state
   - URL state for filters
   - Local storage for preferences

3. Authentication
   - JWT token management
   - Protected routes
   - Role-based UI elements

4. Testing
   - Unit tests (Jest)
   - Integration tests (Playwright)
   - Performance testing (Lighthouse)
```

**Deliverables:**
- ✅ Next.js frontend with App Router
- ✅ Analysis switcher with 4 sections
- ✅ Responsive dashboard
- ✅ Mobile-optimized interface

---

### Phase 5: Odoo API Integration (Weeks 15-17)

**Week 15: API Connector Development**
```python
# New service: odoo_connector.py

class Odoo18Connector:
    """Native Odoo 18.0 API integration"""
    
    def __init__(self, url: str, database: str, api_key: str):
        self.url = url
        self.db = database
        self.api_key = api_key
        
    async def authenticate(self):
        # Odoo 18.0 authentication
        # API key or OAuth
        
    async def fetch_inventory(self, last_sync: datetime):
        # Incremental sync
        # Using write_date field
        
    async def fetch_sales_orders(self, date_range):
        # Sales data extraction
        # Pagination handling
        
    async def fetch_stock_moves(self, filters):
        # Movement tracking
        # Transfer types
        
    async def test_connection(self):
        # Health check
        # Permission validation
```

**Week 16: Scheduled Sync Jobs**
```python
# New: Background job scheduler

class SyncScheduler:
    """Manage automated data synchronization"""
    
    async def schedule_full_sync(self, connection_id: str):
        # Weekly full refresh
        # Complete data reimport
        
    async def schedule_incremental_sync(self, connection_id: str):
        # Hourly incremental
        # Only changed records
        
    async def schedule_real_time_webhooks(self, connection_id: str):
        # Immediate updates
        # If Odoo supports webhooks
        
    async def handle_sync_failure(self, job_id: str, error: Exception):
        # Retry logic
        # Alert notifications
        # Error logging
```

**Week 17: Migration from File to API**
```python
# Migration strategy:

1. Dual Mode Support
   - Allow both file upload and API
   - User-configurable preference
   
2. Data Validation
   - Compare file vs API data
   - Reconciliation reports
   
3. Historical Data Preservation
   - Keep existing file-based data
   - Mark source in database
   
4. Rollback Capability
   - Revert to file upload if API fails
   - Backup connections
```

**Deliverables:**
- ✅ Odoo 18.0 API connector
- ✅ Scheduled sync jobs
- ✅ Migration tools
- ✅ Monitoring dashboard

---

### Phase 6: Reporting & Advanced Features (Weeks 18-20)

**Week 18: Reporting Engine**
```python
# New service: report_generator.py

class ReportGenerator:
    """Advanced reporting capabilities"""
    
    async def generate_scheduled_report(self, template_id: str):
        # Cron-based generation
        # Email delivery
        
    async def create_custom_report(self, config: ReportConfig):
        # User-defined reports
        # Drag-and-drop builder
        
    async def export_data(self, query: Query, format: ExportFormat):
        # PDF generation (ReportLab/WeasyPrint)
        # Excel export (OpenPyXL)
        # CSV streaming
        
    async def schedule_email_delivery(self, report_id: str, recipients: List[str]):
        # SMTP integration
        # Template customization
```

**Week 19: Advanced Analytics**
```python
# ML Integration (Phase 5 from original)

class PredictiveAnalytics:
    """Machine learning models"""
    
    async def forecast_demand(self, product_id: str, days: int):
        # Time-series forecasting
        # Seasonal adjustments
        
    async def predict_stockout_risk(self, location_id: str):
        # Risk scoring
        # Early warning system
        
    async def optimize_reorder_points(self, location_id: str):
        # Dynamic ROP calculation
        # Safety stock optimization
        
    async def anomaly_detection(self, metric: str):
        # Statistical anomaly detection
        # Alert generation
```

**Week 20: PWA & Mobile Optimization**
```typescript
// Progressive Web App features:

1. Service Worker
   - Offline data caching
   - Background sync
   
2. Push Notifications
   - Alert notifications
   - Report ready alerts
   
3. Mobile-Specific UI
   - Bottom navigation
   - Swipe gestures
   - Touch-optimized charts
   
4. App Shell Architecture
   - Fast initial load
   - Lazy loading
```

**Deliverables:**
- ✅ Scheduled report generation
- ✅ Email delivery system
- ✅ ML-based predictions
- ✅ PWA with offline support

---

## 4. Data Migration Strategy

### 4.1 Migration Scripts

```python
# migration_scripts/convert_sqlite_to_postgres.py

async def migrate_data():
    """
    Step-by-step migration from SQLite to PostgreSQL
    """
    
    # Step 1: Extract from SQLite
    sqlite_data = {
        'stock_analysis': await extract_stock_analysis(),
        'where_sold': await extract_where_sold(),
        'product_rank': await extract_product_rank(),
        'sales_reports': await extract_sales_reports(),
        'transactions': await extract_transactions()
    }
    
    # Step 2: Transform to new schema
    transformed_data = {
        'inventory_snapshots': transform_stock_analysis(sqlite_data['stock_analysis']),
        'sales_transactions': transform_where_sold(sqlite_data['where_sold']),
        'sales_daily_summary': transform_sales_reports(sqlite_data['sales_reports']),
        'inventory_movements': transform_transactions(sqlite_data['transactions'])
        # Note: product_rank becomes analytics views, not stored
    }
    
    # Step 3: Load to PostgreSQL
    await load_to_postgres(transformed_data)
    
    # Step 4: Validate
    await validate_migration()
    
    # Step 5: Create analytics views
    await create_analytics_views()
```

### 4.2 Validation Checklist

| Check | Method | Success Criteria |
|-------|--------|----------------|
| Record Count | SQL COUNT | Match between source and target |
| Data Integrity | Checksum/Hash | Identical critical fields |
| Relationships | Foreign key validation | No orphaned records |
| Performance | Query timing | < 100ms for common queries |
| API Compatibility | Endpoint testing | All v1 endpoints work with v2 |

---

## 5. Risk Mitigation & Rollback Plan

| Risk | Mitigation | Rollback Strategy |
|------|-----------|-------------------|
| Data loss during migration | Full backup before migration | Restore from backup |
| Performance degradation | Load testing in staging | Optimize queries, add indexes |
| User adoption issues | Parallel running period | Keep old UI accessible |
| API integration failures | Fallback to file upload | Disable API, use file mode |
| MCP server instability | Circuit breaker pattern | Fallback to direct LLM calls |

### Rollback Procedures

```bash
# Emergency rollback script

# 1. Stop new services
docker-compose stop nextjs-app mcp-server

# 2. Restore database
pg_restore -d micromarket_db backup_pre_migration.sql

# 3. Start legacy services
docker-compose up -d streamlit-app fastapi-sqlite

# 4. Update DNS/routing
# Point traffic back to old platform

# 5. Notify stakeholders
# Send rollback notification
```

---

## 6. Success Criteria

### Phase Success Metrics

| Phase | Criteria | Measurement |
|-------|----------|-------------|
| **Phase 1** | Zero data loss | Record count match 100% |
| **Phase 2** | All 4 analysis sections functional | End-to-end testing pass |
| **Phase 3** | MCP tools respond < 2s | Performance testing |
| **Phase 4** | Lighthouse score > 90 | Automated testing |
| **Phase 5** | API sync 99.9% reliable | 7-day monitoring |
| **Phase 6** | Report generation < 30s | Load testing |

### Final Platform KPIs

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| Analysis Sections | 3 | 4 | +33% |
| Report Types | 5 | 7+ | +40% |
| Database Records | 681K | 1M+ | +47% |
| Query Response Time | <500ms | <200ms | 2.5x faster |
| AI Response Time | Variable | <3s | Consistent |
| Mobile Support | Limited | Full PWA | New capability |
| Concurrent Users | Single user | 1000+ | Scalability |

---

## 7. Resource Requirements

### Development Team

| Role | Count | Duration | Responsibility |
|------|-------|----------|----------------|
| Backend Engineer | 2 | Full project | API, database, MCP server |
| Frontend Engineer | 2 | Weeks 10-20 | Next.js, UI components |
| Data Engineer | 1 | Weeks 1-6 | Migration, ETL, analytics |
| ML Engineer | 1 | Weeks 17-20 | Predictive models |
| DevOps Engineer | 1 | Weeks 1, 19-20 | Infrastructure, deployment |
| QA Engineer | 1 | Weeks 14-20 | Testing, validation |

### Infrastructure Costs

| Component | Current | Target | Monthly Cost |
|-----------|---------|--------|--------------|
| Database | SQLite (free) | PostgreSQL RDS | $200-500 |
| Cache | None | Redis Elasticache | $100-200 |
| Compute | Local server | EC2/Kubernetes | $300-600 |
| Storage | Local disk | S3 + EBS | $50-100 |
| AI/LLM | OpenRouter | OpenRouter + Vector DB | $200-500 |
| **Total** | **Minimal** | **Production** | **$850-1900/mo** |

---

## 8. Conclusion

This upgrade plan transforms the existing **Stockout Analysis Platform** into a comprehensive **Micromarket Business Intelligence Platform** through:

1. **Architecture Modernization**: SQLite → PostgreSQL, Streamlit → Next.js
2. **Scope Expansion**: 3 pillars → 4 analysis sections with sub-analysis
3. **AI Enhancement**: Direct LLM → MCP server with tools
4. **Integration**: File-only → File + API with scheduled sync
5. **User Experience**: Basic UI → Operator-friendly with switchers
6. **Mobility**: Desktop-only → PWA with offline support

**Recommended Approach**: Incremental migration with parallel running to minimize risk and ensure business continuity.

---

**Document Version**: 1.0  
**Created**: Planning Phase  
**Next Review**: After Phase 1 completion