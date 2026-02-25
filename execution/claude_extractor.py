"""
Contract data extraction using Claude Vision API.

This script extracts structured data from contract PDFs using Claude's
vision capabilities to analyze the document directly.
"""

import base64
import json
import re
from typing import Any

import anthropic


EXTRACTION_PROMPT = """Analyze this contract document and extract the following information.
Return your response as valid JSON only, with no additional text.

Extract these fields:
{
  "provider_name": "Company name of the service provider (string or null)",
  "contract_type": "One of: insurance, utility, subscription, rental, saas, service, other (or null)",
  "monthly_cost": "Monthly cost as a number (no currency symbol), or null",
  "annual_cost": "Annual cost as a number (no currency symbol), or null",
  "payment_frequency": "One of: monthly, annual, quarterly, one-time, other (or null)",
  "start_date": "Contract start date in YYYY-MM-DD format, or null",
  "end_date": "Contract end date in YYYY-MM-DD format, or null",
  "auto_renewal": "true if contract auto-renews, false if not, or null if unclear",
  "cancellation_notice_days": "Number of days notice required to cancel (integer), or null",
  "key_terms": ["List of important terms, conditions, or clauses as strings"],
  "parties": [{"name": "Full name of party", "role": "Role (provider, client, insurer, insured, landlord, tenant, etc.)"}],
  "risks": [{"title": "Short risk title", "description": "Description of the risk", "severity": "high, medium, or low"}],
  "confidence": "Your confidence in the extraction accuracy from 0.0 to 1.0"
}

Important:
- If a field cannot be determined from the document, use null for simple fields, [] for arrays
- For costs, extract only the numeric value without currency symbols
- For dates, use ISO format YYYY-MM-DD
- For confidence, estimate based on document clarity and how many fields you could extract
- Return ONLY the JSON object, no markdown formatting or explanation
"""

FULL_TEXT_PROMPT = """Extract ALL text content from this contract document.
- Return the complete text, preserving paragraph structure
- Include all sections, clauses, headers, and details
- Do NOT summarize - return as much original text as possible
- Format as a clean, readable text version of the document

Return as JSON:
{
  "full_text": "the complete extracted text here..."
}"""


def extract_full_text(pdf_bytes: bytes, api_key: str) -> str:
    """Extract full text from a PDF using Claude Vision API."""
    client = anthropic.Anthropic(api_key=api_key)

    # Encode PDF as base64
    pdf_base64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    # Call Claude with the PDF
    message = client.messages.create(
        model="claude-opus-4-20251115",
        max_tokens=8192,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": FULL_TEXT_PROMPT,
                    },
                ],
            }
        ],
    )

    response_text = message.content[0].text

    # Try to extract JSON
    try:
        data = json.loads(response_text)
        return data.get("full_text", "")
    except json.JSONDecodeError:
        # Try to find JSON in response
        json_match = re.search(r'\{"full_text":\s*"(.+?)"\}', response_text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        return response_text  # Return raw text as fallback


def extract_contract_data(pdf_bytes: bytes, api_key: str) -> dict[str, Any]:
    """
    Extract structured contract data from a PDF using Claude Vision API.

    Args:
        pdf_bytes: Raw PDF file bytes
        api_key: Anthropic API key

    Returns:
        Dictionary containing extracted contract data
    """
    client = anthropic.Anthropic(api_key=api_key)

    # Encode PDF as base64
    pdf_base64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

    # Call Claude with the PDF
    message = client.messages.create(
        model="claude-opus-4-20251115",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": EXTRACTION_PROMPT,
                    },
                ],
            }
        ],
    )

    # Parse the response
    response_text = message.content[0].text

    # Try to extract JSON from the response
    try:
        # First try direct JSON parse
        result = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to find JSON in the response (might have markdown formatting)
        json_match = re.search(r"\{[\s\S]*\}", response_text)
        if json_match:
            result = json.loads(json_match.group())
        else:
            # Return empty result with low confidence
            result = {
                "provider_name": None,
                "contract_type": None,
                "monthly_cost": None,
                "annual_cost": None,
                "payment_frequency": None,
                "start_date": None,
                "end_date": None,
                "auto_renewal": None,
                "cancellation_notice_days": None,
                "key_terms": [],
                "parties": [],
                "risks": [],
                "confidence": 0.0,
            }

    # Ensure all expected fields exist
    defaults = {
        "provider_name": None,
        "contract_type": None,
        "monthly_cost": None,
        "annual_cost": None,
        "payment_frequency": None,
        "start_date": None,
        "end_date": None,
        "auto_renewal": None,
        "cancellation_notice_days": None,
        "key_terms": [],
        "parties": [],
        "risks": [],
        "confidence": 0.0,
        "full_text": "",
    }

    for key, default in defaults.items():
        if key not in result:
            result[key] = default

    return result


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[dict]:
    """
    Split text into overlapping chunks for RAG.
    
    Args:
        text: Full text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters between chunks
    
    Returns:
        List of chunks with text and metadata
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    chunk_index = 0
    
    while start < text_length:
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < text_length:
            # Look for sentence endings near chunk boundary
            for punct in ['. ', '! ', '? ', '\n']:
                last_punct = text.rfind(punct, start, end)
                if last_punct > start + chunk_size // 2:
                    end = last_punct + 1
                    break
        
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "index": chunk_index,
                "char_start": start,
                "char_end": min(end, text_length)
            })
            chunk_index += 1
        
        start = end - overlap
        if start <= 0:
            break
    
    return chunks


def extract_contract_with_rag(pdf_bytes: bytes, api_key: str) -> dict[str, Any]:
    """
    Extract contract data including full text for RAG.
    
    Args:
        pdf_bytes: Raw PDF file bytes
        api_key: Anthropic API key
    
    Returns:
        Dictionary with extracted data + full_text + chunks
    """
    # First extract structured data
    result = extract_contract_data(pdf_bytes, api_key)
    
    # Then extract full text
    full_text = extract_full_text(pdf_bytes, api_key)
    result["full_text"] = full_text
    
    # Create chunks
    chunks = chunk_text(full_text)
    result["chunks"] = chunks
    
    return result


if __name__ == "__main__":
    # Test with a sample PDF
    import sys
    import os
    from dotenv import load_dotenv

    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: python claude_extractor.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    result = extract_contract_data(pdf_bytes, api_key)
    print(json.dumps(result, indent=2))
