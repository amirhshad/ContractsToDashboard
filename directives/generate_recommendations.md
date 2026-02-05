# Generate Recommendations

## Goal
Analyze user's NEW contracts and generate actionable AI-powered recommendations.

## Inputs
- List of user's contracts (from database)
- Existing recommendations (to filter out already-analyzed contracts)
- Gemini API key (primary)
- Anthropic API key (fallback)

## AI Provider Priority
1. Gemini 3 Flash (primary, cost-effective)
2. Claude Sonnet 4 (fallback if Gemini unavailable)

## Process
1. Fetch all user's contracts from database
2. Get contract IDs that already have recommendations
3. Filter to only NEW contracts (not yet analyzed)
4. If no new contracts, return empty array
5. Build contracts summary with key fields
6. Send to Gemini for analysis
7. Parse and validate recommendations JSON
8. Store new recommendations in database
9. Return inserted recommendations

## API Endpoint
`POST /api/recommendations/generate`

## Important Behavior
- **Only analyzes NEW contracts** - contracts without existing recommendations
- **Does NOT delete old recommendations** - preserves history
- **Each recommendation links to a specific contract_id**

## Recommendation Types

### 1. cost_reduction
Opportunities to reduce spending.
- Compare against typical market rates
- Identify unused services
- Suggest negotiation points
- Estimate potential savings

### 2. consolidation
Opportunities to combine or bundle contracts.
- Multiple contracts with same provider
- Similar services that could be bundled
- Insurance bundle opportunities

### 3. risk_alert
Unfavorable contract terms requiring attention.
- Auto-renewal with short cancellation window
- Unusual penalty clauses
- Automatic price increases / escalation clauses
- Long lock-in periods
- Missing SLA guarantees
- Liability concerns

### 4. renewal_reminder
Contracts expiring soon that need action.
- Within 30 days: high priority
- Within 60 days: medium priority
- Auto-renewal approaching cancellation deadline

## Output Fields
| Field | Type | Description |
|-------|------|-------------|
| contract_id | uuid | Related contract ID (required) |
| type | enum | cost_reduction, consolidation, risk_alert, renewal_reminder |
| title | string | Short, actionable title |
| description | string | Detailed explanation with action steps |
| estimated_savings | float | Annual savings estimate (or null) |
| priority | enum | high, medium, low |
| reasoning | string | Why this recommendation matters |

## Priority Assignment
- **high**: Expiring within 7 days, cancellation deadline approaching, major risk
- **medium**: Expiring within 30 days, moderate savings potential
- **low**: General optimization opportunities, awareness items

## Database Schema
```sql
recommendations (
  id uuid primary key,
  user_id uuid references auth.users,
  contract_id uuid references contracts,
  type text,
  title text,
  description text,
  estimated_savings numeric,
  priority text,
  reasoning text,
  status text default 'pending',  -- pending, viewed, completed, dismissed
  created_at timestamp
)
```

## Recommendation Generation per Contract
- Generate 2-5 specific, actionable recommendations per new contract
- Focus on:
  1. Risk alerts from key_terms analysis
  2. Renewal/deadline awareness
  3. Cost optimization opportunities
  4. Important clause awareness

## Edge Cases
- **No contracts**: Return empty array
- **All contracts already analyzed**: Return empty array
- **Single new contract**: Focus on that contract's terms and risks
- **AI failure**: Return error, don't corrupt existing recommendations

## Status Workflow
1. `pending` - Newly generated, not yet seen by user
2. `viewed` - User has seen it
3. `completed` - User took action
4. `dismissed` - User chose to ignore
