# Clausemate - Implementation Plan

## Project Overview

A full-stack SaaS application for contract management that:
1. Extracts structured data from contract PDFs using Claude Vision API
2. Analyzes contracts against market rate benchmarks
3. Generates AI-powered recommendations (cost reduction, consolidation, risk alerts, renewal reminders)
4. Displays everything in a user-friendly dashboard

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI + Python |
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| Database | Supabase PostgreSQL + Auth + Storage |
| AI | Anthropic Claude Vision API |

## Current State: Implementation Complete

All major components exist and are functional:

| Layer | Status | Key Files |
|-------|--------|-----------|
| Execution Scripts | Complete | `execution/claude_extractor.py`, `recommendation_engine.py`, `market_rates.py` |
| Backend API | Complete | `backend/routers/upload.py`, `contracts.py`, `recommendations.py` |
| Backend Services | Complete | `backend/services/extraction.py`, `analysis.py` |
| Frontend Pages | Complete | `frontend/src/pages/Dashboard.tsx`, `Upload.tsx`, `Contracts.tsx`, `Login.tsx` |
| Frontend Components | Complete | `ExtractionReview.tsx`, `RecommendationCard.tsx`, `Layout.tsx` |
| Database Schema | Complete | 3 SQL migrations in `supabase/migrations/` |

---

## Phase 1: Environment Setup

### 1.1 Supabase Project Setup
- [ ] Create Supabase project at https://supabase.com (or use existing)
- [ ] Note project URL and API keys from Settings > API
- [ ] Enable Email authentication provider

### 1.2 Run Database Migrations
Execute in Supabase SQL Editor (in order):
1. `supabase/migrations/001_create_contracts.sql` - Contracts table with RLS
2. `supabase/migrations/002_create_recommendations.sql` - Recommendations table with RLS
3. `supabase/migrations/003_storage_policies.sql` - Storage bucket for contract PDFs

### 1.3 Configure Environment Variables

**Backend `.env`:**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
ANTHROPIC_API_KEY=sk-ant-...
```

**Frontend `frontend/.env`:**
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
VITE_API_URL=http://localhost:8000
```

### 1.4 Install Dependencies
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

---

## Phase 2: Run & Test

### 2.1 Start Services
```bash
# Terminal 1: Backend (port 8000)
cd backend && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend (port 5173)
cd frontend && npm run dev
```

### 2.2 Test Flows
| Flow | Steps |
|------|-------|
| Auth | Sign up → Verify email → Login → Logout |
| Upload | Upload PDF → Review extraction → Edit fields → Confirm |
| Dashboard | View stats → Generate recommendations → Accept/dismiss |
| Contracts | List contracts → View details → Delete contract |

---

## Phase 3: Optional Enhancements

- [ ] Add contract detail page (`/contracts/:id`)
- [ ] Add toast notifications for success/error feedback
- [ ] Add batch upload support for multiple PDFs
- [ ] Add export to CSV functionality
- [ ] Improve market rates with regional pricing data
- [ ] Add webhook for automated recommendation generation

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Login   │  │ Dashboard│  │ Contracts│  │     Upload       │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │
└───────┼─────────────┼─────────────┼─────────────────┼───────────┘
        │             │             │                 │
        ▼             ▼             ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │  /contracts  │  │/recommendations│ │      /upload          │ │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬─────────────┘ │
└─────────┼─────────────────┼─────────────────────┼───────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Execution Layer (Python)                     │
│  ┌────────────────┐  ┌─────────────────────┐  ┌──────────────┐  │
│  │ market_rates.py│  │recommendation_engine│  │claude_extractor│ │
│  └────────────────┘  └─────────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │                 │                     │
          ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                            │
│  ┌──────────────────────────┐  ┌──────────────────────────────┐ │
│  │   Supabase (DB/Auth/     │  │   Anthropic Claude API       │ │
│  │      Storage)            │  │   (Vision + Text)            │ │
│  └──────────────────────────┘  └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Critical Files Reference

| Purpose | File Path |
|---------|-----------|
| PDF Extraction | `execution/claude_extractor.py` |
| Recommendations | `execution/recommendation_engine.py` |
| Market Rates | `execution/market_rates.py` |
| Upload API | `backend/routers/upload.py` |
| Contracts API | `backend/routers/contracts.py` |
| Recommendations API | `backend/routers/recommendations.py` |
| Dashboard UI | `frontend/src/pages/Dashboard.tsx` |
| Upload UI | `frontend/src/pages/Upload.tsx` |
| API Client | `frontend/src/lib/api.ts` |
| Contracts Schema | `supabase/migrations/001_create_contracts.sql` |
| Recommendations Schema | `supabase/migrations/002_create_recommendations.sql` |

---

## Verification Checklist

- [ ] Supabase project created and migrations run
- [ ] Storage bucket "contracts" exists with policies
- [ ] Environment variables configured (backend + frontend)
- [ ] Backend starts without errors on port 8000
- [ ] Frontend starts without errors on port 5173
- [ ] Can sign up and login
- [ ] Can upload a PDF and see extraction results
- [ ] Can confirm extraction and save contract
- [ ] Dashboard shows contract stats
- [ ] Can generate AI recommendations

---

## Next Steps

1. **Restart Claude Code session** to activate Supabase MCP
2. Use MCP to list/select Supabase project
3. Run migrations via MCP or SQL Editor
4. Configure .env files with project credentials
5. Install dependencies and start services
6. Test end-to-end flow
