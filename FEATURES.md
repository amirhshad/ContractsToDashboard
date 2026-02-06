# Clausemate - Feature Roadmap

## Current Features (v1.1)

- [x] PDF upload with AI extraction (up to 5 documents per contract)
- [x] Smart AI routing (Gemini Flash → Gemini Pro → Claude)
- [x] Dashboard with spending summary
- [x] Contract list with filtering
- [x] Timeline visualization (desktop + mobile)
- [x] Contract analysis/detail view
- [x] AI-powered recommendations
- [x] Multi-currency support (USD, EUR, GBP, CAD, AUD, JPY)
- [x] Prompt injection security
- [x] Mobile-responsive design
- [x] **Full-text search** (providers, nicknames, types, key terms)
- [x] **Export to CSV** (download contracts as spreadsheet)
- [x] **Spending Charts** (category pie chart, 12-month projection)

---

## Phase 1: Quick Wins

### Email Reminders
- [ ] Send email alerts for upcoming renewals/deadlines
- [ ] Configurable reminder periods (7, 30, 60 days before)
- [ ] Daily/weekly digest option
- **Tech:** Supabase Edge Functions + Resend/SendGrid

### Contract Search ✅
- [x] Full-text search across all contracts
- [x] Search in key terms, provider names, contract types
- [x] Filter by contract type
- **Tech:** Frontend filtering (implemented)

### Export to CSV ✅
- [x] Download contracts list as spreadsheet
- [x] Include all fields (provider, costs, dates, key terms)
- [x] Filename includes date for easy organization
- **Tech:** Frontend CSV generation (native)

---

## Phase 2: Core Improvements

### Spending Charts ✅
- [x] Monthly/yearly spending trends
- [x] Category breakdown pie chart
- [x] Cost projections based on renewals
- **Tech:** Recharts library (implemented)

### Tags & Labels
- [ ] Custom tags for organizing contracts
- [ ] Color-coded labels
- [ ] Filter by tags
- **Tech:** New `contract_tags` junction table

### PDF Viewer
- [ ] View original PDF in-app
- [ ] Side-by-side with extracted data
- [ ] Download option
- **Tech:** react-pdf or iframe embed from Supabase Storage

### Notes & Comments
- [ ] Add personal notes to contracts
- [ ] Track negotiation history
- [ ] Attach follow-up reminders
- **Tech:** New `contract_notes` table

### Dark Mode
- [ ] Theme toggle in header
- [ ] Persist preference
- [ ] System preference detection
- **Tech:** Tailwind dark mode classes

---

## Phase 3: Growth Features

### Shared Accounts
- [ ] Invite family members or team
- [ ] Role-based permissions (view/edit/admin)
- [ ] Shared contract visibility settings
- **Tech:** Supabase RLS policies, new `teams` table

### Calendar Sync
- [ ] Export events to Google Calendar
- [ ] Export to Apple Calendar (.ics)
- [ ] Two-way sync option
- **Tech:** Google Calendar API, iCal generation

### Contract Health Score
- [ ] Overall score (0-100) per contract
- [ ] Factors: risk count, cost vs market, terms fairness
- [ ] Dashboard widget showing portfolio health
- **Tech:** Scoring algorithm in recommendations

### Bulk Upload
- [ ] Upload multiple contracts at once
- [ ] Queue-based processing
- [ ] Progress tracking
- **Tech:** Background jobs, Supabase Edge Functions

### Duplicate Detection
- [ ] Alert when uploading similar contract
- [ ] Suggest merging or replacing
- [ ] Based on provider + contract type matching
- **Tech:** Fuzzy matching on extraction

---

## Future Considerations

### E-Signature Integration
- [ ] Sign contracts via DocuSign/HelloSign
- [ ] Track signature status
- [ ] Store signed versions
- **Complexity:** High (API integrations, legal compliance)

### Mobile App (PWA)
- [ ] Installable on mobile devices
- [ ] Offline support for viewing contracts
- [ ] Push notifications for reminders
- **Tech:** Vite PWA plugin, service workers

### Contract Templates
- [ ] Generate basic contracts from templates
- [ ] NDA, service agreement, lease templates
- [ ] Fill-in-the-blank wizard
- **Complexity:** High (legal review needed)

### Market Rate Comparison
- [ ] "You're paying $X, typical is $Y"
- [ ] Benchmarks by contract type and region
- [ ] Negotiation leverage insights
- **Complexity:** High (requires data aggregation)

### Provider Ratings
- [ ] Rate providers after contract ends
- [ ] Community ratings (opt-in)
- [ ] Provider reputation scores
- **Complexity:** Medium (community features)

### Negotiation Scripts
- [ ] AI-generated talking points
- [ ] Based on contract terms and market rates
- [ ] Email templates for negotiation
- **Tech:** Gemini/Claude prompts

---

## Competitive Differentiators

These features distinguish Clausemate from enterprise CLM tools like Contractify:

| Feature | Clausemate | Enterprise CLM |
|---------|------------|----------------|
| Price | $9-29/mo | $161+/mo |
| Target | Individuals, small biz | Teams, enterprises |
| Visual Timeline | ✅ | ❌ |
| Proactive AI Insights | ✅ | Limited |
| Spending Analysis | ✅ | Basic reporting |
| Complexity | Simple | Complex workflows |
| Setup Time | Minutes | Weeks |

---

## Technical Debt & Improvements

- [ ] Add unit tests for API endpoints
- [ ] Add E2E tests with Playwright
- [ ] Implement error monitoring (Sentry)
- [ ] Add API rate limiting
- [ ] Optimize PDF processing for large files
- [ ] Add request caching for repeated extractions

---

## How to Prioritize

When choosing what to build next, consider:

1. **User Impact** - How many users benefit? How much time/money saved?
2. **Effort** - Development time, complexity, dependencies
3. **Differentiation** - Does it set us apart from competitors?
4. **Revenue** - Can it be a premium feature?

**Suggested next feature:** Email Reminders (high impact, medium effort, prevents churn)
