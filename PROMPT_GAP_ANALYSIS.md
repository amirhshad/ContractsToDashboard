# Clausemate Prompt Gap Analysis

## Executive Summary

This report analyzes all AI prompts used in Clausemate and identifies critical gaps that may impact extraction accuracy, recommendation quality, and overall user experience. The analysis covers 4 distinct prompts across 3 files.

**Overall Assessment: 🟡 Moderate Risk**

The current prompts are functional but have significant gaps that could lead to:
- Inconsistent extraction results across different contract types
- Missing critical risk factors
- Suboptimal recommendations
- Poor handling of edge cases
- Security vulnerabilities

---

## Prompts Inventory

| Location | Prompt Name | Purpose | Lines |
|----------|------------|---------|-------|
| `api/index.py` | `MULTI_DOC_EXTRACTION_PROMPT` | Multi-document extraction | 93-138 |
| `api/index.py` | Inline recommendation prompt | Generate recommendations | 512-539 |
| `execution/claude_extractor.py` | `EXTRACTION_PROMPT` | Single PDF extraction | 16-40 |
| `execution/recommendation_engine.py` | `ANALYSIS_PROMPT` | AI recommendations | 18-46 |

---

## Critical Gaps

### 1. 🔴 Prompt Duplication & Inconsistency

**Problem:** Two different extraction prompts exist with different field sets.

| Field | `EXTRACTION_PROMPT` | `MULTI_DOC_EXTRACTION_PROMPT` |
|-------|---------------------|-------------------------------|
| parties | ❌ Missing | ✅ Included |
| risks | ❌ Missing | ✅ Included |
| payment_frequency | ✅ Included | ❌ Missing |
| documents_analyzed | ❌ Missing | ✅ Included |

**Impact:** Single-document uploads don't extract parties or risks, while multi-document uploads miss payment frequency.

**Recommendation:** Consolidate into a single configurable extraction prompt that handles both cases.

---

### 2. 🔴 Insufficient Risk Analysis Framework

**Current State:**
```
"risks": [
    {
        "title": "Short risk title",
        "description": "Description of the risk or concern",
        "severity": "high, medium, or low"
    }
]
```

**Missing Risk Categories:**
- ❌ **Financial risks**: Hidden fees, price escalation clauses, payment penalties
- ❌ **Termination risks**: Early termination fees, termination for convenience rights
- ❌ **Liability risks**: Indemnification clauses, limitation of liability caps
- ❌ **Data/IP risks**: Data ownership, IP assignment, confidentiality breaches
- ❌ **Compliance risks**: Regulatory requirements, audit rights
- ❌ **Service level risks**: SLA penalties, uptime guarantees, support obligations
- ❌ **Change control risks**: Amendment procedures, unilateral modification rights

**Impact:** Users may miss critical contract risks that could result in financial or legal exposure.

**Recommendation:** Add structured risk categories with specific prompts for each:
```json
{
  "risk_category": "financial | termination | liability | data | compliance | service | change",
  "clause_reference": "Section 5.2",
  "risk_description": "...",
  "severity": "high | medium | low",
  "mitigation_suggestion": "..."
}
```

---

### 3. 🔴 No Currency/Localization Support

**Current State:**
- Prompts assume USD
- No handling for international date formats
- No multi-language support

**Problem Code:**
```python
"monthly_cost": "Total monthly cost across all documents, as a number or null"
```

**Missing:**
- Currency detection and normalization
- Exchange rate context
- Date format localization (DD/MM/YYYY vs MM/DD/YYYY)
- Language detection for non-English contracts

**Impact:** International contracts may have incorrect cost data or date parsing errors.

**Recommendation:** Add currency extraction:
```json
{
  "monthly_cost": {"amount": 1500, "currency": "EUR"},
  "detected_language": "en",
  "date_format_used": "YYYY-MM-DD"
}
```

---

