# BankMind — Banker Intelligence Platform

A B2B SaaS demo for banks — 4 autonomous AI agents handle the full customer lifecycle (Lead → Onboarding → Active → Engaged), coordinated by an Orchestrator, monitored through a real-time Banker Dashboard.

This repository contains the complete codebase for both backend API service and the React frontend dashboard interface.

---

## Project Structure

```text
BankMind/
├── bankmind/
│   ├── bankmind-api/      # FastAPI backend (Python 3.12)
│   │   ├── agents/        # 4 autonomous AI agents (Acquisition, Onboarding, Adoption, Life-Event)
│   │   ├── orchestrator/  # Agent orchestration coordinator
│   │   ├── models/        # SQLAlchemy Database models
│   │   ├── routers/       # FastAPI routing endpoints
│   │   ├── services/      # Claude LLM integration, in-memory Redis, and seeding services
│   │   └── init_db.py     # Database initializer script
│   │
│   └── bankmind-ui/       # React frontend application (Vite, Tailwind CSS, Zustand)
│       └── src/           # UI pages, components, hooks, and state store
```

---

## Quick Start (Local Setup)

### Prerequisites
- **Python 3.12+**
- **Node.js 18+**

---

### 1. Setup the Backend API

1. Navigate to the backend directory:
   ```bash
   cd bankmind/bankmind-api
   ```

2. Copy the environment variables template:
   ```bash
   cp .env.example .env
   ```
   *(Optional: Edit `.env` and configure your `ANTHROPIC_API_KEY` for Claude. If left empty, the system automatically falls back to high-fidelity mock agent simulations.)*

3. Create a Python virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   # On Windows:
   .\.venv\Scripts\pip install -r requirements.txt
   # On macOS/Linux:
   source .venv/bin/activate && pip install -r requirements.txt
   ```

4. Initialize the SQLite database and seed the demo banker account:
   ```bash
   # On Windows:
   .\.venv\Scripts\python init_db.py
   # On macOS/Linux:
   python init_db.py
   ```

5. Run the backend API server:
   ```bash
   # On Windows:
   .\.venv\Scripts\uvicorn main:app --port 8000
   # On macOS/Linux:
   uvicorn main:app --port 8000
   ```

Backend endpoints:
- API Home: [http://localhost:8000](http://localhost:8000)
- Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

### 2. Setup the Frontend UI

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd bankmind/bankmind-ui
   ```

2. Install the frontend dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

Frontend is accessible at: **[http://localhost:5173](http://localhost:5173)**

---

## Banker Demo Guide

1. Open **[http://localhost:5173](http://localhost:5173)** in your browser.
2. Log in using the seeded banker credentials:
   - **Email:** `admin@bankmind.ai`
   - **Password:** `demo123`
3. Navigate to **Demo Controls** from the sidebar menu.
4. Click **Seed Data** to generate test customers and transactions.
5. Click **Run Demo** to orchestrate all 4 AI agents sequentially, watching the live activity logs and dashboard analytics update in real-time.
