# Micromarket Operator Platform - Tech Stack (Simplified)

## Overview

This document outlines the simplified technology stack for the Micromarket Operator Platform, designed for a small-scale deployment (<100 users) with minimal infrastructure complexity.

---

## Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.x | UI Framework |
| **TypeScript** | 5.x | Type Safety |
| **TanStack Query** | 5.x | Data Fetching & Caching |
| **TanStack Table** | 8.x | Data Tables |
| **Zustand** | 4.x | State Management |
| **Recharts** | 2.x | Data Visualization |
| **Tailwind CSS** | 3.x | Styling |
| **shadcn/ui** | Latest | Component Library |
| **Socket.io-client** | 4.x | Real-time Updates |
| **React Hook Form** | 7.x | Form Management |
| **Zod** | 3.x | Schema Validation |
| **date-fns** | 3.x | Date Utilities |
| **Lucide React** | Latest | Icons |

### Frontend Architecture
```
src/
├── components/
│   ├── ui/           # shadcn components
│   ├── charts/       # Recharts wrappers
│   ├── forms/        # Form components
│   └── layout/       # Layout components
├── hooks/            # Custom React hooks
├── stores/           # Zustand stores
├── lib/              # Utilities
├── api/              # API client
├── types/            # TypeScript types
└── routes/           # Route components
```

---

## Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Primary Language |
| **FastAPI** | 0.110+ | API Framework |
| **Uvicorn** | 0.27+ | ASGI Server |
| **Pydantic** | 2.x | Data Validation |
| **SQLAlchemy** | 2.x | ORM |
| **Alembic** | 1.13+ | Database Migrations |
| **Celery** | 5.3+ | Background Tasks |
| **Redis** | 7.x | Cache & Message Broker |
| **python-jose** | 3.3+ | JWT Handling |
| **passlib** | 1.7+ | Password Hashing |
| **bcrypt** | 4.x | Password Hashing |

### Data Processing
| Technology | Version | Purpose |
|------------|---------|---------|
| **Pandas** | 2.x | Data Manipulation |
| **OpenPyXL** | 3.1+ | Excel Processing |
| **python-csv** | Built-in | CSV Processing |

### Backend Architecture
```
backend/
├── app/
│   ├── api/          # API routes
│   │   ├── v1/       # Version 1 endpoints
│   │   └── deps.py   # Dependencies
│   ├── core/         # Core config
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   ├── db/           # Database utils
│   ├── tasks/        # Celery tasks
│   ├── parsers/      # File parsers
│   ├── analytics/    # Analytics engine
│   └── mcp/          # MCP server
├── alembic/          # Migrations
├── tests/            # Test suite
├── uploads/          # Local file storage
└── scripts/          # Utility scripts
```

---

## Database Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **PostgreSQL** | 16.x | Primary Database |
| **PostGIS** | 3.4+ | Geospatial Extension |
| **Redis** | 7.x | Cache & Session Store |

### Database Features Used
- **UUID Primary Keys**: For all entities
- **JSONB Columns**: Flexible metadata storage
- **Generated Columns**: Computed values
- **Geospatial Indexing**: Location data
- **Full-text Search**: Product search

---

## AI/ML Stack

### LLM Integration
| Technology | Version | Purpose |
|------------|---------|---------|
| **OpenAI API** | Latest | GPT-4, GPT-3.5 |
| **LangChain** | 0.1+ | LLM Orchestration |

### MCP (Model Context Protocol)
| Technology | Purpose |
|------------|---------|
| **MCP Server SDK** | Protocol implementation |
| **Custom Tools** | Database query tools |

### Analytics/ML
| Technology | Version | Purpose |
|------------|---------|---------|
| **scikit-learn** | 1.4+ | ML Algorithms |
| **Prophet** | 1.1+ | Time Series Forecasting |
| **Statsmodels** | 0.14+ | Statistical Models |

---

## Infrastructure & Deployment

### Containerization
| Technology | Version | Purpose |
|------------|---------|---------|
| **Docker** | 24.x | Container Runtime |
| **Docker Compose** | 2.24+ | Local Development & Deployment |