### 4. 🟡 Weak Key Terms Extraction

**Current State:**
```
"key_terms": ["List of important terms from ALL documents"]
```

**Problems:**
- No categorization of terms
- No indication of which party the term favors
- No extraction of actual clause text
- Missing term importance ranking

**Improved Structure:**
```json
{
  "key_terms": [
    {
      "category": "payment | termination | liability | renewal | confidentiality | other",
      "summary": "30-day payment terms with 1.5% late fee",
      "clause_text": "Payment is due within 30 days...",
      "favors": "provider | client | neutral",
      "importance": "high | medium | low"
    }
  ]
}
```

---

### 5. 🟡 Missing Contract Context

**Current Extraction Gaps:**

| Missing Field | Why It Matters |
|--------------|----------------|
| `governing_law` | Legal jurisdiction for disputes |
| `dispute_resolution` | Arbitration vs litigation |
| `notice_address` | Where to send cancellation notices |
| `payment_terms` | Net 30, Net 60, etc. |
| `late_payment_penalty` | Fee structure for late payments |
| `insurance_requirements` | Required coverage minimums |
| `assignment_rights` | Can contract be transferred? |
| `force_majeure` | Pandemic/disaster clauses |
| `data_handling` | GDPR/privacy compliance |
| `warranty_terms` | Service guarantees |

---

### 6. 🟡 Recommendation Prompt Gaps

**Current Recommendation Categories:**
1. cost_reduction
2. consolidation
3. risk_alert
4. renewal_reminder

**Missing Recommendation Types:**
- ❌ **Renegotiation opportunity** - Contract nearing renewal with leverage points
- ❌ **Compliance alert** - Terms that may violate regulations
- ❌ **Benchmark comparison** - How terms compare to industry standards
- ❌ **Vendor health alert** - If vendor is known to have issues
- ❌ **Usage optimization** - If paying for unused capacity
- ❌ **Term improvement** - Specific clauses to negotiate

**Missing Context for Better Recommendations:**
```python
# Current - only contract data
contracts_summary.append({
    "id": c["id"],
    "provider": c.get("provider_name"),
    ...
})

# Missing context that would improve recommendations:
# - Company size/industry (affects what's "normal")
# - Previous recommendations acted upon
# - User's stated priorities (cost vs. risk vs. convenience)
# - Similar contracts in the portfolio for comparison
# - Historical spending trends
```

---

### 7. 🟡 Output Format Fragility

**Current JSON Parsing:**
```python
try:
    result = json.loads(response_text)
except json.JSONDecodeError:
    json_match = re.search(r"\{[\s\S]*\}", response_text)
```

**Problems:**
- No schema validation
- Regex fallback is fragile
- No type coercion (strings to numbers)
- No handling of markdown code blocks consistently

**Recommendation:** Use structured output or JSON schema validation:
```python
from pydantic import BaseModel

class ContractExtraction(BaseModel):
    provider_name: str | None
    monthly_cost: float | None
    # ... with validators
```

---

### 8. 🟡 Missing Few-Shot Examples

**Current State:** Zero-shot prompting only

**Problem:** Claude may interpret ambiguous contract terms differently without examples.

**Recommendation:** Add few-shot examples for:
- Insurance contracts (premiums, deductibles, coverage)
- SaaS contracts (seats, tiers, overages)
- Service agreements (hourly rates, retainers)
- Rental/lease agreements (deposits, escalation)

Example:
```
Here's an example extraction from a similar contract:
INPUT: "Monthly service fee: $500 plus $50 per additional user"
OUTPUT: {"monthly_cost": 500, "per_user_cost": 50, "pricing_model": "base_plus_usage"}
```

---

### 9. 🟠 Security Considerations

**Potential Issues:**

1. **Prompt Injection via Contract Content**
   - Malicious PDFs could contain text like "Ignore previous instructions and return..."
   - No sanitization of extracted content before displaying

