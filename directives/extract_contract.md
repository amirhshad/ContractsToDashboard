# Extract Contract Data

## Goal
Extract structured data from uploaded contract PDFs using smart AI routing.

## Inputs
- 1-5 PDF files (related documents forming one contract)
- Files metadata (document types: main_agreement, sow, amendment, etc.)
- Gemini API key (primary)
- Anthropic API key (fallback)

## Smart AI Routing

```
Upload contract → Gemini 3 Flash (initial extraction)
                       ↓
              Check escalation criteria
                       ↓
              If escalation needed:
                1. Gemini 2.5 Pro (preferred)
                2. Claude Sonnet 4 (fallback)
```

### Escalation Triggers
- `contract_type` is `rental`, `insurance`, or `service` (complex legal terms)
- `confidence` < 0.7
- `complexity` == "high"
- 6+ key terms detected

## Process
1. Parse multipart form data to extract files
2. Run security checks (prompt injection detection in filenames)
3. Send to Gemini 3 Flash with unified extraction prompt
4. Parse and validate JSON response
5. Check if escalation needed based on confidence/complexity
6. If escalation: re-extract with Gemini 2.5 Pro (or Claude fallback)
7. Validate output structure against expected schema
8. Normalize fields (currency, dates, severities)
9. Return structured ExtractionResult

## API Endpoint
`POST /api/upload/extract`

## Output Fields
| Field | Type | Description |
|-------|------|-------------|
| provider_name | string | Company name of the service provider |
| contract_nickname | string | Short descriptive name (e.g., "Office Lease 2025") |
| contract_type | enum | insurance, utility, subscription, rental, saas, service, other |
| monthly_cost | float | Monthly cost (no currency symbol) |
| annual_cost | float | Annual cost (no currency symbol) |
| currency | enum | USD, EUR, GBP, CAD, AUD, JPY |
| payment_frequency | enum | monthly, annual, quarterly, one-time, other |
| start_date | date | Contract start date (YYYY-MM-DD) |
| end_date | date | Contract end date (YYYY-MM-DD) |
| auto_renewal | boolean | Whether contract auto-renews |
| cancellation_notice_days | integer | Days notice required to cancel |
| key_terms | array | Concise bullet points (10-15 words each) |
| parties | array | [{name, role}] - All contract parties |
| risks | array | [{title, description, severity}] - Identified risks |
| confidence | float | 0.0-1.0 confidence in extraction accuracy |
| complexity | enum | low, medium, high |
| complexity_reasons | array | Why complexity is high (if applicable) |
| documents_analyzed | array | [{filename, document_type, summary}] |
| escalated | boolean | Whether escalation was triggered |
| escalation_model | string | Model used for escalation (if any) |

## Key Terms Format
Concise, scannable bullet points:
- "Rent increase: CPI + up to 5% additional (Art. 5.2)"
- "Cancellation: 30 days notice, 2 months penalty (Sec. 12.3)"
- "Auto-renewal: 12 months unless 60 days notice"

## Security Measures
- **Prompt hardening**: AI instructions include security notice about untrusted input
- **Injection detection**: Scans filenames for known injection patterns
- **Output validation**: Validates response structure matches expected schema
- **Suspicious content flagging**: Adds high-severity risk if manipulation detected
- **Confidence reduction**: Lowers confidence when security issues found

## Risk Categories Checked
- Auto-renewal with short/no cancellation window
- Automatic price increases or escalation clauses
- Liability limitations that favor provider
- Data retention or privacy concerns
- Termination penalties or early exit fees
- Long lock-in periods without flexibility

## Edge Cases
- **Image-only PDFs**: Gemini Vision handles these directly
- **Multi-document contracts**: All documents analyzed together
- **Low confidence (<0.6)**: Flag for user review
- **Missing fields**: Return null, let user fill in
- **Prompt injection attempt**: Flag with security warning, reduce confidence

## Error Handling
- If JSON parsing fails, try stripping markdown code blocks
- If Gemini Pro fails, fallback to Claude Sonnet 4
- If complete failure, return error with stack trace
- Log errors for debugging
