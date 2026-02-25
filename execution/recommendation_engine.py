"""
AI-powered recommendation engine for contract optimization.

This script analyzes a user's contracts and generates actionable
recommendations for cost savings, consolidation, and risk mitigation.
"""

import json
import re
from datetime import date, datetime, timedelta
from typing import Any

import anthropic

from execution.market_rates import get_market_comparison


ANALYSIS_PROMPT = """Analyze these contracts and generate actionable recommendations.

Contracts:
{contracts_json}

Market Rate Comparisons (if available):
{market_comparison}

Generate recommendations in the following categories:
1. cost_reduction - Contracts where the user is paying above market rates
2. consolidation - Opportunities to combine or bundle contracts
3. risk_alert - Unfavorable terms (auto-renewal traps, short cancellation windows)
4. renewal_reminder - Contracts expiring within 30 days

For each recommendation, provide:
{{
  "contract_id": "ID of the related contract (or null for general recommendations)",
  "type": "cost_reduction | consolidation | risk_alert | renewal_reminder",
  "title": "Short, actionable title (e.g., 'Switch to cheaper provider')",
  "description": "Detailed explanation with specific actions",
  "estimated_savings": "Estimated annual savings as a number, or null",
  "priority": "high | medium | low",
  "reasoning": "Why this recommendation is important",
  "confidence": "0.0 to 1.0 confidence in this recommendation"
}}

Return a JSON array of recommendations. If no recommendations apply, return an empty array [].
Return ONLY the JSON array, no additional text or markdown.
"""


def generate_recommendations(
    contracts: list[dict[str, Any]], api_key: str
) -> list[dict[str, Any]]:
    """
    Generate AI-powered recommendations for a set of contracts.

    Args:
        contracts: List of contract dictionaries from the database
        api_key: Anthropic API key

    Returns:
        List of recommendation dictionaries
    """
    if not contracts:
        return []

    # Generate renewal reminders locally (deterministic)
    recommendations = _generate_renewal_reminders(contracts)

    # Get market comparisons
    market_comparison = get_market_comparison(contracts)

    # Prepare contracts for AI analysis (remove sensitive/internal fields)
    contracts_for_analysis = []
    for c in contracts:
        contracts_for_analysis.append(
            {
                "id": c.get("id"),
                "provider_name": c.get("provider_name"),
                "contract_type": c.get("contract_type"),
                "monthly_cost": c.get("monthly_cost"),
                "annual_cost": c.get("annual_cost"),
                "currency": c.get("currency", "USD"),
                "start_date": c.get("start_date"),
                "end_date": c.get("end_date"),
                "auto_renewal": c.get("auto_renewal"),
                "cancellation_notice_days": c.get("cancellation_notice_days"),
                "key_terms": c.get("key_terms", []),
            }
        )

    # Call Claude for AI-powered analysis
    client = anthropic.Anthropic(api_key=api_key)

    prompt = ANALYSIS_PROMPT.format(
        contracts_json=json.dumps(contracts_for_analysis, indent=2, default=str),
        market_comparison=json.dumps(market_comparison, indent=2),
    )

    message = client.messages.create(
        model="claude-opus-4-20251115",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    response_text = message.content[0].text

    # Parse the response
    try:
        ai_recommendations = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to find JSON array in the response
        json_match = re.search(r"\[[\s\S]*\]", response_text)
        if json_match:
            ai_recommendations = json.loads(json_match.group())
        else:
            ai_recommendations = []

    # Merge with renewal reminders
    recommendations.extend(ai_recommendations)

    # Ensure all recommendations have required fields
    validated = []
    for rec in recommendations:
        validated.append(
            {
                "contract_id": rec.get("contract_id"),
                "type": rec.get("type", "risk_alert"),
                "title": rec.get("title", "Review this contract"),
                "description": rec.get("description", ""),
                "estimated_savings": rec.get("estimated_savings"),
                "priority": rec.get("priority", "medium"),
                "reasoning": rec.get("reasoning"),
                "confidence": rec.get("confidence", 0.5),
            }
        )

    return validated


def _generate_renewal_reminders(contracts: list[dict]) -> list[dict]:
    """Generate renewal reminder recommendations for expiring contracts."""
    reminders = []
    today = date.today()
    thirty_days = today + timedelta(days=30)

    for c in contracts:
        end_date_str = c.get("end_date")
        if not end_date_str:
            continue

        # Parse end date
        if isinstance(end_date_str, str):
            end_date = date.fromisoformat(end_date_str)
        elif isinstance(end_date_str, (date, datetime)):
            end_date = (
                end_date_str.date()
                if isinstance(end_date_str, datetime)
                else end_date_str
            )
        else:
            continue

        # Check if expiring within 30 days
        if today <= end_date <= thirty_days:
            days_left = (end_date - today).days
            reminders.append(
                {
                    "contract_id": c.get("id"),
                    "type": "renewal_reminder",
                    "title": f"{c.get('provider_name', 'Contract')} expires in {days_left} days",
                    "description": f"Your contract with {c.get('provider_name', 'this provider')} "
                    f"expires on {end_date.isoformat()}. "
                    f"{'This contract will auto-renew.' if c.get('auto_renewal') else 'Review and decide whether to renew.'}",
                    "estimated_savings": None,
                    "priority": "high" if days_left <= 7 else "medium",
                    "reasoning": "Upcoming contract expiration requires attention",
                    "confidence": 1.0,
                }
            )

    return reminders


if __name__ == "__main__":
    # Test with sample contracts
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        exit(1)

    sample_contracts = [
        {
            "id": "test-1",
            "provider_name": "Acme Insurance",
            "contract_type": "insurance",
            "monthly_cost": 150,
            "annual_cost": 1800,
            "auto_renewal": True,
            "cancellation_notice_days": 30,
            "end_date": (date.today() + timedelta(days=20)).isoformat(),
        },
        {
            "id": "test-2",
            "provider_name": "Streaming Plus",
            "contract_type": "subscription",
            "monthly_cost": 25,
            "auto_renewal": True,
            "cancellation_notice_days": 0,
        },
    ]

    recommendations = generate_recommendations(sample_contracts, api_key)
    print(json.dumps(recommendations, indent=2))
