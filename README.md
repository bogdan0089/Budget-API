# 💰 Smart Budget API

> **Personal finance backend** — track accounts, transactions, budgets and savings goals with AI-powered spending analysis.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_async-D71F00?style=flat)
[![CI](https://github.com/bogdan0089/Budget-API/actions/workflows/ci.yml/badge.svg)](https://github.com/bogdan0089/Budget-API/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat)

---

## 🎯 Problem

Most people don't know where their money goes. Bank apps show transactions but give no insight — no budget limits, no savings tracking, no understanding of patterns.

**Smart Budget API** solves this by giving every user:
- A clear picture of income vs. spending across multiple accounts
- Monthly budget limits per category with real-time "how much is left" tracking
- Savings goals with progress so you always know how far you are from a target
- AI analysis that reads your actual transaction history and explains your spending in plain language

Built as a production-ready REST API that any frontend (web, mobile) can connect to.

The Vue web client lives in a separate repository: [budget-frontend](https://github.com/bogdan0089/budget-frontend).

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🏦 **Multi-account** | Cash, card, savings, credit — all in one place |
| 💸 **Transactions** | Income & expense with categories; balance updated atomically, delete rolls it back |
| 📊 **Budgets** | Monthly limits per category — shows spent, remaining, % used |
| 🎯 **Goals** | Savings targets with deposit tracking and auto-completion |
| 🏷️ **Categories** | 10 default categories auto-created on registration |
| 🤖 **AI Insights** | Groq (llama-3.3-70b) analyzes your history and answers finance questions |
| 🔐 **Auth** | JWT bearer tokens, bcrypt passwords, per-user data isolation |

---

## 🏗️ Architecture

```
Router → Service → Repository → Database
```

Clean 3-layer architecture — no Unit of Work, no magic. Each layer has one job:

```
app/
│
├── routers/          # HTTP layer — validates request, calls service, maps exceptions to HTTP codes
│   ├── auth_router.py
│   ├── account_router.py
│   ├── transaction_router.py
│   ├── budget_router.py
│   ├── goal_router.py
│   ├── category_router.py
│   └── ai_router.py
│
├── services/         # Business logic — orchestrates operations, enforces rules
│   ├── auth_service.py        # Register (+ create 10 default categories), login, JWT
│   ├── account_service.py     # Account CRUD, ownership checks
│   ├── transaction_service.py # Atomic balance update + transaction in one commit
│   ├── budget_service.py      # Monthly limits, spent calculation, duplicate prevention
│   ├── goal_service.py        # Deposit tracking, auto-completion, guard on completed goals
│   ├── category_service.py    # Read-only (categories managed by system, not user)
│   └── ai_service.py          # Builds spending context, calls Groq API
│
├── repositories/     # Data access — all SQL lives here, services stay clean
│   ├── user_repository.py
│   ├── account_repository.py
│   ├── transaction_repository.py   # get_spent_by_category() for budget calculations
│   ├── budget_repository.py        # get_by_user_and_category() for duplicate check
│   ├── goal_repository.py
│   └── category_repository.py
│
├── db/
│   ├── base_model.py       # UUID primary key + created_at/updated_at for all models
│   ├── base_repository.py  # Generic BaseRepository[T] — add/stage/get/update/delete
│   ├── models.py           # All ORM models + enums in one place
│   └── session.py          # Async SQLAlchemy session factory
│
├── dto/
│   ├── input/      # Request schemas with Pydantic v2 validation (amounts > 0, password min 8)
│   └── output/     # Response schemas — what the API returns
│
├── dependencies/
│   └── auth.py     # get_current_user — JWT decode → User object
│
└── core/
    ├── config.py          # Settings from .env via pydantic-settings
    ├── exceptions.py      # Domain exceptions: EntityNotFound, InsufficientFunds, etc.
    └── error_handlers.py  # One mapping domain exception → HTTP status for the whole app

alembic/        # Async Alembic migrations
tests/          # mock-based pytest-asyncio tests (no DB needed)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (or Docker)

### 1. Clone & install

```bash
git clone https://github.com/YOUR_USERNAME/smart-budget-api.git
cd smart-budget-api

python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
```

Edit `.env`:

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=smart_budget

SECRET_KEY=your-very-long-secret-key-at-least-32-characters
GROQ_API_KEY=your_groq_api_key   # free at console.groq.com
```

### 3a. Run with Docker (recommended)

```bash
docker compose up -d
```

API starts at `http://localhost:8000` — PostgreSQL included.

### 3b. Run locally

```bash
alembic upgrade head       # apply migrations
uvicorn main:app --reload  # start dev server
```

---

## 📖 API Overview

Interactive docs: **`http://localhost:8000/docs`**

### Authentication

```http
POST /auth/register          # creates account + 10 default categories
POST /auth/login             # returns { access_token, token_type }
POST /auth/forgot-password   # emails a reset link (logged to console in dev)
POST /auth/reset-password    # sets a new password by reset token
POST /auth/change-password   # changes password for the logged-in user
```

All other routes require:
```
Authorization: Bearer <token>
```

### Endpoints

```
🏦 Accounts
  GET    /accounts           — list all accounts
  POST   /accounts           — create account (balance starts at 0)
  GET    /accounts/{id}      — get account detail
  PATCH  /accounts/{id}      — update name / currency
  DELETE /accounts/{id}      — delete account

💸 Transactions
  POST   /transactions                    — create transaction (updates balance atomically)
  GET    /transactions/account/{id}       — list account transactions
                                            (filters: type, category_id, date_from, date_to, limit, offset)
  DELETE /transactions/{id}               — delete transaction (rolls the balance back)

📊 Budgets
  GET    /budgets             — list budgets with spent_amount + remaining
  POST   /budgets             — set monthly limit for a category
  PATCH  /budgets/{id}        — update limit
  DELETE /budgets/{id}        — remove budget

🎯 Goals
  GET    /goals               — list savings goals with progress %
  POST   /goals               — create goal with target amount
  POST   /goals/{id}/deposit  — add money toward a goal
  DELETE /goals/{id}          — delete goal

🏷️ Categories
  GET    /categories          — list your categories (income + expense)

🤖 AI
  GET    /ai/analyze          — AI analysis of your spending patterns
  POST   /ai/chat             — ask anything about your finances

❤️ Service
  GET    /health              — liveness probe (no auth)
```

---

## 🧪 Tests

```bash
pytest tests/ -v
```

```
66 passed in 2.62s
```

All tests are mock-based — no database required. Covers:
- Account ownership and CRUD
- Atomic transaction + balance update
- Insufficient funds guard
- Transaction delete with balance rollback and overdraw guard
- Transaction filters (type, category, dates)
- Monthly budget creation, update, spending calculation
- Goal deposit, progress, completion, guard on already-completed goals
- Auth registration and login flows
- AI fallback when no Groq key is configured
- Every domain exception maps to its HTTP status code

---

## 🔑 Environment Variables

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `DB_USER` | ✅ | — | PostgreSQL username |
| `DB_PASSWORD` | ✅ | — | PostgreSQL password |
| `DB_HOST` | ✅ | — | PostgreSQL host |
| `DB_PORT` | ❌ | `5432` | PostgreSQL port |
| `DB_NAME` | ✅ | — | Database name |
| `SECRET_KEY` | ✅ | — | JWT signing key (32+ chars) |
| `ALGORITHM` | ❌ | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌ | `60` | Token TTL in minutes |
| `GROQ_API_KEY` | ❌ | `""` | Groq key — AI features disabled if empty |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |
| `CORS_ORIGINS` | ❌ | `localhost:3000,localhost:5173` | Comma-separated allowed origins |
| `FRONTEND_URL` | ❌ | `http://localhost:5173` | Base URL used in password reset links |
| `RESET_TOKEN_EXPIRE_MINUTES` | ❌ | `60` | Reset link TTL in minutes |
| `SMTP_HOST` | ❌ | `""` | SMTP host — empty means reset links are logged, not emailed |
| `SMTP_PORT` | ❌ | `587` | SMTP port |
| `SMTP_USER` | ❌ | `""` | SMTP username |
| `SMTP_PASSWORD` | ❌ | `""` | SMTP password |
| `SMTP_FROM` | ❌ | `Smart Budget <no-reply@smartbudget.app>` | Sender address |

---

## 📄 License

MIT — free to use, modify and distribute.
