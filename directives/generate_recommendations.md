# Generate Recommendations

## Goal
Analyze user's contracts and generate actionable AI-powered recommendations.

## Inputs
- List of user's contracts (from database)
- Anthropic API key

## Process
1. Generate renewal reminders (deterministic, local)
2. Get market rate comparisons from `execution/market_rates.py`
3. Send contracts + market data to Claude for analysis
4. Parse and validate recommendations
5. Merge all recommendations
6. Store in database

## Script
`execution/recommendation_engine.py`

## Recommendation Types

### 1. cost_reduction
Contracts where user is paying above market rates.
- Compare against `market_rates.py` benchmarks
- Estimate potential savings
- Suggest alternatives

### 2. consolidation
Opportunities to combine or bundle contracts.
- Multiple contracts with same provider
- Similar services that could be bundled
- Insurance bundle opportunities

### 3. risk_alert
Unfavorable contract terms.
- Auto-renewal with short cancellation window
- Unusual penalty clauses
- Automatic price increases
- Long lock-in periods

### 4. renewal_reminder
Contracts expiring soon.
- Within 30 days: high priority
- Within 60 days: medium priority
- Auto-renewal warnings

## Output Fields
| Field | Type | Description |
|-------|------|-------------|
| contract_id | string | Related contract ID (or null) |
| type | enum | cost_reduction, consolidation, risk_alert, renewal_reminder |
| title | string | Short, actionable title |
| description | string | Detailed explanation with actions |
| estimated_savings | float | Annual savings estimate (or null) |
| priority | enum | high, medium, low |
| reasoning | string | Why this recommendation matters |
| confidence | float | 0.0-1.0 confidence level |

## Priority Assignment
- **high**: Expiring within 7 days, potential savings >$500/year
- **medium**: Expiring within 30 days, potential savings $100-500/year
- **low**: General optimization opportunities

## Edge Cases
- No contracts: Return empty array
- Single contract: Focus on cost comparison and term review
- Expired contracts: Skip or mark for cleanup

## Market Rate Updates
- Currently using static benchmarks in `market_rates.py`
- Future: Integrate with pricing APIs
- Update benchmarks quarterly