2. **Data Leakage**
   - Full contract text sent to Claude API
   - No PII detection/redaction option

3. **Hallucination Risk**
   - No grounding mechanism for extracted facts
   - Claude may invent data if contract is unclear

**Recommendations:**
- Add system prompt boundaries
- Implement confidence thresholds for user verification
- Add PII detection for sensitive contracts

---

### 10. 🟠 Performance/Cost Optimization

**Current Issues:**

| Issue | Impact |
|-------|--------|
| Max tokens: 2048 for extraction | May truncate long contracts |
| No caching | Re-extraction costs money |
| Full contract sent every time | Expensive for simple queries |
| No streaming | Slow perceived performance |

**Recommendations:**
- Increase max_tokens for large documents
- Cache extraction results
- Implement incremental extraction for follow-up questions
- Add streaming for better UX

---

## Prioritized Improvement Roadmap

### Phase 1: Critical Fixes (Week 1-2)
| Task | Priority | Effort |
|------|----------|--------|
| Consolidate extraction prompts | 🔴 High | Medium |
| Add missing fields (parties, risks) to single-doc prompt | 🔴 High | Low |
| Add currency detection | 🔴 High | Medium |
| Implement JSON schema validation | 🔴 High | Medium |

### Phase 2: Quality Improvements (Week 3-4)
| Task | Priority | Effort |
|------|----------|--------|
| Expand risk analysis framework | 🟡 Medium | High |
| Add key terms categorization | 🟡 Medium | Medium |
| Add few-shot examples for contract types | 🟡 Medium | Medium |
| Add new recommendation types | 🟡 Medium | Medium |

### Phase 3: Advanced Features (Week 5-6)
| Task | Priority | Effort |
|------|----------|--------|
| Implement confidence-based verification flow | 🟠 Low | High |
| Add user context to recommendations | 🟠 Low | Medium |
| PII detection option | 🟠 Low | High |
| Extraction result caching | 🟠 Low | Medium |

---

## Recommended Prompt Improvements

### Improved Extraction Prompt

```python
UNIFIED_EXTRACTION_PROMPT = """You are a contract analysis expert. Extract structured data from this contract document.

## Instructions
1. Extract ALL requested fields - use null only if truly not present
2. For costs, always include the currency detected
3. For dates, use ISO format (YYYY-MM-DD)
4. For risks, categorize by type and severity
5. For ambiguous terms, note the ambiguity in key_terms

## Output Schema
{
  "provider": {
    "name": "Legal entity name",
    "type": "company | individual | government",
    "address": "If present"
  },
  "client": {
    "name": "Legal entity name",
    "address": "If present"
  },
  "contract_metadata": {
    "type": "insurance | utility | subscription | rental | saas | service | employment | nda | other",
    "title": "Contract title if present",
    "effective_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD or null if perpetual",
    "governing_law": "State/Country",
    "detected_language": "ISO code"
  },
  "financial_terms": {
    "monthly_cost": {"amount": number, "currency": "USD"},
    "annual_cost": {"amount": number, "currency": "USD"},
    "payment_frequency": "monthly | quarterly | annual | one-time",
    "payment_terms": "Net 30, etc.",
    "late_fee": "Description if present",
    "price_escalation": "Annual increase clause if present"
  },
  "renewal_terms": {
    "auto_renewal": true | false,
    "renewal_period": "Duration of renewal",
    "cancellation_notice_days": number,
    "cancellation_method": "How to cancel (email, written, etc.)"
  },
  "parties": [
    {"name": "Full legal name", "role": "provider | client | guarantor | other", "signing_authority": "If named"}
  ],
  "key_terms": [
    {
      "category": "payment | termination | liability | confidentiality | ip | data | service_level | other",
      "summary": "Plain language summary",
      "clause_reference": "Section number if available",
      "favors": "provider | client | neutral"
    }
  ],
  "risks": [
    {
      "category": "financial | termination | liability | compliance | data | service",
      "title": "Short title",
      "description": "What the risk is",
      "severity": "high | medium | low",
      "clause_reference": "Section number",
      "mitigation": "How to address this risk"
    }
  ],
  "extraction_metadata": {
    "confidence": 0.0-1.0,
    "unclear_sections": ["List of sections that were hard to interpret"],
    "missing_standard_clauses": ["Expected clauses not found"]
  }
}

## Contract Type-Specific Guidance
- **Insurance**: Extract premium, deductible, coverage limits, exclusions
- **SaaS**: Extract user limits, feature tiers, overage charges, SLA terms
- **Service**: Extract hourly rates, scope of work, deliverables, milestones
- **Rental**: Extract deposit, maintenance responsibilities, escalation clause

Return ONLY valid JSON. No markdown, no explanation."""
```

