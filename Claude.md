
# Agent Instructions

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `directives/`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, update directives with learnings
- You're the glue between intent and execution. E.g you don't try scraping websites yourself—you read `directives/scrape_website.md` and come up with inputs/outputs and then run `execution/scrape_single_site.py`

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts in `execution/`
- Environment variables, api tokens, etc are stored in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast. Use scripts instead of manual work.

**Why this works:** if you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps. The solution is push complexity into deterministic code. That way you just focus on decision-making.

## Operating Principles

**1. Check for tools first**
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

**2. Self-anneal when things break**
- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits/etc—in which case you check w user first)
- Update the directive with what you learned (API limits, timing, edge cases)
- Example: you hit an API rate limit → you then look into API → find a batch endpoint that would fix → rewrite script to accommodate → test → update directive.

**3. Update directives as you learn**
Directives are living documents. When you discover API constraints, better approaches, common errors, or timing expectations—update the directive. But don't create or overwrite directives without asking unless explicitly told to. Directives are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded).

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update directive to include new flow
5. System is now stronger

## File Organization

**Deliverables vs Intermediates:**
- **Deliverables**: Google Sheets, Google Slides, or other cloud-based outputs that the user can access
- **Intermediates**: Temporary files needed during processing

**Directory structure:**
- `.tmp/` - All intermediate files (dossiers, scraped data, temp exports). Never commit, always regenerated.
- `execution/` - Python scripts (the deterministic tools)
- `directives/` - SOPs in Markdown (the instruction set)
- `.env` - Environment variables and API keys
- `credentials.json`, `token.json` - Google OAuth credentials (required files, in `.gitignore`)

**Key principle:** Local files are only for processing. Deliverables live in cloud services (Google Sheets, Slides, etc.) where the user can access them. Everything in `.tmp/` can be deleted and regenerated.

## Cloud Webhooks (Modal)

The system supports event-driven execution via Modal webhooks. Each webhook maps to exactly one directive with scoped tool access.

**When user says "add a webhook that...":**
1. Read `directives/add_webhook.md` for complete instructions
2. Create the directive file in `directives/`
3. Add entry to `execution/webhooks.json`
4. Deploy: `modal deploy execution/modal_webhook.py`
5. Test the endpoint

**Key files:**
- `execution/webhooks.json` - Webhook slug → directive mapping
- `execution/modal_webhook.py` - Modal app (do not modify unless necessary)
- `directives/add_webhook.md` - Complete setup guide

**Endpoints:**
- `https://nick-90891--claude-orchestrator-list-webhooks.modal.run` - List webhooks
- `https://nick-90891--claude-orchestrator-directive.modal.run?slug={slug}` - Execute directive
- `https://nick-90891--claude-orchestrator-test-email.modal.run` - Test email

**Available tools for webhooks:** `send_email`, `read_sheet`, `update_sheet`

**All webhook activity streams to Slack in real-time.**

## MCP Servers (Model Context Protocol)

MCP servers extend Claude's capabilities by providing direct integrations with external services. The following are configured:

### Supabase MCP
Provides direct database access and management for Supabase projects.

**Installation command used:**
```bash
claude mcp add supabase -s user -- npx -y @supabase/mcp-server-supabase --access-token YOUR_ACCESS_TOKEN
```

**Capabilities:**
- Query and manage database tables
- Execute SQL (read/write unless `--read-only` flag is set)
- Manage database schema
- Access all projects in the org (or scoped to one with `--project-ref`)

**Usage:** Ask natural language questions like "What tables are in my database?" and Claude will use the MCP tools automatically.

**Management commands:**
```bash
claude mcp list                    # List all configured MCP servers
claude mcp remove supabase -s user # Remove the Supabase MCP
```

**Security notes:**
- Access token is stored in `~/.claude.json`
- For production, use `--read-only` flag to prevent write operations
- Scope to specific project with `--project-ref YOUR_PROJECT_REF`

**Docs:** https://supabase.com/docs/guides/getting-started/mcp

### Other Available MCPs
These are available in the current Claude Code environment:
- **Hugging Face** - ML models, datasets, papers, spaces
- **Todoist** - Task and project management
- **Context7** - Library documentation lookup
- **Playwright** - Browser automation

## Contract Optimizer Dashboard

This project is a full-stack application for managing contracts and getting AI-powered cost optimization recommendations.

### Tech Stack

**Frontend:**
- React + TypeScript + Vite
- Tailwind CSS for styling
- Supabase Auth for authentication
- Located in `frontend/`

