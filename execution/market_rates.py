"""
Market rate benchmarks for contract comparison.

This module provides baseline market rates for common contract types
to help identify potential cost savings. In production, this could
be enhanced with real-time pricing APIs.
"""

from typing import Any

# Market rate benchmarks (USD/month)
# Format: category -> {low, median, high} per unit
MARKET_RATES = {
    "insurance": {
        "auto": {"low": 80, "median": 130, "high": 200, "unit": "per vehicle"},
        "home": {"low": 100, "median": 150, "high": 250, "unit": "per property"},
        "renters": {"low": 15, "median": 25, "high": 40, "unit": "per policy"},
        "health": {"low": 300, "median": 500, "high": 800, "unit": "per person"},
    },
    "utility": {
        "electricity": {"low": 80, "median": 120, "high": 200, "unit": "per household"},
        "gas": {"low": 40, "median": 80, "high": 150, "unit": "per household"},
        "water": {"low": 30, "median": 50, "high": 80, "unit": "per household"},
        "internet": {"low": 40, "median": 70, "high": 120, "unit": "per connection"},
        "phone": {"low": 30, "median": 60, "high": 100, "unit": "per line"},
    },
    "subscription": {
        "streaming": {"low": 8, "median": 15, "high": 25, "unit": "per service"},
        "music": {"low": 5, "median": 10, "high": 15, "unit": "per service"},
        "news": {"low": 5, "median": 15, "high": 30, "unit": "per publication"},
        "fitness": {"low": 20, "median": 50, "high": 100, "unit": "per membership"},
        "software": {"low": 10, "median": 30, "high": 100, "unit": "per license"},
    },
    "saas": {
        "crm": {"low": 25, "median": 75, "high": 150, "unit": "per user"},
        "storage": {"low": 5, "median": 12, "high": 25, "unit": "per TB"},
        "productivity": {"low": 10, "median": 20, "high": 50, "unit": "per user"},
        "email": {"low": 5, "median": 12, "high": 25, "unit": "per user"},
        "analytics": {"low": 50, "median": 150, "high": 500, "unit": "per account"},
    },
    "rental": {
        "apartment": {"low": 1000, "median": 1800, "high": 3500, "unit": "per unit"},
        "storage": {"low": 50, "median": 100, "high": 200, "unit": "per unit"},
        "equipment": {"low": 100, "median": 300, "high": 800, "unit": "per item"},
        "vehicle": {"low": 300, "median": 500, "high": 900, "unit": "per vehicle"},
    },
}


def get_market_comparison(contracts: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Compare contracts against market rate benchmarks.

    Args:
        contracts: List of contract dictionaries

    Returns:
        Dictionary with market comparisons for each contract
    """
    comparisons = {}

    for contract in contracts:
        contract_id = contract.get("id")
        contract_type = contract.get("contract_type")
        monthly_cost = contract.get("monthly_cost")

        if not contract_id or not contract_type or not monthly_cost:
            continue

        # Get market rates for this contract type
        type_rates = MARKET_RATES.get(contract_type, {})

        if not type_rates:
            comparisons[contract_id] = {
                "status": "no_benchmark",
                "message": f"No market benchmarks available for {contract_type}",
            }
            continue

        # Find the best matching subcategory based on provider name
        provider_name = (contract.get("provider_name") or "").lower()
        best_match = None
        best_score = 0

        for subcategory, rates in type_rates.items():
            # Simple keyword matching
            if subcategory in provider_name:
                best_match = (subcategory, rates)
                best_score = 2
            elif best_score < 1:
                best_match = (subcategory, rates)
                best_score = 1

        if not best_match:
            comparisons[contract_id] = {
                "status": "no_match",
                "message": f"Could not match to specific {contract_type} subcategory",
            }
            continue

        subcategory, rates = best_match
        monthly_cost = float(monthly_cost)

        # Compare to benchmark
        if monthly_cost < rates["low"]:
            status = "below_market"
            savings_potential = 0
        elif monthly_cost <= rates["median"]:
            status = "competitive"
            savings_potential = 0
        elif monthly_cost <= rates["high"]:
            status = "above_median"
            savings_potential = monthly_cost - rates["median"]
        else:
            status = "significantly_above"
            savings_potential = monthly_cost - rates["median"]

        comparisons[contract_id] = {
            "status": status,
            "subcategory": subcategory,
            "your_cost": monthly_cost,
            "market_low": rates["low"],
            "market_median": rates["median"],
            "market_high": rates["high"],
            "unit": rates["unit"],
            "potential_monthly_savings": round(savings_potential, 2),
            "potential_annual_savings": round(savings_potential * 12, 2),
        }

    return comparisons


def get_all_benchmarks() -> dict[str, Any]:
    """Return all market rate benchmarks."""
    return MARKET_RATES


if __name__ == "__main__":
    # Test with sample contracts
    sample_contracts = [
        {
            "id": "1",
            "provider_name": "State Farm Auto Insurance",
            "contract_type": "insurance",
            "monthly_cost": 180,
        },
        {
            "id": "2",
            "provider_name": "Netflix Streaming",
            "contract_type": "subscription",
            "monthly_cost": 22,
        },
        {
            "id": "3",
            "provider_name": "Comcast Internet",
            "contract_type": "utility",
            "monthly_cost": 95,
        },
    ]

    import json

    result = get_market_comparison(sample_contracts)
    print(json.dumps(result, indent=2))
