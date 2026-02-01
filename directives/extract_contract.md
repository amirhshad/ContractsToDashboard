# Extract Contract Data

## Goal
Extract structured data from uploaded contract PDFs using Claude Vision API.

## Inputs
- PDF file (raw bytes)
- Anthropic API key

## Process
1. Encode PDF as base64
2. Send to Claude Vision API with extraction prompt
3. Parse JSON response
4. Validate and normalize extracted fields
5. Return structured ContractExtractionResult

## Script
`execution/claude_extractor.py`

## Output Fields
| Field | Type | Description |
|-------|------|-------------|
| provider_name | string | Company name of the service provider |
| contract_type | enum | insurance, utility, subscription, rental, saas, service, other |
| monthly_cost | float | Monthly cost (no currency symbol) |
| annual_cost | float | Annual cost (no currency symbol) |
| payment_frequency | enum | monthly, annual, quarterly, one-time, other |
| start_date | date | Contract start date (YYYY-MM-DD) |
| end_date | date | Contract end date (YYYY-MM-DD) |
| auto_renewal | boolean | Whether contract auto-renews |
| cancellation_notice_days | integer | Days notice required to cancel |
| key_terms | array | Important terms and conditions |
| confidence | float | 0.0-1.0 confidence in extraction accuracy |

## Edge Cases
- **Image-only PDFs**: Claude Vision handles these directly
- **Multi-page contracts**: Full document is analyzed
- **Low confidence (<0.6)**: Flag for user review
- **Missing fields**: Return null, let user fill in

## Error Handling
- If JSON parsing fails, try regex extraction
- If complete failure, return empty result with confidence 0.0
- Log errors for debugging

## Cost Considerations
- Claude API costs per token
- PDFs are tokenized by page count
- Consider caching extraction results
