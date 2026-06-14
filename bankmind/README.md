# BankMind — Banker Intelligence Platform

A B2B SaaS demo for banks — 4 autonomous AI agents handle the full customer lifecycle (Lead → Onboarding → Active → Engaged), coordinated by an Orchestrator, monitored through a real-time Banker Dashboard.

## Stack
- **Backend**: FastAPI (Python 3.11) + PostgreSQL + Redis
- **AI**: Claude claude-sonnet-4-6 (Anthropic)
- **Frontend**: React + Vite + Tailwind CSS + Zustand
- **Real-time**: WebSocket

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop (for PostgreSQL + Redis)
- An Anthropic API key

### 1. Start Database & Redis

```bash
cd bankmind-api
docker compose up -d
```

Wait ~10 seconds for services to be healthy.

### 2. Set up Backend

```bash
cd bankmind-api

# Copy and configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Install dependencies
pip install -r requirements.txt

# Run migrations (creates all 6 tables + seeds demo banker)
alembic upgrade head

# Start the API server
uvicorn main:app --reload --port 8000
```

### 3. Set up Frontend

```bash
cd bankmind-ui

# Install dependencies (already done if you ran npm install)
npm install

# Start dev server
npm run dev
```

### 4. Access the App

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### 5. Demo Credentials

```
Email: admin@bankmind.ai
Password: demo123
```

---

## Running the Demo

1. **Login** with demo credentials
2. **Navigate to Demo Controls** (sidebar → ▶ Demo Controls)
3. Click **Seed Data** to create 5 demo customers with 60 transactions each
4. Click **Run Demo** — all 4 AI agents will run sequentially
5. Watch the **Live Activity Feed** update in real-time on the Dashboard
6. Click any customer card to see the **3-panel detail view** (Profile | Chat | Agent Logs)
7. Use **Override** on any agent action to test the banker control flow
8. Click **Reset** to wipe data and start fresh anytime

---

## The 4 AI Agents

| Agent | Stage | What it does |
|---|---|---|
| **Acquisition** | Lead | Scores leads 0–100, crafts outreach, auto-transitions ≥70 to onboarding |
| **Onboarding** | Onboarding | Full KYC dialogue, doc verification, eligibility check, account creation |
| **Adoption** | Active | Detects unused features, sends personalized nudges (max 2/day via Redis) |
| **Life-Event** | Active | Analyzes 60-day transactions, detects life signals, recommends products |

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET` | Secret key for JWT signing |
| `ANTHROPIC_API_KEY` | Your Anthropic API key (Claude claude-sonnet-4-6) |
| `FRONTEND_URL` | Frontend URL for CORS whitelist |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login` | Banker login → JWT |
| GET | `/api/v1/customers` | List all customers |
| GET | `/api/v1/customers/:id` | Get customer detail |
| POST | `/api/v1/agents/run/:id` | Manually trigger agent for customer |
| GET | `/api/v1/dashboard/kpis` | Dashboard KPI metrics |
| GET | `/api/v1/dashboard/pipeline` | Pipeline stage counts |
| POST | `/api/v1/demo/seed` | Seed 5 demo customers |
| POST | `/api/v1/demo/run` | Run full demo sequence |
| POST | `/api/v1/demo/reset` | Wipe all data and re-seed |
| WS | `/ws/dashboard` | Real-time WebSocket feed |
| GET | `/health` | DB + Redis health check |

---

## Project Structure

```
bankmind/
├── bankmind-api/          # FastAPI backend
│   ├── agents/            # 4 AI agents + base class
│   ├── orchestrator/      # Agent coordination
│   ├── models/            # SQLAlchemy models (6 tables)
│   ├── routers/           # FastAPI route handlers
│   ├── services/          # LLM, Redis, Seed services
│   ├── websocket/         # WebSocket connection manager
│   ├── prompts/           # 4 system prompt files
│   └── alembic/           # 7 DB migrations
└── bankmind-ui/           # React frontend
    └── src/
        ├── pages/         # 5 pages (Login, Dashboard, etc.)
        ├── components/    # All UI components
        ├── store/         # Zustand state stores
        ├── hooks/         # useWebSocket hook
        └── lib/           # API fetch wrapper
```
