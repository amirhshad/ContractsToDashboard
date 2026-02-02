"""Unified extraction prompts for contract analysis."""

UNIFIED_EXTRACTION_PROMPT = """You are analyzing contract documents to extract structured data.
You may receive 1 to 5 related documents that together form a single contractual relationship.

IMPORTANT INSTRUCTIONS:
1. Analyze ALL provided documents together as one contract package
2. Extract a UNIFIED view combining information from all documents
3. If documents have conflicting terms, use the most recent/specific version
4. Amendments and SOWs typically override terms in the main agreement
5. Combine costs if multiple documents specify separate fees
6. Return ONLY valid JSON - no markdown, no explanation, no code blocks

REQUIRED OUTPUT FORMAT:
{
    "provider_name": "Company/service provider name (string or null)",
    "contract_type": "insurance | utility | subscription | rental | saas | service | other",
    "monthly_cost": 0.00,
    "annual_cost": 0.00,
    "currency": "USD | EUR | GBP | CAD | AUD | JPY (detect from document)",
    "payment_frequency": "monthly | annual | quarterly | one-time | other",
    "start_date": "YYYY-MM-DD or null",
    "end_date": "YYYY-MM-DD or null",
    "auto_renewal": true | false | null,
    "cancellation_notice_days": 0,
    "key_terms": ["Important terms from ALL documents"],
    "parties": [
        {
            "name": "Full legal name of party",
            "role": "provider | client | insurer | insured | landlord | tenant | licensor | licensee | vendor | customer"
        }
    ],
    "risks": [
        {
            "title": "Short risk title",
            "description": "Why this is a risk and what to watch for",
            "severity": "high | medium | low"
        }
    ],
    "confidence": 0.0-1.0,
    "documents_analyzed": [
        {
            "filename": "original filename",
            "document_type": "main_agreement | sow | terms_conditions | amendment | addendum | exhibit | schedule | other",
            "summary": "One sentence summary"
        }
    ]
}

RISK CATEGORIES TO CHECK:
- Auto-renewal with short/no cancellation window
- Automatic price increases or escalation clauses
- Liability limitations that favor provider
- Data retention or privacy concerns
- Termination penalties or early exit fees
- Long lock-in periods without flexibility
- Unusual indemnification requirements
- Missing SLA or service guarantees
- Ambiguous scope of services

CONTRACT TYPE GUIDANCE:
- insurance: Health, auto, home, liability policies
- utility: Electric, gas, water, internet, phone
- subscription: Streaming, magazines, memberships
- rental: Real estate leases, equipment rental
- saas: Software subscriptions, cloud services
- service: Consulting, maintenance, professional services
- other: Anything that doesn't fit above

FIELD EXTRACTION RULES:
1. provider_name: Main company providing the service (not the customer)
2. parties: Extract ALL parties (usually 2+), identify their contractual roles
3. costs: Convert to numbers only (no currency symbols). Detect currency separately.
4. dates: Always use YYYY-MM-DD format
5. confidence: 0.9+ for clear documents, 0.6-0.8 for partial info, <0.6 for unclear
6. key_terms: Include renewal terms, limitations, important obligations, SLAs

Return ONLY the JSON object. Do not include any other text."""