**Backend:**
- Python serverless functions on Vercel
- Supabase PostgreSQL database with Row Level Security
- Supabase Storage for PDF files
- Smart AI routing for contract extraction (see below)
- API handler in `api/index.py`

**Database Tables:**
- `contracts` - User contracts with provider, costs, dates, etc.
- `recommendations` - AI-generated cost optimization recommendations

### Deployment

**Live URL:** https://contracts-dashboard.vercel.app

**GitHub:** https://github.com/amirhshad/ContractsToDashboard

**Deploy commands:**
```bash
vercel --prod --yes          # Deploy to Vercel
git push origin main         # Push to GitHub (auto-deploy if connected)
```

**Environment Variables (Vercel):**
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_KEY` - Supabase service role key (for backend)
- `GEMINI_API_KEY` - Google Gemini API key (primary AI provider)
- `ANTHROPIC_API_KEY` - Claude API key (fallback for escalation)
- `VITE_SUPABASE_URL` - Frontend Supabase URL
- `VITE_SUPABASE_ANON_KEY` - Frontend Supabase key

### Local Development

**Backend:**
```bash
cd backend
python3.10 -m uvicorn backend.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Important:** The `frontend/.env` should NOT include `VITE_API_URL` for production builds. The frontend uses relative URLs (`/api/...`) which work on both local dev and Vercel.

### Key Files

- `api/index.py` - Vercel serverless API (all endpoints)
- `frontend/src/lib/api.ts` - Frontend API client
- `frontend/src/lib/supabase.ts` - Supabase client setup
- `vercel.json` - Vercel deployment configuration
- `.vercelignore` - Files to exclude from Vercel deployment
- `supabase/migrations/` - Database migration SQL files

### API Endpoints

- `GET /api/health` - Health check (includes AI routing config)
- `GET /api/contracts` - List user contracts
- `GET /api/contracts/summary` - Dashboard summary stats
- `GET /api/contracts/:id` - Get single contract
- `DELETE /api/contracts/:id` - Delete contract
- `POST /api/upload/extract` - Extract data from PDF using smart AI routing
- `POST /api/upload/confirm` - Save confirmed contract
- `GET /api/recommendations` - List recommendations
- `POST /api/recommendations/generate` - Generate AI recommendations

### Smart AI Routing

The system uses intelligent model routing to balance cost and quality:

**Flow:**
```
Upload contract → Gemini 3 Flash (initial extraction)
                       ↓
              Check escalation criteria
                       ↓
              If escalation needed:
                1. Gemini 2.5 Pro (preferred)
                2. Claude Sonnet 4 (fallback)
```

**Escalation Triggers:**
- `contract_type` is `rental`, `insurance`, or `service` (complex legal terms)
- `confidence` < 0.7
- `complexity` == "high"
- 6+ key terms detected

**Model Configuration:**
- Primary: `gemini-3-flash-preview` (fast, cost-effective)
- Escalation: `gemini-2.5-pro` (thorough, higher quality)
- Fallback: `claude-sonnet-4` (if Gemini Pro fails)

**Why This Matters:**
- Rental contracts have complex clauses (CPI + additional % increases)
- Insurance contracts have detailed coverage terms
- Simpler models miss multi-component clauses
- Escalation ensures complete extraction for complex contracts

### Multi-Document Support

Contracts can include up to 5 related documents:
- Main agreement
- Statement of Work (SOW)
- Terms & Conditions
- Amendments/Addendums
- Exhibits/Schedules

The AI analyzes all documents together and extracts a unified view.

### Contract Nickname

Each contract has a `contract_nickname` field for unique identification across the dashboard:
- Auto-generated by AI (e.g., "Office Lease - Aziëweg 220", "Car Insurance 2025")
- Used in Timeline, Analysis, Dashboard, and Contracts pages
- Falls back to `provider_name` if not set

### Notes

- Vercel's Python runtime doesn't support FastAPI/ASGI well, so we use a basic HTTP handler
- All authenticated endpoints require `Authorization: Bearer <token>` header
- PDFs are processed using Gemini's document understanding (with Claude fallback)
- The `.vercelignore` file prevents local `.env` files from being deployed
- Currency detection supports USD, EUR, GBP, CAD, AUD, JPY
- Key terms extraction is thorough: includes article references, percentages, all clause components

## Summary

You sit between human intent (directives) and deterministic execution (Python scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.

Also, use Opus-4.5 for everything while building. It came out a few days ago and is an order of magnitude better than Sonnet and other models. If you can't find it, look it up first.