### Simple Deployment Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │              NGINX (Reverse Proxy)               │   │
│  │         - Static file serving                    │   │
│  │         - API routing                            │   │
│  │         - SSL termination                        │   │
│  └────────────────────┬────────────────────────────┘   │
│                       │                                 │
│  ┌────────────────────┼────────────────────────────┐   │
│  │                    │                            │   │
│  ▼                    ▼                            ▼   │
│ ┌────────┐    ┌──────────────┐    ┌──────────────┐   │
│ │Frontend│    │  FastAPI     │    │   Celery     │   │
│ │(React) │    │  (API)       │    │   Worker     │   │
│ │(NGINX) │    │  (Uvicorn)   │    │              │   │
│ └────────┘    └──────┬───────┘    └──────┬───────┘   │
│                      │                    │           │
│                      └────────┬───────────┘           │
│                               │                       │
│                      ┌────────▼────────┐             │
│                      │   PostgreSQL    │             │
│                      │   (Database)    │             │
│                      └─────────────────┘             │
│                               │                       │
│                      ┌────────▼────────┐             │
│                      │     Redis       │             │
│                      │ (Cache/Queue)   │             │
│                      └─────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

### Deployment Options

#### Option 1: Single Server (Recommended for <100 users)
- **Server**: 4 vCPU, 8GB RAM, 100GB SSD
- **OS**: Ubuntu 22.04 LTS
- **Deployment**: Docker Compose
- **SSL**: Let's Encrypt with certbot

#### Option 2: Managed Services
- **Database**: Managed PostgreSQL (AWS RDS, DigitalOcean, etc.)
- **Server**: 2 vCPU, 4GB RAM for application
- **File Storage**: Local mounted volume or simple cloud block storage

---

## Monitoring & Logging

| Technology | Version | Purpose |
|------------|---------|---------|
| **Prometheus** | 2.49+ | Metrics Collection |
| **Grafana** | 10.3+ | Visualization |
| **Loki** | 2.9+ | Log Aggregation |
| **Sentry** | Latest | Error Tracking |

### Simplified Monitoring Stack
```
┌─────────────────────────────────────────┐
│         Docker Compose                  │
│  ┌─────────┐  ┌─────────┐  ┌────────┐ │
│  │Prometheus│  │ Grafana │  │  Loki  │ │
│  │(Metrics) │  │(Charts) │  │ (Logs) │ │
│  └─────────┘  └─────────┘  └────────┘ │
└─────────────────────────────────────────┘
```

### Key Metrics Monitored
- API response times
- Database query performance
- Cache hit rates
- LLM token usage
- File processing throughput
- Error rates by endpoint

---

## Security Stack

| Technology | Purpose |
|------------|---------|
| **JWT** | Token-based Authentication |
| **bcrypt** | Password Hashing |
| **Let's Encrypt** | Free SSL Certificates |
| **Fail2Ban** | Intrusion Prevention |

### Security Measures
- **Authentication**: JWT with refresh tokens
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: TLS 1.3 in transit
- **API Security**: Rate limiting, request validation
- **CORS**: Strict origin policies

---

## Testing Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| **pytest** | 8.x | Test Framework |
| **pytest-asyncio** | 0.23+ | Async Testing |
| **pytest-cov** | 4.x | Coverage |
| **Playwright** | 1.41+ | E2E Testing |
| **Locust** | 2.20+ | Load Testing |

### Testing Strategy
- **Unit Tests**: 70% coverage target
- **Integration Tests**: API and DB testing
- **E2E Tests**: Critical user paths

---

## Development Tools

| Tool | Purpose |
|------|---------|
| **VS Code** | Primary IDE |
| **Git** | Version Control |
| **GitHub Actions** | CI/CD |
| **Postman** | API Testing |
| **pgAdmin** | Database Management |

### VS Code Extensions
- Python (Microsoft)
- Pylance
- ESLint
- Prettier
- Tailwind CSS IntelliSense
- Docker

### Code Quality
| Tool | Purpose |
|------|---------|
| **Ruff** | Python Linter |
| **Black** | Python Formatter |
| **isort** | Import Sorting |
| **mypy** | Type Checking |
| **ESLint** | JS/TS Linter |
| **Prettier** | JS/TS Formatter |

