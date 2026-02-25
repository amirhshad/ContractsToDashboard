# Contract Q&A - Ask Questions About Your Contract

## Goal
Allow users to ask questions about their contracts and receive AI-powered answers with citations from the extracted contract data.

## Inputs
- Contract ID
- User's question (natural language)
- Contract data from database (key_terms, parties, risks, costs, dates)

## Process
1. Fetch contract from database
2. Build context from contract fields
3. Send to LLM with the Q&A prompt
4. Return answer with citations

## API Endpoint
`POST /api/contracts/:id/query`

## Request Body
```json
{
  "question": "What is the cancellation policy?"
}
```

## Response
```json
{
  "answer": "You can cancel this contract with 30 days notice...",
  "citations": [
    "Cancellation notice: 30 days required",
    "Section 4.2: Termination terms"
  ]
}
```

## Q&A Prompt Template

```
You are a contract analyst assistant. Your job is to answer questions about contracts based on the extracted data.

## Contract Information

**Provider:** {provider_name}
**Type:** {contract_type}
**Monthly Cost:** {monthly_cost}
**Annual Cost:** {annual_cost}
**Payment Frequency:** {payment_frequency}
**Start Date:** {start_date}
**End Date:** {end_date}
**Auto-Renewal:** {auto_renewal}
**Cancellation Notice:** {cancellation_notice_days} days

**Key Terms:**
{key_terms}

**Parties:**
{parties}

**Risks:**
{risks}

## Question
{user_question}

## Instructions
1. Answer the question based ONLY on the contract data provided
2. If the question cannot be answered from the available data, say so clearly
3. Provide specific citations from the contract data when possible
4. Be concise but thorough
5. Use plain language, avoiding legal jargon where possible

## Response Format
Return a JSON object with:
- "answer": Your answer to the question
- "citations": Array of specific quotes/text that support your answer (empty if not applicable)
```