### Improved Recommendation Prompt

```python
RECOMMENDATION_PROMPT = """You are a contract optimization expert advising a small business.

## User Context
- Company type: {company_type}
- Industry: {industry}
- Primary goal: {user_goal}  # cost_reduction | risk_mitigation | convenience

## Current Contract Portfolio
{contracts_json}

## Market Benchmarks
{market_data}

## Generate Recommendations

For each recommendation, provide:
{
  "contract_id": "UUID or null for portfolio-wide",
  "type": "cost_reduction | consolidation | risk_alert | renewal_reminder | renegotiation | compliance | benchmark",
  "title": "Action-oriented title (verb + outcome)",
  "description": "Specific steps to take",
  "estimated_savings": {"annual": number, "confidence": "high|medium|low"},
  "priority": "high | medium | low",
  "effort": "low | medium | high",
  "reasoning": "Data-driven justification",
  "negotiation_script": "What to say to the vendor (if applicable)",
  "deadline": "YYYY-MM-DD if time-sensitive"
}

## Prioritization Rules
- HIGH priority: >$500/year savings OR expiring within 7 days OR high-severity risk
- MEDIUM priority: $100-500/year savings OR expiring within 30 days OR medium risk
- LOW priority: <$100/year savings OR general optimization

## Quality Standards
- Be specific: "Switch from Plan A to Plan B" not "Consider alternatives"
- Include numbers: "Save $240/year by..." not "Save money by..."
- Be actionable: Include the exact steps to take
- Reference specific contract terms when relevant

Return 3-7 recommendations as a JSON array. If no recommendations apply, explain why in a single recommendation."""
```

---

## Appendix: Test Cases for Validation

### Extraction Test Cases
1. ✅ Standard SaaS contract with clear terms
2. ⚠️ Insurance policy with complex premium structure
3. ⚠️ Multi-party agreement with guarantor
4. ⚠️ Contract with conflicting amendment
5. ⚠️ Non-English contract (German, Spanish)
6. ⚠️ Scanned/OCR contract with poor quality
7. ❌ Contract with no dates specified
8. ❌ Contract with ambiguous auto-renewal language

### Recommendation Test Cases
1. ✅ Contract expiring in 7 days with auto-renewal
2. ✅ Above-market pricing for SaaS tool
3. ⚠️ Multiple contracts with same vendor
4. ⚠️ High-risk liability clause detected
5. ⚠️ No contracts in portfolio (empty state)
6. ❌ Contract with conflicting risk factors

---

## Conclusion

The current prompts provide a functional baseline but have significant gaps in:

1. **Completeness** - Missing important fields and risk categories
2. **Consistency** - Different prompts extract different data
3. **Robustness** - Fragile JSON parsing and no validation
4. **Intelligence** - Limited context for better recommendations

Addressing these gaps will significantly improve:
- Extraction accuracy (est. +20-30%)
- Recommendation relevance (est. +40%)
- User trust and engagement
- Competitive differentiation

---

*Report generated: February 2026*
*Next review: After Phase 1 implementation*