---

## Package Management

### Python
```txt
# requirements.txt
# Core
fastapi==0.110.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
sqlalchemy==2.0.25
alembic==1.13.1

# Data
pandas==2.2.0
openpyxl==3.1.0

# AI/ML
langchain==0.1.0
openai==1.12.0
scikit-learn==1.4.0
prophet==1.1.5

# Tasks
celery==5.3.0
redis==5.0.0

# Auth
python-jose==3.3.0
passlib==1.7.0
bcrypt==4.0.0

# Testing
pytest==8.0.0
pytest-asyncio==0.23.0
```

### JavaScript/TypeScript
```json
// package.json dependencies
{
  "dependencies": {
    "react": "^18.2.0",
    "@tanstack/react-query": "^5.18.0",
    "zustand": "^4.5.0",
    "tailwindcss": "^3.4.0",
    "recharts": "^2.10.0",
    "socket.io-client": "^4.7.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "eslint": "^8.56.0",
    "prettier": "^3.2.0",
    "playwright": "^1.41.0"
  }
}
```

---

## Simplified Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                        │
│              ┌─────────────────────┐                    │
│              │   React Web App     │                    │
│              │   (Browser)         │                    │
│              └──────────┬──────────┘                    │
│                         │ HTTPS                         │
└─────────────────────────┼───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   NGINX (Reverse Proxy)                  │
│              - Serves static files (React)               │
│              - Routes /api to FastAPI                    │
│              - SSL termination                           │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                   FastAPI Application                    │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  API Endpoints                                      │ │
│  │  ├── /auth/*     (Authentication)                   │ │
│  │  ├── /markets/*  (Micromarket CRUD)                 │ │
│  │  ├── /products/* (Product management)               │ │
│  │  ├── /inventory/* (Stock levels)                    │ │
│  │  ├── /sales/*    (Sales data)                       │ │
│  │  ├── /uploads/*  (File upload)                      │ │
│  │  ├── /analytics/* (Insights & reports)            │ │
│  │  └── /chat/*     (AI chatbot)                       │ │
│  ├─────────────────────────────────────────────────────┤ │
│  │  Services                                           │ │
│  │  ├── Analytics Engine                               │ │
│  │  ├── MCP Server                                     │ │
│  │  └── File Parser                                    │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼──────┐  ┌───────▼──────┐  ┌──────▼──────┐
│  PostgreSQL  │  │    Redis     │  │ Local       │
│  (Database)  │  │  (Cache/     │  │ Filesystem  │
│              │  │   Queue)     │  │ (Uploads)   │
└──────────────┘  └──────────────┘  └─────────────┘
```

---

## Deployment Configuration

### docker-compose.yml (Production)
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
      - ./data/certbot:/etc/letsencrypt
    depends_on:
      - api

  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres/db
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - postgres
      - redis

  worker:
    build: ./backend
    command: celery -A app.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres/db
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./uploads:/app/uploads
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## Performance Targets (Simplified Scale)

| Metric | Target | Notes |
|--------|--------|-------|
| API Response Time (p95) | < 300ms | Single server |
| Dashboard Load Time | < 3s | No CDN needed |
| Chat Response Time | < 5s | LLM latency |
| Concurrent Users | 50 | Comfortable limit |
| File Processing | 5K records/min | Background job |
| Database Size | < 100GB | With 2-year retention |

---

## Scaling Path (Future)

When approaching 100 users or growth needs:

1. **Database**: Move to managed PostgreSQL (AWS RDS, etc.)
2. **File Storage**: Migrate to S3-compatible storage
3. **Caching**: Redis Cluster for higher availability
4. **Workers**: Multiple Celery workers
5. **Load Balancing**: Multiple API instances behind NGINX

---

## Document Information

| Property | Value |
|----------|-------|
| **Version** | 1.0 (Simplified) |
| **Last Updated** | January 2025 |
| **Scale** | <100 users |
| **Deployment** | Docker Compose |
| **Status** | Approved |

---

*This is a simplified stack designed for rapid deployment and easy maintenance at small scale.*